import sys
import zmq
import numpy as np
import pickle
from matplotlib import animation
import matplotlib.pyplot as plt
from scipy import signal
from time import time
from basic_ofdm import ofdmSignalDemod 
#from mpl_toolkits.mplot3d import Axes3D

from scipy.io import savemat

saveFile = 0

def computeIQcorrection(I, Q):
    beta_I = np.mean(I)
    beta_Q = np.mean(Q)

    I2 = I - beta_I
    Q2 = Q - beta_Q

    Iamp = np.std(I2)
    Qamp = np.std(Q2)

    I2 = I2/Qamp
    Q2 = Q2/Qamp

    print('rms magnitude: ', Iamp, Qamp)
    print('rms magnitude after norm: ', np.std(I2), np.std(Q2))

    alfa = np.sqrt(2*np.inner(I2, I2)/I.shape[0])
    s_phi = (2/alfa)*np.inner(I2, Q2)/I.shape[0]
    c_phi = np.sqrt(1-(s_phi*s_phi))


    print('alfa : ', alfa)
    print('s_phi: ', s_phi)
    print('c_phi: ', c_phi)

    A = 1/alfa
    C = -s_phi/(alfa*c_phi)
    D = 1/c_phi

    Icorr = A*I2*Qamp
    Qcorr = (C*I2 + D*Q2)*Qamp
    return Icorr, Qcorr, (A, C, D, alfa, s_phi, c_phi)

def computeIQcorrection2(I, Q):
    I = I - np.mean(I)
    Q = Q - np.mean(Q)
    Iamp = np.std(I)
    Qamp = np.std(Q)
    print('rms magnitude after norm: ', np.std(I), np.std(Q))

    theta1 = np.mean(np.sign(I)*Q)
    theta2 = np.mean(np.sign(I)*I)
    theta3 = np.mean(np.sign(Q)*Q)
    C1 = theta1/theta2
    C2 = np.sqrt((theta3*theta3 - theta1*theta1)/ (theta2*theta2))
    Icorr = C2*I
    Qcorr = C1*I + Q

    g = theta3/ theta2
    phi = np.arcsin(theta1/ theta3)
    print(g, phi)

    return Icorr, Qcorr, (g, phi) 


class RadaraDataSubscriber:
    def __init__(self, topic='10001'):
        self.port = "5556"
        self.topic = topic
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        #self.socket.connect ("tcp://100.83.133.86:%s" % self.port)
        #self.socket.connect ("tcp://100.74.172.66:%s" % self.port)
        #self.socket.connect ("tcp://100.89.147.30:%s" % self.port)
        self.socket.connect ("tcp://100.66.96.2:%s" % self.port)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic) 
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(411)
        self.ax2 = self.fig.add_subplot(412)
        self.ax3 = self.fig.add_subplot(413)
        self.ax4 = self.fig.add_subplot(414)
        
        self.last_tstamp = 0
        self.loadTxSymbols()
        #self.make3Dviz()

    def make3Dviz(self):
        y = np.linspace(0,255, 256)
        x = np.linspace(0,127, 128)

        X, Y = np.meshgrid(x, y)
        self.meshX = X
        self.meshY = Y
        input('making 3Dviz, press any key...')


    def loadTxSymbols(self):
        with open('tx-code_ofdm3jan2.npy', 'rb') as f:
            sym = np.load(f)
            print('sym shape : ', sym.shape)
            self.sym = sym


    def VizData(self, sc):

        print(sc)

        def read_newdata(sc):
            [topic, sn, fs, freq, sent_time, I, Q] = self.socket.recv_multipart()
            print(topic, sent_time.decode('utf-8'), sn.decode('utf-8'))
            Idata = pickle.loads(I)
            Qdata = pickle.loads(Q)
            fs = int(fs.decode('utf-8'))
            freq = int(freq.decode('utf-8'))

            print('Tone frequency={}, Sampling frequency={}'.format(freq, fs))


            Icorr, Qcorr, coeffs = computeIQcorrection2(Idata, Qdata)

            Ispectrum = np.fft.fft(Icorr, n=256, axis = 0)
            Qspectrum = np.fft.fft(Qcorr, n=256, axis = 0)
            IQspectrum = np.fft.fft(Icorr+ 1j*Qcorr, n=256, axis = 0)

            Iorig = np.fft.fft(Idata , n=256, axis = 0)
            Qorig = np.fft.fft(Qdata , n=256, axis = 0)
            IQorig = np.fft.fft(Idata + 1j*Qdata, n=256, axis = 0)
            return Ispectrum, Qspectrum, IQspectrum, Iorig, Qorig, IQorig


        Ispec, Qspec, IQspec, Iorig, Qorig, IQorig = read_newdata(sc)

        self.ax1.plot(np.abs(Ispec))
        self.ax1.plot(np.abs(Iorig))
        self.ax2.plot(np.abs(Qspec))
        self.ax2.plot(np.abs(Qorig))
        self.ax3.plot(np.abs(IQspec))
        self.ax3.plot(np.abs(IQorig))
        self.ax4.plot(np.unwrap(np.angle(IQspec)))
        self.ax4.plot(np.unwrap(np.angle(IQorig)))
        plt.show()

        





if __name__ == "__main__":
    print(sys.argv[1])
    S = RadaraDataSubscriber()
    S.VizData(int(sys.argv[1]))


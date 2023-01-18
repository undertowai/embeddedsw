import sys
import zmq
import numpy as np
import pickle
from matplotlib import animation
import matplotlib.pyplot as plt
from scipy import signal
import numpy.matlib

from time import time
from basic_ofdm import ofdmSignalDemod 
#from mpl_toolkits.mplot3d import Axes3D

from scipy.io import savemat

from measure_iq import computeIQcorrection
from measure_iq import computeIQcorrection2

saveFile = [[0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]]


class RadaraDataSubscriber:
    def __init__(self, topic='10001'):

        self.loadTxSymbols()
        self.makeFFTwin()


        self.port = "5556"
        self.topic = topic
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect ("tcp://100.83.133.86:%s" % self.port)
        #self.socket.connect ("tcp://100.74.172.66:%s" % self.port)
        #self.socket.connect ("tcp://100.89.147.30:%s" % self.port)
        #self.socket.connect ("tcp://100.66.96.2:%s" % self.port)
        #self.socket.connect ("tcp://127.0.0.1:%s" % self.port)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic) 
        self.fig = plt.figure()
        #self.ax = self.fig.add_subplot(111, projection='3d')

        #self.ax1 = self.fig.add_subplot(111)

        #self.ax1 = self.fig.add_subplot(311)
        #self.ax2 = self.fig.add_subplot(312)
        #self.ax3 = self.fig.add_subplot(313)
        
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        
        self.last_tstamp = 0
        #self.make3Dviz()

    def make3Dviz(self):
        y = np.linspace(0,255, 256)
        x = np.linspace(0,127, 128)

        X, Y = np.meshgrid(x, y)
        self.meshX = X
        self.meshY = Y
        input('making 3Dviz, press any key...')

    def makeFFTwin(self):
        range_win = signal.windows.hann(self.sym.shape[0])
        print('range_win shape: ', range_win.shape)
        range_win_cube = np.matlib.repmat(range_win[:,np.newaxis], 1, self.sym.shape[1])
        print('range_win_cube shape: ', range_win_cube.shape)
        self.range_win_cube = np.reshape(range_win_cube, self.sym.shape)
        print('range_win_cube shape: ', range_win_cube.shape)
        #plt.plot(self.range_win_cube[:,0:4])
        #plt.show()

        dopp_win = signal.windows.hann(self.sym.shape[1])
        print('dopp_win shape: ', dopp_win.shape)
        dopp_win_cube = np.matlib.repmat(dopp_win[:,np.newaxis], 1, self.sym.shape[0])
        print('dopp_win_cube shape: ', dopp_win_cube.shape)
        #plt.plot(dopp_win_cube[:,0])
        #plt.show()
        self.dopp_win_cube = dopp_win_cube.transpose()
        #plt.plot(self.dopp_win_cube[0,:])
        #plt.show()


    def loadTxSymbols(self):
        with open('tx-code_ofdm_18jan.npy', 'rb') as f:
            sym = np.load(f)
            print('sym shape : ', sym.shape)
            self.sym = sym

    def plotTimeDomain(self, Idata, Qdata):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.plot(Idata[256:512])
        self.ax2.plot(Qdata[256:512])
        self.ax3.plot(np.arctan(Qdata[256:512]/Idata[256:512]))

    def plotSpectrum(self, Idata, Qdata,fs):
        self.ax1.clear()
        #self.ax2.clear()
        #self.ax3.clear()
        self.ax1.set_title('{:.2f} fps'.format(self.fps))

        fI, Pxx_denI = signal.welch(Idata[65536:2*65536], fs, nperseg=256)
        fQ, Pxx_denQ = signal.welch(Qdata[65536:2*65536], fs, nperseg=256)

        #Icorr, Qcorr, coeff = computeIQcorrection2(Idata, Qdata)
        #fIc, Pxx_denIc = signal.welch(Icorr[65536:2*65536], fs, nperseg=256)
        #fQc, Pxx_denQc = signal.welch(Qcorr[65536:2*65536], fs, nperseg=256)

        self.ax1.semilogy(fI, Pxx_denI, label='I')
        self.ax1.semilogy(fQ, Pxx_denQ, label='Q')

        #self.ax2.semilogy(fQ, Pxx_denQ, label='Q')
        #self.ax2.semilogy(fQc, Pxx_denQc, label='Qc')

        #self.ax2.set_xlabel('Freq [100MHz]')
        #self.ax2.set_ylabel('dBFS ?')

        #fIQ, Pxx_denIQ = signal.welch(Idata[65536:2*65536] + 1j*Qdata[65536:2*65536], fs, nperseg=256)
        #fIQc, Pxx_denIQc = signal.welch(Icorr[65536:2*65536] + 1j*Qcorr[65536:2*65536], fs, nperseg=256)
        #self.ax3.semilogy(fIQc, Pxx_denIQc, label='IQc')
        #self.ax3.semilogy(fIQ, Pxx_denIQ, label='IQ')


    def demodOFDM(self,ax,  Idata, Qdata, tx, rx, hw_delay = 57): #(256-200)):
        ax.clear()
        global saveFile

        sBegin = 1*128*512-hw_delay
        sEnd   = 2*128*512-hw_delay
        Idata = Idata[sBegin:sEnd] - np.mean(Idata[sBegin:sEnd])
        Qdata = Qdata[sBegin:sEnd] - np.mean(Qdata[sBegin:sEnd])
        #demod_data = Qdata[1*128*512-hw_delay:2*128*512-hw_delay] + 1j*Idata[1*128*512-hw_delay:2*128*512-hw_delay]
        demod_data = Qdata + 1j*Idata
        #demod_data = demod_data.transpose()
        demod_data = demod_data

        '''
        if(saveFile[tx][rx] < 20):
            mat_dict= {'Icap': Qdata.transpose(), 'Icap': Qdata.transpose(), 'IQ_data': demod_data}
            filename = 'raw_capture'+'_'+str(tx)+'_'+str(rx)+'_'+str(saveFile[tx][rx])+'.mat'
            print('saving ... ', filename, '@num : ', saveFile[tx][rx], ', ',tx, rx)
            savemat(filename, mat_dict)
            saveFile[tx][rx] = saveFile[tx][rx]+1
            print(saveFile)
        '''
            
        #print('min max rx: ', np.min(Idata), np.max(Idata))
        print('demod_data_array shape: ', demod_data.shape)
        demod_data = demod_data[0:128*512]
        print('demod_data shape: ', demod_data.shape)
        signal = np.reshape(demod_data[np.newaxis,:], (128,512)).transpose()
        #print('signal shape: ', signal.shape)
        signal_cp = signal[255:, :]
        #print('signal_cp shape: ', signal_cp.shape)
        rx_sym = np.fft.fft(signal_cp, n=256, axis = 0)
        sym_conj = self.sym.conj()
        phase_signal = rx_sym*sym_conj




        range_doppler = np.fft.fftshift(np.fft.fft2(phase_signal.conj()), axes =1)
        #range_doppler = np.fft.fftshift(np.fft.fft2(phase_signal), axes =1)
        #range_doppler = np.fft.fft(phase_signal, axis =0)

        '''
        print('Range fft on axis 0 of phase_signal shape: ', phase_signal.shape, 'and cube axis : ', self.range_win_cube.shape)
        range_slow = phase_signal#*self.range_win_cube
        range_doppler = np.fft.ifft(range_slow, axis = 0)

        #range_doppler = range_slow*self.dopp_win_cube
        #range_doppler = np.fft.fftshift(np.fft.fft(range_slow, axis = 1), axes = 1)
        '''



        return range_doppler





    def VizData(self):

        def read_newdata(i):
            #[topic, sn, fs, freq, sent_time, I0, Q0, I1, Q1, I2, Q2, I3, Q3] = self.socket.recv_multipart()
            #[topic, sn, fs, freq, sent_time, I, Q] = self.socket.recv_multipart()

            [topic, sn, txn, rx_list, fs, freq, sent_time, iq_data] = self.socket.recv_multipart()
            print(topic, sent_time.decode('utf-8'), sn.decode('utf-8'))
            iq_data = pickle.loads(iq_data)
            txnumber = int(txn.decode('utf-8'))
            fs = int(fs.decode('utf-8'))
            freq = int(freq.decode('utf-8'))

            print('Tone frequency={}, Sampling frequency={}'.format(freq, fs))

            #print('length of iq_data: ', len(iq_data))

            #print('shape of iq_data[0]: ', iq_data[0][0].shape)
            #print('shape of iq_data[1]: ', iq_data[1][0].shape)
            #print('shape of iq_data[2]: ', iq_data[2][0].shape)
            #print('shape of iq_data[3]: ', iq_data[3][0].shape)

            tstamp = time()
            
            self.fps = 1 / (tstamp - self.last_tstamp)
            self.last_tstamp = tstamp

            Idata0, Qdata0 = iq_data[0]
            Idata1, Qdata1 = iq_data[1]
            Idata2, Qdata2 = iq_data[2]
            Idata3, Qdata3 = iq_data[3]
            print('Tx num: ', txnumber,  'Idata0 , Qdata0 : ', Idata0.shape, Qdata0.shape)


            '''
            range_doppler1 = self.demodOFDM(self.ax1, Idata0, Qdata0, txnumber, 0)#, hw_delay =193)
            range_doppler2 = self.demodOFDM(self.ax2, Idata1, Qdata1, txnumber, 1)#, hw_delay =193)
            range_doppler3 = self.demodOFDM(self.ax3, Idata2, Qdata2, txnumber, 2)#, hw_delay =193)
            range_doppler4 = self.demodOFDM(self.ax4, Idata3, Qdata3, txnumber, 3)#, hw_delay =193)
            '''

            
            sig0 = Idata0.astype(np.float32) + 1j*Qdata0.astype(np.float32)
            sig1 = Idata1.astype(np.float32) + 1j*Qdata1.astype(np.float32)
            sig2 = Idata2.astype(np.float32) + 1j*Qdata2.astype(np.float32)
            sig3 = Idata3.astype(np.float32) + 1j*Qdata3.astype(np.float32)
            hw_delay = 220
            sBegin = 1*128*512-hw_delay
            sEnd   = 2*128*512-hw_delay
            print('sig shapes: ', sig0.shape)
            range_doppler1, ph1 = ofdmSignalDemod(sig0[sBegin:sEnd], self.sym)#, hw_delay =193)
            range_doppler2, ph1 = ofdmSignalDemod(sig1[sBegin:sEnd], self.sym)#, hw_delay =193)
            range_doppler3, ph1 = ofdmSignalDemod(sig2[sBegin:sEnd], self.sym)#, hw_delay =193)
            range_doppler4, ph1 = ofdmSignalDemod(sig3[sBegin:sEnd], self.sym)

            range_doppler = np.abs(range_doppler1)+np.abs(range_doppler2)+np.abs(range_doppler3)+np.abs(range_doppler4)
            print('range_doppler shape: ', range_doppler.shape)
            #range_doppler = np.abs(range_doppler1)#+np.abs(range_doppler2)+np.abs(range_doppler3)+np.abs(range_doppler4)
            self.ax4.clear()
            self.ax4.imshow((np.abs(range_doppler[:32,64-8:64+8])))
            self.ax3.clear()
            self.ax3.imshow((np.abs(range_doppler)))
            range_doppler_zero_cut = (np.abs(np.squeeze(range_doppler[:32,64])))
            self.ax2.clear()
            self.ax2.plot(range_doppler_zero_cut)
            range_doppler_zero_cut[:2] = 0
            self.ax2.plot(range_doppler_zero_cut) #%np.concatenate(np.zeros((4,)), 10*np.squeeze(range_doppler[4:,64]) ))
            #self.ax2.set_ylim([175, 210])

            self.plotSpectrum(Idata0, Qdata0, fs)
            '''
            '''







        anim = animation.FuncAnimation(plt.gcf(), read_newdata, interval=10)
        plt.show()


if __name__ == "__main__":
    S = RadaraDataSubscriber()
    S.VizData()



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

class RadarDataSubscriber:
    def __init__(self,  delay=0, topic='10001'):

        self.loadTxSymbols()
        self.makeFFTwin()
        self.hw_delay = delay


        self.port = "5556"
        self.topic = topic
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

        self.socket.connect ("tcp://192.168.1.17:%s" % self.port)
        #self.socket.connect ("tcp://100.127.217.27:%s" % self.port)
        #self.socket.connect ("tcp://100.83.133.86:%s" % self.port)
        #self.socket.connect ("tcp://100.74.172.66:%s" % self.port)
        #self.socket.connect ("tcp://100.89.147.30:%s" % self.port)
        #self.socket.connect ("tcp://100.66.96.2:%s" % self.port)
        #self.socket.connect ("tcp://127.0.0.1:%s" % self.port)
        self.socket.setsockopt_string(zmq.SUBSCRIBE, self.topic) 
        self.fig = plt.figure()
        #self.ax = self.fig.add_subplot(111, projection='3d')
        #self.make3Dviz()



        self.ax=[]
        for r in range(16):
            self.ax.append(self.fig.add_subplot(4,4,r+1))

        
        self.last_tstamp = 0

        self.all_phase=[]


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
        with open('tx-code_ofdm_12jan.npy', 'rb') as f:
            sym = np.load(f)
            print('sym shape : ', sym.shape)
            self.sym = sym

    def plotTimeDomainDiff(self, ax, Iref, Qref, Idata, Qdata):
        A = np.angle(Idata[256:512] + 1j*Qdata[256:512])
        Aref = np.angle(Iref[256:512] + 1j*Qref[256:512])
        ax.plot(np.unwrap(A)-np.unwrap(Aref))

    def plotTimeDomain(self, ax, Idata, Qdata):
        ax.clear()
        A = np.angle(Idata[256:512] + 1j*Qdata[256:512])
        ax.plot((A))

        #ax.plot(Idata[256:512])
        #ax.plot(Qdata[256:512])


    def plotSpectrum(self, ax, ax2, bin_track, Idata, Qdata,fs):
        ax.clear()
        #self.ax2.clear()
        #self.ax3.clear()
        ax.set_title('{:.2f} fps'.format(self.fps))

        #fI, Pxx_denI = signal.welch(Idata[65536:2*65536], fs, nperseg=256)
        #fQ, Pxx_denQ = signal.welch(Qdata[65536:2*65536], fs, nperseg=256)

        #Icorr, Qcorr, coeff = computeIQcorrection2(Idata, Qdata)
        #fIc, Pxx_denIc = signal.welch(Icorr[65536:2*65536], fs, nperseg=256)
        #fQc, Pxx_denQc = signal.welch(Qcorr[65536:2*65536], fs, nperseg=256)

        Idata = Idata[65536:2*65536]
        Idata = Idata - np.mean(Idata)
        Qdata = Qdata[65536:2*65536]
        Qdata = Qdata - np.mean(Qdata)
        #print('incoming data shape: ', Idata.shape)
        #print('incoming data shape: ', Qdata.shape)

        Idata_fold = np.reshape(Idata, (256, 256))
        #Idata_fold = np.mean(Idata_fold, axis = 0)
        Qdata_fold = np.reshape(Qdata, (256, 256))
        #Qdata_fold = np.mean(Qdata_fold, axis = 0)

        fftIQ = np.fft.fft(Idata_fold + 1j*Qdata_fold, axis = 1)
        #fftQ = np.fft.fft(Qdata_fold, axis = 1)
        phase_trk = np.angle(fftIQ[256-bin_track])
        #fftI = np.fft.fft(Idata[65536:2*65536])
        #fftQ = np.fft.fft(Qdata[65536:2*65536])
        mean_fftIQ = np.mean(fftIQ, axis = 0)
        ax.plot(10*np.log10(np.abs(mean_fftIQ)), label='I', marker='o')
        #ax.plot(10*np.log10(np.abs(fftQ)), label='Q', marker='*')
        ax.set_yticks(numpy.arange(0, 100, 10))
        ax.grid()

        ax2.clear()
        ax2.plot(phase_trk)


        
        #self.ax2.semilogy(fQ, Pxx_denQ, label='Q')
        #self.ax2.semilogy(fQc, Pxx_denQc, label='Qc')

        #self.ax2.set_xlabel('Freq [100MHz]')
        #self.ax2.set_ylabel('dBFS ?')

        #fIQ, Pxx_denIQ = signal.welch(Idata[65536:2*65536] + 1j*Qdata[65536:2*65536], fs, nperseg=256)
        #fIQc, Pxx_denIQc = signal.welch(Icorr[65536:2*65536] + 1j*Qcorr[65536:2*65536], fs, nperseg=256)
        #self.ax3.semilogy(fIQc, Pxx_denIQc, label='IQc')
        #self.ax3.semilogy(fIQ, Pxx_denIQ, label='IQ')


    def demodOFDM(self,Idata, Qdata, tx, rx, track_carrier_phase): #(256-200)):
        global saveFile


        #Idata = Idata/np.std(Idata)
        #Qdata = Qdata/np.std(Qdata)


        #demod_data = Qdata[1*128*512-hw_delay:2*128*512-hw_delay] + 1j*Idata[1*128*512-hw_delay:2*128*512-hw_delay]
        demod_data = Qdata + 1j*Idata
        demod_data = demod_data.transpose()

        '''
        if(saveFile[tx][rx] < 1000):
            mat_dict= {'Icap': Qdata.transpose(), 'Icap': Qdata.transpose(), 'IQ_data': demod_data}
            filename = 'raw_capture'+'_'+str(tx)+'_'+str(rx)+'_'+str(saveFile[tx][rx])+'.mat'
            print('saving ... ', filename, '@num : ', saveFile[tx][rx], ', ',tx, rx)
            savemat(filename, mat_dict)
            saveFile[tx][rx] = saveFile[tx][rx]+1
            print(saveFile)
        '''
            
        #print('min max rx: ', np.min(Idata), np.max(Idata))
        demod_data = demod_data[0:128*512]
        signal = np.reshape(demod_data[np.newaxis,:], (128,512)).transpose()
        #print('signal shape: ', signal.shape)
        signal_cp = signal[255:, :]
        #print('signal_cp shape: ', signal_cp.shape)
        rx_sym = np.fft.fft(signal_cp, n=256, axis = 0)
        sym_conj = self.sym.conj()
        phase_signal = rx_sym*sym_conj


        #phase_signal_track = rx_sym[track_carrier_phase-1:track_carrier_phase+2, :]




        range_doppler = np.fft.fftshift(np.fft.fft2(phase_signal.conj()), axes =1)
        #range_doppler = np.fft.fftshift(np.fft.fft2(phase_signal), axes =1)
        #range_doppler = np.fft.fft(phase_signal, axis =0)




        return range_doppler, rx_sym #phase_signal_track



    def calculateRDtrack(self, iq_data, txnumber, rx_number, sc=32):
        '''
        Idata0, Qdata0 = iq_data[0]
        Idata1, Qdata1 = iq_data[1]
        Idata2, Qdata2 = iq_data[2]
        Idata3, Qdata3 = iq_data[3]

        Idata4, Qdata4 = iq_data[4]
        Idata5, Qdata5 = iq_data[5]
        Idata6, Qdata6 = iq_data[6]
        Idata7, Qdata7 = iq_data[7]

        print('Tx num: ', txnumber,  'Idata0 , Qdata0 : ', Idata0.shape, Qdata0.shape)
        '''
        trk_carrier = []

        beta = []
        theta = []

        for rr in rx_number:
            #print('calculating demodOFDM for rr = ', rr, beta)
            hw_delay = self.hw_delay
            sBegin = 1*128*512-hw_delay
            sEnd   = 2*128*512-hw_delay
            Idata = iq_data[rr][1]
            Qdata = iq_data[rr][0]
            Idata = Idata[sBegin:sEnd] - np.mean(Idata[sBegin:sEnd])
            Qdata = Qdata[sBegin:sEnd] - np.mean(Qdata[sBegin:sEnd])
            range_doppler, trk_carrier_this = self.demodOFDM(Idata, Qdata, txnumber, rr, track_carrier_phase=sc)
            trk_carrier.append(trk_carrier_this)
            self.ax[rr].plot((np.angle(trk_carrier_this[256-sc]))) #.transpose())))
            self.ax[rr].plot((np.angle(trk_carrier_this[sc]))) #.transpose())))
            self.ax[rr].set_ylim(-np.pi, np.pi)
            self.ax[rr].grid()

            mean_trk_this = (np.mean(trk_carrier_this, axis=1))
            kappa = mean_trk_this[256-sc]/mean_trk_this[sc]
            zeta = (1+kappa)/(1-kappa)
            #print('kappa for rx: ', rr, 'is: ', kappa, zeta)
            theta_this = np.arctan(zeta.real)
            beta_this  = -1/(zeta.imag*np.cos(theta_this))

            beta.append(beta_this)
            theta.append(theta_this)
            self.ax[rr+8].plot(10*np.log10(np.abs(np.mean(trk_carrier_this,axis=1)))) #.transpose())))
            self.ax[rr+8].set_yticks(numpy.arange(0, 60, 5))
            self.ax[rr+8].grid()

            '''
            theta_corr = np.arcsin(Idata) - theta_this
            Idata = (np.abs(Idata)/beta_this)*np.sin(theta_corr)
            #Icorr, Qcorr, coeff = computeIQcorrection(Qdata, Idata)

            range_doppler2, trk_carrier_this2 = self.demodOFDM(Idata, Qdata, txnumber, rr, track_carrier_phase = sc)
            self.ax[rr+8].plot((np.abs(np.mean(trk_carrier_this2,axis=1)))) #.transpose())))
            #self.ax[rr+8].plot(Icorr[256:256+96], marker='*')
            #self.ax[rr+8].plot(Qcorr[256:256+96])
            '''

        for r in range(len(iq_data)):
            if(len(self.all_phase) < r+1):
                self.all_phase.append([])
            self.all_phase[r].append(np.angle(trk_carrier[r][256-sc]))
        #print('IQ gain imbalance: ', beta)

        return beta, theta


    def VizData(self):


        def read_newdata(i):
            #[topic, sn, fs, freq, sent_time, I0, Q0, I1, Q1, I2, Q2, I3, Q3] = self.socket.recv_multipart()
            #[topic, sn, fs, freq, sent_time, I, Q] = self.socket.recv_multipart()

            [topic, sn, txn, rxnumbers, fs, freq, sent_time, iq_data] = self.socket.recv_multipart()
            print(topic, sent_time.decode('utf-8'), sn.decode('utf-8'))
            iq_data = pickle.loads(iq_data)
            sn = int(sn.decode('utf-8'))
            txnumber = int(txn.decode('utf-8'))
            fs = int(fs.decode('utf-8'))
            freq = int(freq.decode('utf-8'))

            print('Tone frequency={}, Sampling frequency={}'.format(freq, fs))


            tstamp = time()
            
            self.fps = 1 / (tstamp - self.last_tstamp)
            self.last_tstamp = tstamp



            for r in range(16):
                self.ax[r].clear()

            '''
            beta, theta = self.calculateRDtrack(iq_data, txnumber,range(len(iq_data)), sc = 4)
            print('beta estimates ... ', beta, theta)
            '''

            for rr in rxnumbers:
                self.plotSpectrum(self.ax[rr+8], self.ax[rr] , 4, iq_data[rr][0], iq_data[rr][1],fs)



        anim = animation.FuncAnimation(plt.gcf(), read_newdata, interval=1)
        plt.show()


if __name__ == "__main__":
    delay = int(sys.argv[1])
    print('initializing with hw_delay: ', delay)
    S = RadarDataSubscriber(delay=delay)
    S.VizData()

    fig2 = plt.figure()
    ax9 = fig2.add_subplot(111)
    for r in range(len(S.all_phase)):
        all_phase_this = np.asarray(S.all_phase[r]).flatten()
        ax9.plot(all_phase_this)
    plt.show()


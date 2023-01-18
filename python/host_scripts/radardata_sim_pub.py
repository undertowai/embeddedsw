import numpy as np
import matplotlib.pyplot as plt
import json
import argparse
import zmq
import pickle
import time

class RadarDataPublisher:
    def __init__(self, Ifile, Qfile, topic='10001'):
        self.port = "5556"
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind("tcp://0.0.0.0:%s" % self.port)
        self.topic = topic
        self.I, self.Q = self.LoadDataFromFile(Ifile, Qfile)


    def LoadDataFromFile(self, Ifile, Qfile):
        with open(Ifile, 'rb') as f:
            I = np.load(f, allow_pickle=True)
            print('reading I, shape: ', I.shape)
            print('min max: ', np.min(I), np.max(I))
        with open(Qfile, 'rb') as f:
            Q = np.load(f, allow_pickle=True)
            print('reading Q, shape: ', Q.shape)
            print('min max: ', np.min(Q), np.max(Q))

        '''
        with open(Cfile, 'rb') as f:
            sym = np.load(f)
            plt.plot(sym[:,0])
            plt.show()
            print('sym shape : ', sym.shape)
        '''


        return I,Q

    def PublishData(self, index, tx, rx, dwell):
        this_time = time.time_ns()
        print('this_time: ', this_time)
        print('adcData shape: ', self.I.shape, self.I.dtype)
        print('adcData shape: ', self.Q.shape, self.Q.dtype)
        tx_adc_I = []
        tx_adc_Q = []
        for d in range(dwell):
            print('adding dwell: ', d)
            tx_adc_I.append(self.I)
            tx_adc_Q.append(self.Q)

        tx_send_I = np.asarray(tx_adc_I)
        tx_send_Q = np.asarray(tx_adc_Q)

        print('size tx_send_I,Q 00: ', tx_send_I.shape, tx_send_Q.shape)
        tx_send_I = np.reshape(tx_send_I, (dwell*tx_adc_I[0].shape[0], ) )
        tx_send_Q = np.reshape(tx_send_Q, (dwell*tx_adc_I[0].shape[0], ) )
        print('size tx_send_I,Q 11: ', tx_send_I.shape, tx_send_Q.shape)
        '''
        plt.plot(tx_send_I[0:128])
        plt.plot(tx_send_I[65536:65536+128])
        plt.title('verifying dwell time repeat/ reshape')
        plt.show()
        '''

        for tt in tx:
            print('Tx array in time multiplex: ', tx)
            print('Rx array active: ', rx)
            rx_adc_IQ = []
            for rr in rx:
                rx_adc_IQ.append([tx_send_I, tx_send_Q])

            print('rx chunk len, size: ', len(rx_adc_IQ), rx_adc_IQ[0][0].shape, rx_adc_IQ[0][1].shape)
            self.socket.send_multipart([bytes(self.topic, 'utf-8'), \
                bytes(str(index), 'utf-8'), \
                bytes(str(tt),'utf-8'), \
                bytes(pickle.dumps(rx)), \
                bytes(str(480), 'utf-8'), \
                bytes(str('0'), 'utf-8'), \
                bytes(str(this_time), 'utf-8'), \
                pickle.dumps(rx_adc_IQ)])
            print('sent out a chunk of data ... ')



def main(Ifile, Qfile, tx_num, rx_num, dwell):

    pub = RadarDataPublisher(Ifile, Qfile)
    index = 0
    while True:
        pub.PublishData(index, tx_num, rx_num, dwell)
        time.sleep(1)
        index = index+1


    return




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ifile", type=str, default='./Ichannel_ofdm_18jan.npy')
    parser.add_argument("--qfile", type=str, default='./Qchannel_ofdm_18jan.npy')
    #parser.add_argument("--cfile", type=str, default='./tx-code_ofdm_18jan.npy')
    parser.add_argument('--tx', action='store', dest='txlist',type=int, nargs='*', default=[4], help="Examples: -tx 4 5 6 7")
    parser.add_argument('--rx', action='store', dest='rxlist',type=int, nargs='*', default=[0,1,2,3], help="Examples: --rx 0 1 2 3 4 5 6 7")
    parser.add_argument("--dwell", type=int, default=2)
    args = parser.parse_args()

    print(args.txlist)
    print(args.rxlist)

    print(args)

    main(args.ifile, args.qfile, args.txlist, args.rxlist, args.dwell)


import numpy as np
import numpy.matlib
import scipy.io
import matplotlib.pyplot as plt
from scipy.signal import welch
from basic_ofdm import ofdmSignalDemod

def prepOFDMSymbol(Nsc=256, Nsym=128, buffer_size= 65536, viz = True, tonedbg = False, carrier=120):
    mat = scipy.io.loadmat('./DATA_SEQUENCES_256.mat')
    codes = mat['d_f_256']
    print(codes.shape)
    sym = np.zeros((Nsc, Nsym), dtype = np.float64)
    sym = codes[:,0:Nsym]
    print('code symbols shape: ', sym.shape)

    #dbg feature, if required generate a single tone
    if(tonedbg):
        re = np.zeros(sym.shape)
        im = np.zeros(sym.shape)
        symbol = np.exp(1j*np.pi/4)
        re[carrier,:] = symbol.real
        im[carrier,:] = symbol.imag
        #re[carrier+8,:] = symbol.real
        #im[carrier+8,:] = symbol.imag
        sym = re + 1j*im

        

    # checking if PRI can be done in the given buffer
    pri = buffer_size/(2*Nsc*Nsym)
    print('pri possibility: ', pri)


    # doing iFFT
    out_sym = np.fft.ifft(sym, n=Nsc, axis = 0)
    print('outsym shape: ', out_sym.shape)
    #plt.plot(np.fft.fft(out_sym[:,0])) # attempt seeing the spectrum of the time domain signal
    #plt.plot(sym[:,0])
    #plt.show()

    if(viz == True):
        plt.plot(out_sym[:,0].real)
        plt.show()

    # adding CP
    out_sym_cp = np.concatenate((out_sym, out_sym), axis =0)
    print('outsym_cp shape: ', out_sym_cp.shape)
    #plt.plot(np.fft.fft(out_sym_cp[:,0])) # attempt seeing the spectrum of CP signal
    #plt.show()
    if(viz == True):
        plt.plot(out_sym_cp[:,0].real)
        plt.show()

    #dbg print, ignore
    #print('papr for each pulse: ', np.max(np.abs(out_sym), axis = 0)/ np.mean(np.abs(out_sym), axis = 0))
    #print('real min, max : ', (np.max(out_sym_cp.real, axis = 0), np.min(out_sym_cp.real, axis = 0)))
    #print('imag min, max : ', (np.max(out_sym_cp.imag, axis = 0), np.min(out_sym_cp.imag, axis = 0)))

    #scaling to full DAC 
    out_sym_cp = np.power(2,18)*out_sym_cp
    file_tx = np.reshape(out_sym_cp.transpose(), (buffer_size,))
    print('verifying npy reshaping: ')
    if(viz == True):
        plt.plot(file_tx[0:512].real)
        plt.plot(out_sym_cp[0:512,0].real)
        plt.show()


    f, pxx = welch(file_tx, 600e6, nperseg = 512, nfft = 512, noverlap = 256, return_onesided=True)
    if(viz == True):
        plt.semilogy(f, pxx)
        plt.show()


    I = file_tx.real.astype(np.int16)
    Q = file_tx.imag.astype(np.int16)

    if(viz == True):
        plt.plot(I[0:512])
        plt.show()



    print('I shape: ', I.shape)
    I = I.reshape((buffer_size,))
    print('I shape: ', I.shape)

    print('Q shape: ', Q.shape)
    Q = Q.reshape((buffer_size,))
    print('Q shape: ', Q.shape)

    if(tonedbg == True):
        carrier_name = str(carrier)
    else:
        carrier_name = carrier

    with open('tx-code_'+carrier_name+'.npy', 'wb') as f:
        np.save(f, sym)
    with open('Ichannel_'+carrier_name+'.npy', 'wb') as f:
        np.save(f, I)

    with open('Qchannel_'+carrier_name+'.npy', 'wb') as f:
        np.save(f, Q)

    return file_tx


def decodeOFDMFromFile(Ifile='Ichannel.npy', Qfile='Qchannel.npy', Cfile ='tx-code.npy', simDelay=0):
    with open(Ifile, 'rb') as f:
        I = np.load(f, allow_pickle=True)
        print('reading I, shape: ', I.shape)
        print('min max: ', np.min(I), np.max(I))
    with open(Qfile, 'rb') as f:
        Q = np.load(f, allow_pickle=True)
        print('reading Q, shape: ', Q.shape)
        print('min max: ', np.min(Q), np.max(Q))

    with open(Cfile, 'rb') as f:
        sym = np.load(f)
        plt.plot(sym[:,0])
        plt.show()
        print('sym shape : ', sym.shape)

    zeroPad = np.zeros((simDelay,), dtype = np.complex128)
    I = I.astype(np.float32)
    Q = Q.astype(np.float32)
    tx = I + 1j*Q

    print('Decoding from file, displaying timedomain signal')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(tx[0:512].real)
    ax.set_title('timedomain signal: 1 OFDM symbol + CP')
    plt.show()

    rx = np.concatenate((zeroPad, tx), axis =0)
    signal = rx[0:tx.shape[0]]
    range_doppler, phase_signal =ofdmSignalDemod(signal, sym)

    plt.imshow(np.abs(range_doppler))
    #plt.imshow(np.fft.fftshift((np.abs(np.fft.fft2(phase_signal.conj()))), axes =1))
    plt.show()

    '''
    y = np.linspace(0,255, 256)
    x = np.linspace(0,127, 128)
    meshX, meshY = np.meshgrid(x, y)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(meshX, meshY, (np.abs(range_doppler)))
    plt.show()
    '''


    plt.plot(10*np.log(np.abs(range_doppler[:,63])))
    plt.plot(10*np.log(np.abs(range_doppler[:,64])))
    plt.plot(10*np.log(np.abs(range_doppler[:,65])))
    plt.show()

    plt.plot(phase_signal[:,0].real)
    plt.show()

'''
def ofdmSignalDemod(signal, sym):
    signal = signal - np.mean(signal)
    signal = np.reshape(signal, (128,512)).transpose()

    signal_cp = signal[256:, :]
    print('signal_cp shape: ', signal_cp.shape, signal_cp.dtype)

    rx_sym = np.fft.fft(signal_cp, n=256, axis = 0)
    phase_signal = rx_sym*sym.conj()


    range_doppler = np.fft.fftshift(np.fft.fft2(phase_signal.conj()), axes =1)

    return range_doppler, phase_signal
'''

if __name__ == '__main__':
    carrier = 'ofdm_18jan'
    
    Ifile = 'Ichannel_'+str(carrier)+'.npy'
    Qfile = 'Qchannel_'+str(carrier)+'.npy'
    Cfile = 'tx-code_'+str(carrier)+'.npy'

    prepOFDMSymbol(carrier=carrier)
    decodeOFDMFromFile(Ifile=Ifile, Qfile=Qfile, Cfile= Cfile, simDelay=110) #, carrier= carrier)

    '''
    # uncomment following for generating single tone
    Ifile = 'Ichannel_'+str(carrier)+'.npy'
    Qfile = 'Qchannel_'+str(carrier)+'.npy'
    Cfile = 'test-code_'+str(carrier)+'.npy'
    #prepOFDMSymbol(tonedbg = True, carrier=carrier)
    with open(Ifile, 'rb') as f:
        I = np.load(f)
        print('reading I, shape: ', I.shape)
        I = I.astype(np.float32)
        print(I.shape)
        print(I[0:8], I[128:136])
        print(I[8:16], I[136:144])
        print(np.max(I[0:65536]))
        plt.plot(I)
        plt.show()

    with open(Qfile, 'rb') as f:
        Q = np.load(f)
        print('reading Q, shape: ', I.shape)
        Q = Q.astype(np.float32)
        print(Q[0:8], Q[128:136])
        print(Q[8:16], Q[136:144])
        print(Q.shape)


    file_tx = I + 1j*Q
    file_tx = np.reshape(file_tx, (128, 512)).transpose()
    plt.plot(np.fft.fft(file_tx[:,0]))
    plt.show()

    '''



import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.io import loadmat
import scipy.io
from mpl_toolkits.mplot3d import Axes3D

def test_ofdm_spectrum(Nsc, Nsym=128):
    #for ii in [0,1, 127,128, 254,255]:
    for ii in [32, 16]:
        I = np.zeros((Nsc, Nsym), dtype=np.float64)
        Q = np.zeros((Nsc,Nsym), dtype=np.float64)
        sym = np.exp(1j*np.pi/4)
        I[ii,:] = sym.real
        Q[ii,:] = sym.imag
        S = np.fft.ifft(I+ 1j*Q, axis = 0)
        plt.plot(S[:,0].real)
        plt.plot(S[:,0].imag)
        plt.show()
        plt.plot(np.fft.fft(S[:,0]))
        plt.show()

        S_cp = np.concatenate((S, S), axis = 0)
        tx = np.reshape(S_cp.transpose(), (2*Nsc*Nsym,))

        f, pxx = welch(tx.real, 600e6, nperseg=512, nfft=512, noverlap=256)
        plt.semilogy(f, pxx)
        plt.show()




def ofdmSignalDemod(signal, sym):
    signal = np.reshape(signal[np.newaxis,:], (128,512)).transpose()
    #signal = np.reshape(signal, (512,128))


    signal_cp = signal[256:, :]
    print('signal_cp shape: ', signal_cp.shape, signal_cp.dtype)

    rx_sym = np.fft.fft(signal_cp, n=256, axis = 0)
    phase_signal = rx_sym*sym.conj()


    range_doppler = np.fft.fftshift(np.fft.fft2(phase_signal.conj()), axes =1)

    return range_doppler, phase_signal


def test_ofdm_siso(Nsc, Nsym, simDelay = 0):
    mat = loadmat('./DATA_SEQUENCES_256.mat')
    codes = mat['d_f_256']
    sym = codes[:,0:128]
    out_sym = np.fft.ifft(sym, n = 256, axis = 0)
    out_sym_cp = np.concatenate((out_sym, out_sym), axis = 0)
    tx = np.reshape(out_sym_cp.transpose(), (2*256*128,))
    print(tx.shape)
    print(np.max(tx), np.min(tx))


    tx = np.power(2,18)*tx
    tx_I = tx.real.astype(dtype = np.int16)
    tx_Q = tx.imag.astype(dtype = np.int16)
    print(np.max(tx_I), np.min(tx_I))
    print(np.max(tx_Q), np.min(tx_Q))


    zeroPad = np.zeros((simDelay,), dtype = np.int16)

    rx_I = np.concatenate((zeroPad, tx_I), axis = 0)
    rx_Q = np.concatenate((zeroPad, tx_Q), axis = 0)
    rx = rx_I + 1j*rx_Q
    signal = rx[0:tx.shape[0]]
    range_doppler, phase_signal = ofdmSignalDemod(signal, sym)

    plt.plot(phase_signal[:,0].real)
    plt.show()

    plt.imshow(np.abs(range_doppler))
    plt.show()

    plt.plot(np.log(np.abs(range_doppler[:,64])))
    plt.show()


    y = np.linspace(0,255, 256)
    x = np.linspace(0,127, 128)
    meshX, meshY = np.meshgrid(x, y)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection = '3d')
    ax.plot_surface(meshX, meshY, np.log(np.abs(range_doppler)))
    plt.show()





if __name__ == '__main__':
    #test_ofdm_spectrum(Nsc =256)

    test_ofdm_siso(Nsc=256, Nsym=128)

    



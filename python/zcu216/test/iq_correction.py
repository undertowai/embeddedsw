import numpy as np

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


def computeIQcorrection2(I,Q):
    I = I - np.mean(I)
    Q = Q - np.mean(Q)
    Iamp = np.std(I)
    Qamp = np.std(Q)
    theta1 = np.mean(np.sign(I)*Q)
    theta2 = np.mean(np.sign(I)*I)
    theta3 = np.mean(np.sign(Q)*Q)
    C1 = theta1/theta2
    C2 = np.sqrt( (theta3*theta3 - theta1*theta1)/ (theta2*theta2) )
    Icorr = C2*I
    Qcorr = C1*I + Q
    g = theta3/theta2
    phi = np.arcsin(theta1/ theta3)
    print(g, phi)
    return Icorr, Qcorr, (g,phi)


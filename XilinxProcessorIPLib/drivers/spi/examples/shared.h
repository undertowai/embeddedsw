
int SpiSendData(const char *devName, unsigned int SS, unsigned int bytesInBurst, unsigned int *txBuf, unsigned int len);
int SpiRecvData(const char *devName, unsigned int SS, unsigned int bytesInBurst, unsigned int *rxBuf, unsigned int len, u32 readKey);
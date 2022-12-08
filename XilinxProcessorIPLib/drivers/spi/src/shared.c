

#include "xspi.h"
#include "xspi_l.h"

static int XSpi_WriteBuf (XSpi *Spi, u8 ic, u32 d, size_t len)
{
    int Status;
	u8 tx[3] = { (d >> 16) & 0xff, (d >> 8) & 0xff, d & 0xff };

	XSpi_SetSlaveSelect(Spi, 1<<ic);
	Status = XSpi_Transfer(Spi, tx, NULL, len);
	XSpi_SetSlaveSelect(Spi, 0);

	return Status;
}

static int XSpi_ReadBuf (XSpi *Spi, u8 ic, u32 *d, size_t len, u32 i, u32 readKey)
{
	u8 tx[3] = { i | readKey, 0, 0 };
	/* Write register */
    int Status;

    if (len != 3) {
        printf("XSpi_ReadBuf: len = %d Is not supported\r\n", len);
        return -XST_FAILURE;
    }

	XSpi_SetSlaveSelect(Spi, 1<<ic);
	Status = XSpi_Transfer(Spi, tx, tx, len);

	*d = (tx[0] << 16) + (tx[1] << 8) + tx[2];
	XSpi_SetSlaveSelect(Spi, 0);
	return Status;
}

static int _SpiInit(XSpi *Spi, const char *devName)
{
    int Status = XST_SUCCESS;
    u32 ControlReg;

    Status = _metal_init();
 	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}   

    Status = XSpi_Initialize(Spi, devName);
	if (Status != XST_SUCCESS) {
    	printf("XSpi_Initialize Failed\r\n");
		return -XST_FAILURE;
	}

    Status = XSpi_SelfTest(Spi);
	if (Status != XST_SUCCESS) {
        xil_printf("XSpi_SelfTest Failed: %d\r\n", Status);
		return -XST_FAILURE;
	}

    if (Spi->SpiMode != XSP_STANDARD_MODE) {
        xil_printf("SpiInstancePtr->SpiMode != XSP_STANDARD_MODE\r\n");
		return -XST_FAILURE;
	}

	ControlReg = XSpi_GetControlReg(Spi);

	ControlReg |= (XSP_CR_MASTER_MODE_MASK | XSP_CR_MANUAL_SS_MASK);
	XSpi_SetControlReg(Spi, ControlReg);

    XSpi_Start(Spi);
	XSpi_IntrGlobalDisable(Spi);

    return Status;
}

int SpiSendData(const char *devName, unsigned int SS, unsigned int bytesInBurst, unsigned int *txBuf, unsigned int len)
{
    XSpi Spi = {0};
    int Status;

    Status = _SpiInit(&Spi, devName);
    if (Status != XST_SUCCESS) {
        return Status;
    }

    for (unsigned int i = 0; i < len; i++) {
        u32 data;

        data = txBuf[0];
        Status = XSpi_WriteBuf(&Spi, SS, data, bytesInBurst);
        if (Status != XST_SUCCESS) {
            printf("XSpi_WriteBuf Failed\r\n");
            return -XST_FAILURE;
        }

        txBuf++;
    }
    metal_device_close(Spi.device);

    return XST_SUCCESS;
}

int SpiRecvData(const char *devName, unsigned int SS, unsigned int bytesInBurst, unsigned int *rxBuf, unsigned int len, u32 readKey)
{
    XSpi Spi = {0};
    int Status;

    Status = _SpiInit(&Spi, devName);
    if (Status != XST_SUCCESS) {
        return Status;
    }

    for (unsigned int i = 0; i < len; i++) {
        u32 data;;

        data = 0;
        Status = XSpi_ReadBuf(&Spi, SS, &data, bytesInBurst, i, readKey);
        if (Status != XST_SUCCESS) {
            printf("XSpi_WriteBuf Failed\r\n");
            return -XST_FAILURE;
        }
        rxBuf[0] = data;

        rxBuf++;
    }
    metal_device_close(Spi.device);

    return XST_SUCCESS;
}

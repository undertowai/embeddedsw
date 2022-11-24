

#include "xspi.h"
#include "xspi_l.h"
#include "printf.h"

#include "shared.h"


#define XSPI_SIGNATURE "quad_spi"
#define XSPI_COMPATIBLE_STRING "xlnx,axi-quad-spi"
#define XSPI_PLATFORM_DEVICE_DIR "/sys/bus/platform/devices/"
#define XSPI_COMPATIBLE_PROPERTY "compatible" /* device tree property */

Xmetal_dev_parm_t Xspi_DevParm =
{
	XSPI_SIGNATURE,
	XSPI_COMPATIBLE_STRING,
	XSPI_PLATFORM_DEVICE_DIR,
	XSPI_COMPATIBLE_PROPERTY
};

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

static int _metal_init (void)
{
    struct metal_init_params init_param = {
	    .log_handler	= metal_default_log_handler,
	    .log_level	= METAL_LOG_WARNING,
    };

	if (metal_init(&init_param)) {
		printf("ERROR: Failed to run metal initialization\n");
		return XST_FAILURE;
	}
    return XST_SUCCESS;
}

static int _SpiInit(XSpi *Spi, const char *devName)
{
    int Status = XST_SUCCESS;
    u32 ControlReg;

    Status = _metal_init();
 	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}   

    strcpy(Xspi_DevParm.name, devName);
    Status = XSpi_Initialize(Spi, &Xspi_DevParm);
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
    XSpi Spi;
    int Status;

    Status = _SpiInit(&Spi, devName);
    if (Status != XST_SUCCESS) {
        return Status;
    }
    printf("Sending Data; %s len=%d, Burst size=%d SS=%d\r\n", devName, len, bytesInBurst, SS);

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
    XSpi Spi;
    int Status;

    Status = _SpiInit(&Spi, devName);
    if (Status != XST_SUCCESS) {
        return Status;
    }
    printf("Reading Data; len=%d, Burst size=%d\r\n", len, bytesInBurst);

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

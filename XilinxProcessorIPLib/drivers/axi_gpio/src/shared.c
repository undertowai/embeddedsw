
#include <metal_api.h>
#include <xstatus.h>

#if USE_METAL

u32 XGpio_RegisterMetal(XGpio_t *InstancePtr)
{
	s32 Status;

	/* Map RFDC device IO region */
	InstancePtr->io = metal_device_io_region(InstancePtr->device, 0);
	if (InstancePtr->io == NULL) {
		metal_log(METAL_LOG_ERROR, "\n Failed to map XGPIO region for %s.\n", InstancePtr->device->name);
		return XST_DMA_ERROR;

	}

	return XST_SUCCESS;
}

static int _AXI_Gpio_Init(XGpio_t *Gpio, const char *devName)
{
    int Status = XST_SUCCESS;
    u32 ControlReg;

    Status = _metal_init();
 	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}   

    Status = metal_device_open("platform", devName, &Gpio->device);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", devName);
		return -XST_FAILURE;
	}

    XGpio_RegisterMetal(Gpio);
	if (Status != XST_SUCCESS) {
        metal_device_close(Gpio->device);
		return -XST_FAILURE;
	}

    return Status;
}

#else /*USE_METAL*/

static int _AXI_Gpio_Init(XGpio_t *Gpio, const char *devName, u32 base, u32 size)
{
	int fd = open("/dev/mem", O_RDWR | O_SYNC);
	Gpio->io = (void *)mmap(NULL, size, PROT_READ | PROT_WRITE, MAP_SHARED,
			fd, base);

	if (Gpio->io == MAP_FAILED) {
		return -XST_FAILURE;
	}
	return fd;
}

#endif /*USE_METAL*/

int AXI_Gpio_Set(const char *DevName, u32 base, u32 size, u32 val)
{
    int fd;
    XGpio_t Gpio = {0};

    fd = _AXI_Gpio_Init(&Gpio, DevName, base, size);
	if (fd == XST_FAILURE) {
		return XST_FAILURE;
	}

    Xil_Out32(Gpio.io, 0x0, val);
#if USE_METAL
	metal_device_close(Gpio.device);
else
	close(fd);
#endif
    return XST_SUCCESS;
}

int AXI_Gpio_Read(const char *DevName, u32 base, u32 size, u32 *val)
{
    int fd;
    XGpio_t Gpio = {0};

    fd = _AXI_Gpio_Init(&Gpio, DevName, base, size);
	if (fd == XST_FAILURE) {
		return XST_FAILURE;
	}

    *val = Xil_In32(Gpio.io, 0x0);
#if USE_METAL
	metal_device_close(Gpio.device);
#else
	close(fd);
#endif
    return XST_SUCCESS;
}
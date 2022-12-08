
#include <metal_api.h>
#include <xstatus.h>

typedef struct {
    struct metal_io_region *io; /* Libmetal IO structure */
	struct metal_device *device; /* Libmetal device structure */
} XGpio_t;

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

int AXI_Gpio_Set(const char *DevName, u32 val)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, DevName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}

    Xil_Out32(Gpio.io, 0x0, val);
	metal_device_close(Gpio.device);
    return Status;
}

int AXI_Gpio_Read(const char *DevName, u32 *val)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, DevName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}

    *val = Xil_In32(Gpio.io, 0x0);
	metal_device_close(Gpio.device);

    return Status;
}
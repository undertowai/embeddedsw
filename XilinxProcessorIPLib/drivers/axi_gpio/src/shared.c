
#include <metal_api.h>
#include <xstatus.h>

typedef struct {
    struct metal_io_region *io; /* Libmetal IO structure */
	struct metal_device *device; /* Libmetal device structure */
} XGpio_t;

static int Gpio_Dev_Init(XGpio_t *Gpio, const char *devName)
{
	metal_dev_io_t mdev;

    if (XST_SUCCESS != metal_dev_io_init(&mdev, devName)) {
		return XST_FAILURE;
	}
	Gpio->device = mdev.device;
	Gpio->io = mdev.io;
	return XST_SUCCESS;
}


int AXI_Gpio_Set(const char *DevName, u32 val)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != Gpio_Dev_Init(&Gpio, DevName)) {
		return XST_FAILURE;
	}

    Xil_Out32(Gpio.io, 0x0, val);
	metal_device_close(Gpio.device);
	metal_finish();
    return XST_SUCCESS;
}

int AXI_Gpio_Read(const char *DevName, u32 base, u32 size, u32 *val)
{
    int fd;
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != Gpio_Dev_Init(&Gpio, DevName)) {
		return XST_FAILURE;
	}

    *val = Xil_In32(Gpio.io, 0x0);
	metal_device_close(Gpio.device);
	metal_finish();
    return XST_SUCCESS;
}
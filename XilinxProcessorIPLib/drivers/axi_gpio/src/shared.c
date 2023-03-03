
#include <metal_api.h>
#include <xstatus.h>

int Gpio_Dev_Init_NoMetal(metal_dev_io_t *mdev, const char *devName)
{
    int Status = XST_SUCCESS;

    Status = metal_device_open("platform", devName, &mdev->device);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", devName);
		return XST_FAILURE;
	}

	mdev->io = metal_device_io_region(mdev->device, 0);

	if (NULL == mdev->io) {
        metal_device_close(mdev->device);
		return XST_FAILURE;
	}
    return Status;
}

static int Gpio_Dev_Init(metal_dev_io_t *mdev, const char *devName)
{
    if (XST_SUCCESS != metal_dev_io_init(mdev, devName)) {
		return XST_FAILURE;
	}
	return XST_SUCCESS;
}


int AXI_Gpio_Set(const char *DevName, u32 val, u32 val2)
{
    metal_dev_io_t Gpio = {0};

	if (XST_SUCCESS != Gpio_Dev_Init(&Gpio, DevName)) {
		return XST_FAILURE;
	}

    Xil_Out32(Gpio.io, 0x0, val);
	Xil_Out32(Gpio.io, 0x8, val2);
	metal_device_close(Gpio.device);
	metal_finish();
    return XST_SUCCESS;
}

int AXI_Gpio_Init_NoMetal(void **ptr, const char *DevName)
{
    metal_dev_io_t *Gpio = (metal_dev_io_t *)malloc(sizeof(metal_dev_io_t));

	if (Gpio == NULL) {
		return XST_FAILURE;
	}
	memset(Gpio, 0, sizeof(*Gpio));

	if (XST_SUCCESS != Gpio_Dev_Init_NoMetal(Gpio, DevName)) {
		return XST_FAILURE;
	}
	*ptr = Gpio;
    return XST_SUCCESS;
}

int AXI_Gpio_Finish_NoMetal(void *ptr)
{
    metal_dev_io_t *Gpio = (metal_dev_io_t *)ptr;

	metal_device_close(Gpio->device);
	free(ptr);
    return XST_SUCCESS;
}

int AXI_Gpio_Set_NoMetal(void *ptr, uint32_t val, uint32_t val2)
{
    metal_dev_io_t *Gpio = (metal_dev_io_t *)ptr;

    Xil_Out32(Gpio->io, 0x0, val);
	Xil_Out32(Gpio->io, 0x8, val2);
    return XST_SUCCESS;
}

int AXI_Gpio_Read(const char *DevName, u32 base, u32 size, u32 *val)
{
    int fd;
    metal_dev_io_t Gpio = {0};

	if (XST_SUCCESS != Gpio_Dev_Init(&Gpio, DevName)) {
		return XST_FAILURE;
	}

    *val = Xil_In32(Gpio.io, 0x0);
	metal_device_close(Gpio.device);
	metal_finish();
    return XST_SUCCESS;
}
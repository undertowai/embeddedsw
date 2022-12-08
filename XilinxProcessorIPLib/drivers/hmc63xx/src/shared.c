

//TODO: Fix these

#include <metal_api.h>
#include <xstatus.h>

#include "axi_gpio.h"
#include "hmc.h"

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

int HMC63xx_GpioInit(const char *devName)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc63xx_SpiCoreInit(&Gpio);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6300_SetIfGain(const char *devName, int ic, int val)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_SetIfGain(&Gpio, ic, val);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6300_RMW(const char *devName, int ic, u32 i, u32 val, u32 mask)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_rmw(&Gpio, ic, i, val, mask);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6300_SendDefaultConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_def_init(&Gpio, ic, 0, TRUE);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6300_CheckConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    Status = hmc6300_check_def_config(&Gpio, ic);
    if (Status) {
        metal_device_close(Gpio.device);
        return Status;
    }

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6300_PrintConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_dump_regs(&Gpio, ic);
    //hmc6300_print_status(&Gpio, ic);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6301_SendDefaultConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6301_def_init(&Gpio, ic, 0, TRUE);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6301_RMW(const char *devName, int ic, u32 i, u32 val, u32 mask)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6301_rmw(&Gpio, ic, i, val, mask);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6301_CheckConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    Status = hmc6301_check_def_config(&Gpio, ic);
    if (Status) {
        metal_device_close(Gpio.device);
        return Status;
    }

    metal_device_close(Gpio.device);

    return Status;
}


int HMC6301_PrintConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6301_dump_regs(&Gpio, ic);
    //hmc6301_print_status(&Gpio, ic);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC63xx_Reset (const char *devName)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _AXI_Gpio_Init(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_set_reset(&Gpio);
    hmc6301_set_reset(&Gpio);

    metal_device_close(Gpio.device);
    return Status;
}
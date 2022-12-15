

#include <metal_api.h>
#include <xstatus.h>

#include "axi_gpio.h"
#include "hmc.h"

static int HMC_Dev_Init(XGpio_t *Gpio, const char *devName)
{
	metal_dev_io_t mdev;

    if (XST_SUCCESS != metal_dev_io_init(&mdev, devName)) {
		return XST_FAILURE;
	}
	Gpio->device = mdev.device;
	Gpio->io = mdev.io;
	return XST_SUCCESS;
}

int HMC63xx_GpioInit(const char *devName)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc63xx_SpiCoreInit(&Gpio);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6300_SetIfGain(const char *devName, int ic, int val)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6300_SetIfGain(&Gpio, ic, val);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6300_SetRVGAGain(const char *devName, int ic, int val)
{
	int status = XST_SUCCESS;
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    if (hmc6300_RFVGAgain(&Gpio, ic, val)) {
		status = XST_FAILURE;
	}

	metal_device_close(Gpio.device);
    return status;
}

int HMC6300_Power(const char *devName, int ic, int pwup)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6300_powerup(&Gpio, ic, pwup);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6300_RMW(const char *devName, int ic, u32 i, u32 val, u32 mask)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6300_rmw(&Gpio, ic, i, val, mask);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6300_SendDefaultConfig(const char *devName, int ic)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6300_def_init(&Gpio, ic, 0, TRUE);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6300_CheckConfig(const char *devName, int ic)
{
    int Status = XST_SUCCESS;
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}

    if (hmc6300_check_def_config(&Gpio, ic)) {
        Status = XST_FAILURE;
    }

	metal_device_close(Gpio.device);
    return Status;
}

int HMC6300_PrintConfig(const char *devName, int ic)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6300_dump_regs(&Gpio, ic);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6301_SendDefaultConfig(const char *devName, int ic)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6301_def_init(&Gpio, ic, 0, TRUE);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6301_SetAtt(const char *devName, int ic, int i, int q, int att)
{
	int status = XST_SUCCESS;
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    if (hmc6301_attenuation(&Gpio, ic, i, q, att)) {
		status = XST_FAILURE;
	}

	metal_device_close(Gpio.device);
    return status;
}

int HMC6301_SetIfGain(const char *devName, int ic, int val)
{
	int status = XST_SUCCESS;
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    if (hmc6301_SetIfGain(&Gpio, ic, val)) {
		status  = XST_FAILURE;
	}

	metal_device_close(Gpio.device);
    return status;
}

int HMC6301_RMW(const char *devName, int ic, u32 i, u32 val, u32 mask)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6301_rmw(&Gpio, ic, i, val, mask);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC6301_CheckConfig(const char *devName, int ic)
{
    int Status = XST_SUCCESS;
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    if (hmc6301_check_def_config(&Gpio, ic)) {
        Status = XST_FAILURE;
    }

	metal_device_close(Gpio.device);
    return Status;
}


int HMC6301_PrintConfig(const char *devName, int ic)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6301_dump_regs(&Gpio, ic);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}

int HMC63xx_Reset (const char *devName)
{
    XGpio_t Gpio = {0};

	if (XST_SUCCESS != HMC_Dev_Init(&Gpio, devName)) {
		return XST_FAILURE;
	}
    hmc6300_set_reset(&Gpio);
    hmc6301_set_reset(&Gpio);

	metal_device_close(Gpio.device);
    return XST_SUCCESS;
}
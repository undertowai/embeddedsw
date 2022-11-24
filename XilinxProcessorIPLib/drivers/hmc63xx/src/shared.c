

//TODO: Fix these

#include <metal_api.h>
#include <xstatus.h>

#include "axi_gpio.h"
#include "hmc.h"

#define XSPI_SIGNATURE "axi_gpio"
#define XSPI_COMPATIBLE_STRING "xlnx,axi-gpio"
#define XSPI_PLATFORM_DEVICE_DIR "/sys/bus/platform/devices/"
#define XSPI_COMPATIBLE_PROPERTY "compatible" /* device tree property */

Xmetal_dev_parm_t XGpio_DevParm =
{
	XSPI_SIGNATURE,
	XSPI_COMPATIBLE_STRING,
	XSPI_PLATFORM_DEVICE_DIR,
	XSPI_COMPATIBLE_PROPERTY
};

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

static int _HMC_SpiInit(XGpio_t *Gpio, const char *devName)
{
    int Status = XST_SUCCESS;
    u32 ControlReg;

    Status = _metal_init();
 	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}   

    strcpy(XGpio_DevParm.name, devName);

    Status = metal_device_open("platform", XGpio_DevParm.name, &Gpio->device);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", XGpio_DevParm.name);
		return -XST_FAILURE;
	}

    XGpio_RegisterMetal(Gpio);
	if (Status != XST_SUCCESS) {
        metal_device_close(Gpio->device);
		return -XST_FAILURE;
	}

    return Status;
}

int HMC6300_SendDefaultConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _HMC_SpiInit(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_def_init(&Gpio, ic, 0, TRUE);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6300_PrintConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _HMC_SpiInit(&Gpio, devName);
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

    Status = _HMC_SpiInit(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6301_def_init(&Gpio, ic, 0, TRUE);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC6301_PrintConfig(const char *devName, int ic)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _HMC_SpiInit(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_dump_regs(&Gpio, ic);
    //hmc6301_print_status(&Gpio, ic);

    metal_device_close(Gpio.device);

    return Status;
}

int HMC63xx_Reset (const char *devName)
{
    s32 Status;
    XGpio_t Gpio = {0};

    Status = _HMC_SpiInit(&Gpio, devName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}
    hmc6300_set_reset(&Gpio);
    hmc6301_set_reset(&Gpio);

    metal_device_close(Gpio.device);
    return Status;
}
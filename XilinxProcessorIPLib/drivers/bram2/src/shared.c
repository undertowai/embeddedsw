
#include <metal_api.h>
#include <xstatus.h>

typedef struct {
    struct metal_io_region *io; /* Libmetal IO structure */
	struct metal_device *device; /* Libmetal device structure */
} XBram_t;

u32 XBram_RegisterMetal(XBram_t *InstancePtr)
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

static int _AXI_Bram_Init(XBram_t *Bram, const char *devName)
{
    int Status = XST_SUCCESS;
    u32 ControlReg;

    Status = _metal_init();
 	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}   

    Status = metal_device_open("platform", devName, &Bram->device);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", devName);
		return -XST_FAILURE;
	}

    XBram_RegisterMetal(Bram);
	if (Status != XST_SUCCESS) {
        metal_device_close(Bram->device);
		return -XST_FAILURE;
	}

    return Status;
}

int AXI_Bram_Write(const char *DevName, u64 address, const u32 *data, u64 words)
{
    s32 Status;
    XBram_t Bram = {0};
	const u32 word_size = 4;
	u64 i;

    Status = _AXI_Bram_Init(&Bram, DevName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}

	for (i = 0; i < words; i++) {
		Xil_Out32(Bram.io, address, data[0]);
		data++;
		address += word_size;
	}

	metal_device_close(Bram.device);
    return Status;
}

int AXI_Bram_Read(const char *DevName, u64 address, u32 *data, u64 words)
{
    s32 Status;
    XBram_t Bram = {0};
	const u32 word_size = 4;
	u64 i;

    Status = _AXI_Bram_Init(&Bram, DevName);
	if (Status != XST_SUCCESS) {
		return -XST_FAILURE;
	}

	for (i = 0; i < words; i++) {
		data[0] = Xil_In32(Bram.io, address);
		data++;
		address += word_size;
	}
	metal_device_close(Bram.device);
    return Status;
}
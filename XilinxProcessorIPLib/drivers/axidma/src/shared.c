

#include <metal_api.h>
#include <xstatus.h>

#include "xaxidma.h"

XAxiDma_Config *XDMA_LookupConfig(struct metal_device **Deviceptr, XAxiDma_Config *CfgPtr, const char *DeviceName)
{
	s32 Status = 0;
	u32 AddrWidth = 0;

	Status = metal_device_open_wrap("platform", DeviceName, Deviceptr);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", DeviceName);
		return NULL;
	}
	Status = metal_linux_get_device_property(*Deviceptr, "xlnx,addrwidth", &AddrWidth, sizeof(AddrWidth));

	AddrWidth = ntohl(AddrWidth);

	if (Status == XST_SUCCESS) {
		//TODO:
		CfgPtr->AddrWidth = AddrWidth;
		CfgPtr->BaseAddr = 0;
		CfgPtr->DeviceId = 0;
		CfgPtr->HasMm2S = 0;
		CfgPtr->HasMm2SDRE = 0;
		CfgPtr->HasS2Mm = 1;
		CfgPtr->HasS2MmDRE = 0;
		CfgPtr->HasSg = 0;
		CfgPtr->HasStsCntrlStrm = 0;
		CfgPtr->MicroDmaMode = 0;
		CfgPtr->Mm2SBurstSize = 0;
		CfgPtr->Mm2SDataWidth = 0;
		CfgPtr->Mm2sNumChannels = 0;
		CfgPtr->S2MmBurstSize = 0x100;
		CfgPtr->S2MmDataWidth = 0x100;
		CfgPtr->S2MmNumChannels = 1;
		CfgPtr->SgLengthWidth = 31;
	} else {
		metal_log(METAL_LOG_ERROR, "\n Failed to read device tree property \"reg\"");
		metal_device_close(*Deviceptr);
		return NULL;
	}

	return CfgPtr;
}

u32 XAxiDma_RegisterMetal(XAxiDma *InstancePtr)
{
	s32 Status;

	InstancePtr->io = metal_device_io_region(InstancePtr->device, 0);
	if (InstancePtr->io == NULL) {
		metal_log(METAL_LOG_ERROR, "\n Failed to map AXIDMA region for %s.\n", InstancePtr->device->name);
		return XST_DMA_ERROR;

	}

	return XST_SUCCESS;
}

static int Xdma_Init(XAxiDma *AxiDma, const char *DevName)
{
    int Status;
    XAxiDma_Config *CfgPtr, Cfg = {0};

	CfgPtr = XDMA_LookupConfig(&AxiDma->device, &Cfg, DevName);

	if (NULL == CfgPtr) {
		printf("ERROR: Failed to run XDMA_LookupConfig\n");
		return XST_FAILURE;
	}

	Status = XAxiDma_RegisterMetal(AxiDma);
	if (Status != XST_SUCCESS) {
		printf("Register metal failed %d\r\n", Status);
		metal_device_close(AxiDma->device);
		return XST_FAILURE;
	}

	Status = XAxiDma_CfgInitialize(AxiDma, CfgPtr);
	if (Status != XST_SUCCESS) {
		printf("Initialization failed %d\r\n", Status);
		metal_device_close(AxiDma->device);
		return XST_FAILURE;
	}
    return XST_SUCCESS;
}

int XDMA_StartTransfer(const char *DevName, u32 addr_hi, u32 addr_lo, u64 len)
{
	int Status;
	u64 addr = ((u64)addr_hi << 32) | addr_lo;
    XAxiDma Dma = {0};

    _metal_init();

    if (XST_SUCCESS != Xdma_Init(&Dma, DevName)) {
		metal_finish();
        return XST_FAILURE;
    }

	Status = XAxiDma_SimpleTransfer(&Dma, addr, len, XAXIDMA_DEVICE_TO_DMA);
    if (XST_SUCCESS != Status) {
		printf("XAxiDma_SimpleTransfer Failed : %d\r\n", Status);
    }

	metal_device_close(Dma.device);
	metal_finish();
    return Status;
}

int XDMA_Reset(const char *DevName)
{
    XAxiDma Dma = {0};
    _metal_init();

    if (XST_SUCCESS != Xdma_Init(&Dma, DevName)) {
        return -XST_FAILURE;
    }

    XAxiDma_Reset(&Dma);
	metal_device_close(Dma.device);
	metal_finish();
    return XST_SUCCESS;
}
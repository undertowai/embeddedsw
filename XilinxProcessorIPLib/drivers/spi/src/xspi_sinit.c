/******************************************************************************
* Copyright (C) 2005 - 2022 Xilinx, Inc.  All rights reserved.
* SPDX-License-Identifier: MIT
******************************************************************************/

/*****************************************************************************/
/**
*
* @file xspi_sinit.c
* @addtogroup spi_v4_9
* @{
*
* The implementation of the XSpi component's static initialization
* functionality.
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- ---- -------- -----------------------------------------------
* 1.01a jvb  10/13/05 First release
* 1.11a wgr  03/22/07 Converted to new coding style.
*
* </pre>
*
******************************************************************************/

/***************************** Include Files *********************************/

#include "xspi.h"

#include <metal/device.h>

#include <dirent.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <string.h>
#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>

#include <metal/sys.h>
#include <metal/irq.h>
#include <metal/sleep.h>
#include "metal/alloc.h"
#include <metal/device.h>
#include <metal/io.h>


/************************** Constant Definitions *****************************/


/**************************** Type Definitions *******************************/

/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/

/************************** Variable Definitions *****************************/

/*****************************************************************************/
/**
*
* Compare two strings in the reversed order.This function compares only
* the last "Count" number of characters of Str1Ptr and Str2Ptr.
*
* @param    Str1Ptr is base address of first string
* @param    Str2Ptr is base address of second string
* @param    Count is number of last characters  to be compared between
*           Str1Ptr and Str2Ptr
*
* @return
*           0 if last "Count" number of bytes matches between Str1Ptr and
*           Str2Ptr, else difference in unmatched character.
*
*@note     None.
*
******************************************************************************/
static s32 XSpi_Strrncmp(const char *Str1Ptr, const char *Str2Ptr, size_t Count)
{
	u16 Len1 = strlen(Str1Ptr);
	u16 Len2 = strlen(Str2Ptr);
	u8 Diff;

	for (; Len1 && Len2; Len1--, Len2--) {
		if ((Diff = Str1Ptr[Len1 - 1] - Str2Ptr[Len2 - 1]) != 0) {
			return Diff;
		}
		if (--Count == 0) {
			return 0;
		}
	}

	return (Len1 - Len2);
}


u32 XSpi_RegisterMetal(XSpi *InstancePtr, u16 DeviceId)
{
	s32 Status;

	/* Map RFDC device IO region */
	InstancePtr->io = metal_device_io_region(InstancePtr->device, 0);
	if (InstancePtr->io == NULL) {
		metal_log(METAL_LOG_ERROR, "\n Failed to map XSPI region for %s.\n", InstancePtr->device->name);
		return XST_DMA_ERROR;

	}

	return XST_SUCCESS;
}

#define XSPI_SIGNATURE "quad_spi"
#define XSPI_COMPATIBLE_STRING "xlnx,axi-quad-spi"
#define XSPI_PLATFORM_DEVICE_DIR "/sys/bus/platform/devices/"
#define XSPI_COMPATIBLE_PROPERTY "compatible" /* device tree property */

s32 XSpi_GetDeviceNameByDeviceId(char *DevNamePtr, u16 DevId)
{
	s32 Status = -1;
	u32 Data = 0;
	char CompatibleString[NAME_MAX];
	char DeviceName[NAME_MAX];
	struct metal_device *DevicePtr;
	DIR *DirPtr;
	struct dirent *DirentPtr;
	char Len = strlen(XSPI_COMPATIBLE_STRING);
	char SignLen = strlen(XSPI_SIGNATURE);

	DirPtr = opendir(XSPI_PLATFORM_DEVICE_DIR);
	if (DirPtr) {
		while ((DirentPtr = readdir(DirPtr)) != NULL) {
			if (XSpi_Strrncmp(DirentPtr->d_name, XSPI_SIGNATURE, SignLen) == 0) {

				Status = metal_device_open("platform", DirentPtr->d_name, &DevicePtr);
				if (Status) {
					metal_log(METAL_LOG_ERROR, "\n Failed to open device %s", DirentPtr->d_name);
					continue;
				}

				Status = metal_linux_get_device_property(DevicePtr, XSPI_COMPATIBLE_PROPERTY,
									 CompatibleString, Len);

				if (Status < 0) {
					metal_log(METAL_LOG_ERROR, "\n Failed to read device tree property");
				} else if (strncmp(CompatibleString, XSPI_COMPATIBLE_STRING, Len) == 0) {
					//FIXME:
					{
						strcpy(DevNamePtr, DirentPtr->d_name);
						Status = 0;
						metal_device_close(DevicePtr);
						break;
					}
					// Status = metal_linux_get_device_property(DevicePtr, XRFDC_CONFIG_DATA_PROPERTY,
					// 					 DeviceName, XRFDC_DEVICE_ID_SIZE);
					// printf("Data=%s, Status=%d\r\n", DeviceName, Status);
					// if (Status < 0) {
					// 	metal_log(METAL_LOG_ERROR, "\n Failed to read device tree property");
					// } else if (Data == DevId) {
					// 	strcpy(DevNamePtr, DirentPtr->d_name);
					// 	Status = 0;
					// 	metal_device_close(DevicePtr);
					// 	break;
					// }
				}
				metal_device_close(DevicePtr);
			}
		}
	}

   Status = (s32)closedir(DirPtr);
   if (Status < 0) {
      metal_log(METAL_LOG_ERROR, "\n Failed to close directory");
   }

	return Status;
}


/*****************************************************************************/
/**
*
* Looks up the device configuration based on the unique device ID. A table
* contains the configuration info for each device in the system.
*
* @param	DeviceId contains the ID of the device to look up the
*		configuration for.
*
* @return
*
* A pointer to the configuration found or NULL if the specified device ID was
* not found. See xspi.h for the definition of XSpi_Config.
*
* @note		None.
*
******************************************************************************/
XSpi_Config *XSpi_LookupConfig(struct metal_device **Deviceptr, u16 DeviceId)
{
	XSpi_Config *CfgPtr = NULL;
	u32 Index;
	s32 Status = 0;
	u32 NumInstances = 1;
	u32 AddrWidth = 0;
	char DeviceName[NAME_MAX];

	Status = XSpi_GetDeviceNameByDeviceId(DeviceName, DeviceId);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to find axidma device with device id %d", DeviceId);
		return NULL;
	}

	Status = metal_device_open("platform", DeviceName, Deviceptr);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", DeviceName);
		return NULL;
	}

	CfgPtr = (XSpi_Config *)malloc(sizeof(XSpi_Config));
	if (CfgPtr == NULL) {
		metal_log(METAL_LOG_ERROR, "\n Failed to allocate memory for XSpi_Config");
		metal_device_close(*Deviceptr);
		return NULL;
	}

	CfgPtr->device = *Deviceptr;

	CfgPtr->AxiFullBaseAddress = 0;
	CfgPtr->AxiInterface = 0;
	CfgPtr->BaseAddress = 0;
	CfgPtr->DataWidth = 8;
	CfgPtr->DeviceId = 0;
	CfgPtr->FifosDepth;
	CfgPtr->HasFifos = 0;
	CfgPtr->NumSlaveBits = 1;
	CfgPtr->SlaveOnly = 0;
	CfgPtr->SpiMode = 0;
	CfgPtr->Use_Startup = 0;
	CfgPtr->XipMode = 0;

	return CfgPtr;
}

/*****************************************************************************/
/**
*
* Initializes a specific XSpi instance such that the driver is ready to use.
*
* The state of the device after initialization is:
*	- Device is disabled
*	- Slave mode
*	- Active high clock polarity
*	- Clock phase 0
*
* @param	InstancePtr is a pointer to the XSpi instance to be worked on.
* @param	DeviceId is the unique id of the device controlled by this XSpi
*		instance. Passing in a device id associates the generic XSpi
*		instance to a specific device, as chosen by the caller or
*		application developer.
*
* @return
*
*		- XST_SUCCESS if successful.
*		- XST_DEVICE_IS_STARTED if the device is started. It must be
*		  stopped to re-initialize.
*		- XST_DEVICE_NOT_FOUND if the device was not found in the
*		  configuration such that initialization could not be
*		  accomplished.
*
* @note		None.
*
******************************************************************************/
int XSpi_Initialize(XSpi *InstancePtr, u16 DeviceId)
{
	XSpi_Config *ConfigPtr;	/* Pointer to Configuration ROM data */

	Xil_AssertNonvoid(InstancePtr != NULL);

	/*
	 * Lookup the device configuration in the temporary CROM table. Use this
	 * configuration info down below when initializing this component.
	 */
	ConfigPtr = XSpi_LookupConfig(&(InstancePtr->device), DeviceId);
	if (ConfigPtr == NULL) {
		return XST_DEVICE_NOT_FOUND;
	}

	XSpi_RegisterMetal(InstancePtr, DeviceId);

	return XSpi_CfgInitialize(InstancePtr, ConfigPtr,
				  ConfigPtr->BaseAddress);

}


void Xil_AssertNonvoid(void *Expression)
{
	if (!Expression) {
		abort();
	}
}

void Xil_AssertVoid(void *Expression)
{
	Xil_AssertNonvoid(Expression);
}

void Xil_AssertNonvoidAlways()
{
	Xil_AssertNonvoid(NULL);
}

void Xil_AssertVoidAlways()
{
	Xil_AssertNonvoid(NULL);
}


/** @} */

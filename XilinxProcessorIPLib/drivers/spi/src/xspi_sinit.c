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
XSpi_Config *XSpi_LookupConfig(struct metal_device **Deviceptr, const char *devName)
{
	XSpi_Config *CfgPtr = NULL;
	u32 Index;
	s32 Status = 0;
	u32 NumInstances = 1;
	u32 AddrWidth = 0;
	u32 u32_prop = 0;
	char *property_name;

	Status = metal_device_open_wrap("platform", devName, Deviceptr);
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to open device %s.\n", devName);
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

	property_name = "bits-per-word";
	Status = metal_linux_get_device_property(*Deviceptr, property_name, &u32_prop, sizeof(u32_prop));
	if (Status != XST_SUCCESS) {
		goto GET_PROPERTY_FAILED;
	}

	CfgPtr->DataWidth = ntohl(u32_prop);;
	CfgPtr->DeviceId = 0;

	property_name = "fifo-size";
	Status = metal_linux_get_device_property(*Deviceptr, property_name, &u32_prop, sizeof(u32_prop));
	if (Status != XST_SUCCESS) {
		goto GET_PROPERTY_FAILED;
	}

	CfgPtr->FifosDepth = ntohl(u32_prop);
	CfgPtr->HasFifos = !!u32_prop;

	property_name = "xlnx,num-ss-bits";
	Status = metal_linux_get_device_property(*Deviceptr, property_name, &u32_prop, sizeof(u32_prop));
	if (Status != XST_SUCCESS) {
		goto GET_PROPERTY_FAILED;
	}

	CfgPtr->NumSlaveBits = ntohl(u32_prop);
	CfgPtr->SlaveOnly = 0;

	property_name = "xlnx,spi-mode";
	Status = metal_linux_get_device_property(*Deviceptr, property_name, &u32_prop, sizeof(u32_prop));
	if (Status != XST_SUCCESS) {
		goto GET_PROPERTY_FAILED;
	}

	CfgPtr->SpiMode = ntohl(u32_prop);;
	CfgPtr->Use_Startup = 0;
	CfgPtr->XipMode = 0;
GET_PROPERTY_FAILED:
	if (Status != XST_SUCCESS) {
		metal_log(METAL_LOG_ERROR, "\n Failed to get property %s", property_name);
		metal_device_close(*Deviceptr);
		free(CfgPtr);
		CfgPtr = NULL;
	}

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
int XSpi_Initialize(XSpi *InstancePtr, const char *devName)
{
	int DeviceId = 0;
	XSpi_Config *ConfigPtr;	/* Pointer to Configuration ROM data */

	Xil_AssertNonvoid(InstancePtr != NULL);

	/*
	 * Lookup the device configuration in the temporary CROM table. Use this
	 * configuration info down below when initializing this component.
	 */
	ConfigPtr = XSpi_LookupConfig(&(InstancePtr->device), devName);
	if (ConfigPtr == NULL) {
		return XST_DEVICE_NOT_FOUND;
	}

	XSpi_RegisterMetal(InstancePtr, DeviceId);

	return XSpi_CfgInitialize(InstancePtr, ConfigPtr,
				  ConfigPtr->BaseAddress);

}


/** @} */

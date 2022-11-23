/******************************************************************************
* Copyright (C) 2008 - 2021 Xilinx, Inc.  All rights reserved.
* SPDX-License-Identifier: MIT
******************************************************************************/

/******************************************************************************/
/**
* @file xspi_selftest_example.c
*
* This file contains a example for using the SPI Hardware and driver.
*
* @note
*
* None
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date     Changes
* ----- ---- -------- -----------------------------------------------
* 1.00a sv   05/16/05 Initial release for TestApp integration.
* 1.11a sdm  03/03/08 Minor changes to comply to coding guidelines
* 3.00a ktn  10/28/09 Converted all register accesses to 32 bit access.
*		      Updated to use the HAL APIs/macros. Replaced call to
*		      XSpi_Initialize API with XSpi_LookupConfig and
*		      XSpi_CfgInitialize.
* 4.2   ms   01/23/17 Added printf statement in main function to
*                     ensure that "Successfully ran" and "Failed" strings
*                     are available in all examples. This is a fix for
*                     CR-965028.
* </pre>
*
*******************************************************************************/

/***************************** Include Files **********************************/

#include "xspi.h"
#include "xspi_l.h"
#include "printf.h"

/************************** Constant Definitions ******************************/

#define XSPI_SIGNATURE "quad_spi"
#define XSPI_COMPATIBLE_STRING "xlnx,axi-quad-spi"
#define XSPI_PLATFORM_DEVICE_DIR "/sys/bus/platform/devices/"
#define XSPI_COMPATIBLE_PROPERTY "compatible" /* device tree property */

Xmetal_dev_parm_t Xspi_DevParm =
{
	XSPI_SIGNATURE,
	XSPI_COMPATIBLE_STRING,
	XSPI_PLATFORM_DEVICE_DIR,
	XSPI_COMPATIBLE_PROPERTY
};

/*
 * The following constants map to the XPAR parameters created in the
 * xparameters.h file. They are defined here such that a user can easily
 * change all the needed parameters in one place.
 */
#define SPI_DEVICE_ID       0

/**************************** Type Definitions ********************************/


/***************** Macros (Inline Functions) Definitions **********************/


/************************** Function Prototypes *******************************/

int SpiSelfTestExample(u16 DeviceId);

/************************** Variable Definitions ******************************/

XSpi Spi; /* The instance of the SPI device */


/******************************************************************************/
/**
* Main function to call the example. This function is not included if the
* example is generated from the TestAppGen test tool.
*
*
* @return	XST_SUCCESS if successful, XST_FAILURE if unsuccessful
*
* @note		None
*
*******************************************************************************/
#ifndef TESTAPP_GEN
int main(void)
{
	int Status;

	struct metal_init_params init_param = METAL_INIT_DEFAULTS;

	if (metal_init(&init_param)) {
		printf("ERROR: Failed to run metal initialization\n");
		return XST_FAILURE;
	}

	/*
	 * Call the example , specify the device ID that is generated in
	 * xparameters.h
	 */
	Status = SpiSelfTestExample(SPI_DEVICE_ID);
	if (Status != XST_SUCCESS) {
	printf("Spi selftest Example Failed\r\n");
	return XST_FAILURE;
	}

	printf("Successfully ran Spi selftest Example\r\n");
	return XST_SUCCESS;
}
#endif


/*****************************************************************************/
/**
*
* This function does a selftest and loopback test on the SPI device and
* XSpi driver as an example. The purpose of this function is to illustrate
* how to use the XSpi component.
*
*
* @param	DeviceId is the XPAR_<SPI_instance>_DEVICE_ID value from
*		xparameters.h
*
* @return	XST_SUCCESS if successful, XST_FAILURE if unsuccessful
*
* @note		None
*
****************************************************************************/
int SpiSelfTestExample(u16 DeviceId)
{
	int Status;
	XSpi_Config *ConfigPtr;	/* Pointer to Configuration data */
	struct metal_device *Deviceptr; 

	Status = XSpi_Initialize(&Spi, SPI_DEVICE_ID);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	/*
	 * Perform a self-test to ensure that the hardware was built correctly
	 */
	Status = XSpi_SelfTest(&Spi);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}

	return XST_SUCCESS;
}


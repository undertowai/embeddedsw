/******************************************************************************
* Copyright (c) 2020 - 2021 Xilinx, Inc. All rights reserved.
* SPDX-License-Identifier: MIT
******************************************************************************/

/*****************************************************************************/
/**
*
* @file xplm_stl.c
*
* This file contains the wrapper code for STL interface
*
* <pre>
* MODIFICATION HISTORY:
*
* Ver   Who  Date        Changes
* ----- ---- -------- -------------------------------------------------------
* 1.00  rama 08/12/2020 Initial release
* 1.01  rama 03/22/2021 Updated hook for periodic STL execution and FTTI
*                       configuration
*
* </pre>
*
* @note
*
******************************************************************************/

/***************************** Include Files *********************************/
#include "xplm_default.h"

#ifdef PLM_ENABLE_STL
#include "xstl_plminterface.h"
#include "xplm_stl.h"
#include "xplm_pm.h"

/************************** Constant Definitions *****************************/

/**************************** Type Definitions *******************************/

/***************** Macros (Inline Functions) Definitions *********************/

/************************** Function Prototypes ******************************/
static int XPlm_ChangeStlPeriodicity(u32 FttiTime);

/************************** Variable Definitions *****************************/

/*****************************************************************************/
/**
 * @brief This function is used as a callback to change FTTI time for STL
 *
 * @param	FttiTime New FTTI time
 *
 * @return	XST_SUCCESS or error code in case of failure
 *
 *****************************************************************************/
static int XPlm_ChangeStlPeriodicity(u32 FttiTime)
{
	int Status = XST_FAILURE;
	u32 *NewFtti = &FttiTime;

	if (FttiTime < DEFAULT_FTTI_TIME) {
		Status = XST_INVALID_PARAM;
		goto END;
	}

	Status = XPlm_RemoveKeepAliveTask();
	if (XST_SUCCESS != Status) {
		goto END;
	}

	Status = XPlm_CreateKeepAliveTask((void *)NewFtti);

END:
	return Status;
}

/*****************************************************************************/
/**
 * @brief This function initializes the STL module and registers the
 * STL handler.
 *
 * @return	Status as defined in xplmi_status.h
 *
 *****************************************************************************/
int XPlm_StlInit(void)
{
	int Status = XST_FAILURE;

	Status = XStl_Init(XPlm_ChangeStlPeriodicity);
	if (Status != XST_SUCCESS)
	{
		Status = XPlmi_UpdateStatus(XPLM_ERR_STL_MOD, Status);
		goto END;
	}

END:
	return Status;
}

/*****************************************************************************/
/**
 * @brief This function is used as a hook to run PLM STLs periodically
 *
 * @return	Status as defined in xplmi_status.h
 *
 *****************************************************************************/
int XPlm_PeriodicStlHook(void)
{
	int Status = XST_FAILURE;

	Status = XStl_PlmPeriodicTask();
	if (XST_SUCCESS != Status) {
		Status = XPlmi_UpdateStatus(XPLM_ERR_STL_MOD, Status);
	}

	return Status;
}
#endif /* PLM_ENABLE_STL */

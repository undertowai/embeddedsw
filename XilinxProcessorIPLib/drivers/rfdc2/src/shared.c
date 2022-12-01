
/***************************** Include Files *********************************/
#include <stdio.h>
#include <stdarg.h>
#include <metal_api.h>
#include <xstatus.h>
#include <unistd.h>
#include "xstatus.h"
#include "xrfdc.h"
#include "LMK_display.h"
#include "LMX_display.h"
#include "xrfclk.h"
#include <metal/log.h>
#include <metal/sys.h>

#ifdef RFDC_CLI
#include "rfdc_poweron_status.h"
#include "rfdc_cmd.h"
//#include "adc_CalCoefficients.h"
#include "adc_FreezeCal.h"
#include "rfdc_nyquistzone.h"
#include "adc_LinkCoupling.h"
#endif

// Includes for user added CLI functions used in this file
#include "rfdc_interpolation_decimation.h"
#include "rfdc_mts.h"
#include "rfdc_dsa_vop.h"

#ifdef RFDC_CLI
#include "adcSaveCalCoefficients.h"
#include "adcGetCalCoefficients.h"
#include "adcLoadCalCoefficients.h"
#include "adcDisableCoeffOvrd.h"
#endif

/******************** Constant Definitions **********************************/
#define ENABLE_METAL_PRINTS

// PLL debug defines. Will print all calculated values
#undef LMK_DEBUG
#undef LMX_DEBUG

/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes ******************************/

void my_metal_default_log_handler(enum metal_log_level level,
			       const char *format, ...);

static int resetAllClk104(void);
void reverse32bArray(u32 *src, int size);
int printCLK104_settings(void);

/************************** Variable Definitions *****************************/

// VT100 esc sequences
char CHAR_ATTRIB_OFF[5] = "\x1B[0m";
char BOLD_ON[5]      	= "\x1B[1m";
char UNDERLINE_ON[5] 	= "\x1B[4m";
char BLINK_ON[5]        = "\x1B[5m";
char REVERSE_ON[5]    	= "\x1B[5m";

char CLR_SCREEN[5]   	= "\x1B[2J";


// data buffer used for reading PLL registers
static u32 data[256];

const char clkoutBrdNames[][18] = {
		"RFIN_RF1",   "RF1_ADC_SYNC",
		"NC",         "AMS_SYSREF",
		"RFIN_RF2",   "RF2_DAC_SYNC",
		"DAC_REFCLK", "DDR_PL_CAP_SYNC",
		"PL_CLK",     "PL_SYSREF",
		"NC",         "J10 SINGLE END",
		"ADC_REFCLK", "NC",
};

lmk_config_t lmkConfig;
lmx_config_t lmxConfig;

extern const u32 LMK_CKin[LMK_FREQ_NUM][LMK_COUNT];
extern const u32 LMX2594[][LMX2594_COUNT];

static int _metal_init (void)
{
	struct metal_init_params init_param = METAL_INIT_DEFAULTS;

	if (metal_init(&init_param)) {
		printf("ERROR: Failed to run metal initialization\n");
		return XST_FAILURE;
	}
	return XST_SUCCESS;
}

static int _RFDC_Init (XRFdc *RFdcInstPtr)
{
	int Status;
	u32  Val;
	u32  Minor;
	u32  Major;
	XRFdc_Config *ConfigPtr;
	struct metal_device *deviceptr;
	u32 RFdcDeviceId = 0;

	_metal_init();

	ConfigPtr = XRFdc_LookupConfig(RFdcDeviceId);
    if (ConfigPtr == NULL) {
		return XST_FAILURE;
	}

#ifndef __BAREMETAL__
	Status = XRFdc_RegisterMetal(RFdcInstPtr, RFdcDeviceId, &deviceptr);
	if (Status != XST_SUCCESS) {
		return XST_FAILURE;
	}
#endif

    Status = XRFdc_CfgInitialize(RFdcInstPtr, ConfigPtr);
    if (Status != XST_SUCCESS) {
        printf("RFdc Init Failure\n\r");
		return XST_FAILURE;
    }

	// Display IP version
	Val = Xil_In32(RFdcInstPtr->io, 0x00000);
	Major = (Val >> 24) & 0xFF;
	Minor = (Val >> 16) & 0xFF;

	return XST_SUCCESS;
}

int RFDC_Init_Clk104(void)
{
	int Status;
	int lmkConfigIndex;
	int gpioID = 343;


	printf("Configuring LMK...\r\n");
	/* The parameter is a gpioID, see Linux boot logging */
	XRFClk_Init(gpioID);

	lmkConfigIndex = 3;
	//LMX2594_FREQ_300M00_PD	if (XST_FAILURE == XRFClk_SetConfigOnAllChipsFromConfigId(lmkConfigIndex, LMX2594_FREQ_8192M00, LMX2594_FREQ_7864M32)) {
	if (XST_FAILURE == XRFClk_SetConfigOnAllChipsFromConfigId(lmkConfigIndex, LMX2594_FREQ_300M00_PD, LMX2594_FREQ_300M00_PD)) {
		return XST_FAILURE;
		printf("Failure in XRFClk_SetConfigOnAllChipsFromConfigId()\n\r");
	}

	// if (XST_FAILURE == XRFClk_SetConfigOnOneChipFromConfigId(RFCLK_LMK, 5)) {
	// 	printf("\nFailure in XRFClk_SetConfigOnAllChipsFromConfigId()");
	// 	return XST_FAILURE;
	// }

	if (XST_SUCCESS != printCLK104_settings()) {
		XRFClk_Close();
		return XST_FAILURE;
	}

	XRFClk_Close();

	return XST_SUCCESS;
}

int RFDC_Restart(void)
{
	int Status;
	XRFdc_Config *ConfigPtr;
	int lmkConfigIndex;
	XRFdc RFdcInst;      /* RFdc driver instance */

	Status = _RFDC_Init(&RFdcInst);

    if (Status != XST_SUCCESS) {
        printf("RFdc Init Failure\n\r");
		return XST_FAILURE;
    }

	rfdcStartup(&RFdcInst);
	rfdcReady(&RFdcInst);
	dacCurrent(&RFdcInst);

	return XST_SUCCESS;
}

int RFDC_GetSamplingFreq (void)
{
	int SamplingFreq;
	int Status;
	XRFdc RFdcInst;      /* RFdc driver instance */

	Status = _RFDC_Init(&RFdcInst);

    if (Status != XST_SUCCESS) {
        printf("RFdc Init Failure\n\r");
		return XST_FAILURE;
    }

	XRFdc* RFdcInstPtr = &RFdcInst;
	XRFdc_BlockStatus blockStatus;
	u32 InterpolationFactor;

	if(XRFdc_IsDACBlockEnabled(RFdcInstPtr, 0, 0)) {
		XRFdc_GetBlockStatus(RFdcInstPtr, XRFDC_DAC_TILE, 0, 0, &blockStatus);
		SamplingFreq = blockStatus.SamplingFreq * 1e9;
	} else {
		xil_printf("Error reading DAC 0 sampling rate\r\n");
		return -XST_FAILURE;
	}

	Status = XRFdc_GetInterpolationFactor(RFdcInstPtr, 0, 0, &InterpolationFactor);
	if (Status != XST_SUCCESS) {
		xil_printf("XRFdc_GetInterpolationFactor() failed\r\n");
		return -XST_FAILURE;
	}

	// update Sampling Freq with interpolation factor to represent sampling freq
	// of axis interface
	SamplingFreq = SamplingFreq / (float)InterpolationFactor;

	return SamplingFreq / 1000000;
}

/****************************************************************************/
/**
*
* This function resets all CLK_104 PLL I2C devices.
*
* @param	None
*
* @return
*	- XST_SUCCESS if successful.
*	- XST_FAILURE if failed.
*
* @note		None
*
****************************************************************************/
static int resetAllClk104(void)
{
	int ret = EXIT_FAILURE;
//	printf("Reset LMK\n\r");
	if (XST_FAILURE == XRFClk_ResetChip(RFCLK_LMK)) {
		printf("Failure in XRFClk_ResetChip(RFCLK_LMK)\n\r");
		return ret;
	}

//	printf("Reset LMX2594_1\n\r");
	if (XST_FAILURE == XRFClk_ResetChip(RFCLK_LMX2594_1)) {
		printf("Failure in XRFClk_ResetChip(RFCLK_LMX2594_1)\n\r");
		return ret;
	}

//	printf("Reset LMX2594_2\n\r");
	if (XST_FAILURE == XRFClk_ResetChip(RFCLK_LMX2594_2)) {
		printf("Failure in XRFClk_ResetChip(RFCLK_LMX2594_2)\n\r");
		return ret;
	}

#ifdef XPS_BOARD_ZCU111
//	printf("Reset LMX2594_3\n\r");
	if (XST_FAILURE == XRFClk_ResetChip(RFCLK_LMX2594_3)) {
		printf("Failure in XRFClk_ResetChip(RFCLK_LMX2594_3)\n\r");
		return ret;
	}
#endif

	return EXIT_SUCCESS;
}


/****************************************************************************/
/**
*
* Print LMK PLL device settings such as input and output clk frequencies.
* The instance structure is initialized by calling LMK_init()
*
* @param
*	- lmkInstPtr a pointer to the LMK instance structure
*
* @return
*	- void
*
* @note		None
*
****************************************************************************/
void printLMKsettings(lmk_config_t *lmkInstPtr)
{


#ifdef LMK_DEBUG
    LMK_intermediateDump(lmkInstPtr);
#endif

    // Print LMK CLKin frequencies
    if(lmkInstPtr->clkin_sel_mode == LMK_CLKin_SEL_MODE_AUTO_MODE ) {
    	printf("CLKin Auto Mode Enabled\n\r");
    }
    for(int i=0; i<3; i++) {
    	if(lmkInstPtr->clkin[i].freq != -1) {
    		printf("CLKin%d_freq: %12ldKHz\n\r", i, lmkInstPtr->clkin[i].freq/1000);
    	}
    }

    // Print LMK CLKout frequencies
	for(int i=0; i<7; i++) {
		printf("DCLKout%02d(%-10s):", i*2, clkoutBrdNames[i*2]);
		if(lmkInstPtr->clkout[i].dclk_freq == -1) {
			printf("%12s", "-----");
		} else {
			printf("%9ldKHz", lmkInstPtr->clkout[i].dclk_freq/1000);
		}

		printf(" SDCLKout%02d(%-15s):", i*2 + 1, clkoutBrdNames[i*2 +1]);
		if(lmkInstPtr->clkout[i].sclk_freq == -1) {
			printf("%12s\n\r", "-----");
		} else {
			printf("%9ldKHz\n\r", lmkInstPtr->clkout[i].sclk_freq/1000);
		}
	}
}


/****************************************************************************/
/**
*
* Print LMX PLL device output clk frequencies.
* The instance structure is initialized by calling LMX_SettingsInit()
*
* @param
* 	- clkin is the clk freq fed into the LMX PLL. This value is used to
* 	  calculate and display the output frequencies
*	- lmxInstPtr a pointer to the LMX instance structure
*
* @return
*	- void
*
* @note		None
*
****************************************************************************/
void printLMXsettings(long int clkin, lmx_config_t *lmxInstPtr)
{


#ifdef LMX_DEBUG
    LMX_intermediateDump(lmxInstPtr);
#endif

    // Print LMX CLKin freq
    printf("CLKin_freq: %10ldKHz\n\r", clkin/1000);


    // Print LMX CLKout frequencies
	printf("RFoutA Freq:");
	if(lmxInstPtr->RFoutA_freq == -1) {
		printf("%13s\n\r", "-----");
	} else {
		printf("%10ldKHz\n\r", lmxInstPtr->RFoutA_freq/1000);
	}

	printf("RFoutB Freq:");
	if(lmxInstPtr->RFoutB_freq == -1) {
		printf("%13s\n\r", "-----");
	} else {
		printf("%10ldKHz\n\r", lmxInstPtr->RFoutB_freq/1000);
	}

}


/****************************************************************************/
/**
*
* Reads the configuration of LMK and LMX PLL then calculates and displays
* the PLL frequencies and settings.
* The instance structures ar initialized by calling LMK_init() or
* LMX_SettingsInit()
*
* @param
* 	- nil
*
* @return
*	- void
*
* @note		None
*
****************************************************************************/
int printCLK104_settings(void)
{
	char pllNames[3][9] = {"LMK ----", "LMX_RF1", "LMX_RF2"};
	u32  chipIds[3] = {RFCLK_LMK, RFCLK_LMX2594_1, RFCLK_LMX2594_2};

	for(int i=0; i<(sizeof(chipIds) / sizeof(chipIds[0])); i++) {
		if (XST_FAILURE == XRFClk_GetConfigFromOneChip(chipIds[i], data)) {
			printf("Failure in XRFClk_GetConfigFromOneChip()\n\r");
			return XST_FAILURE;
		}

		// For LMX, reverse readback data to match exported register sets and
		// order of LMX2594[][]
		if(chipIds[i] != RFCLK_LMK) {
			reverse32bArray(data, LMX2594_COUNT-3);
		}

#if 0
		// Dump raw data read from device
		printf("Config data is:\n\r");
		for (int j = 0; j < ((chipIds[i]==RFCLK_LMK) ? LMK_COUNT : LMX2594_COUNT-3); j++) {
			printf("%08X, ", data[j]);
			if( !(j % 6) ) printf("\n\r");
		}
		printf("\n\r");
#endif

		// Display clock values of device
		printf("Clk settings read from %s ---------------------\n\r", pllNames[i]);
		if(chipIds[i] == RFCLK_LMK) {
			LMK_init(data, &lmkConfig);
			printLMKsettings(&lmkConfig);
		} else {
			// clkout index is i=1 idx = 0, i=2 idx=2. i&2 meets this alg
			LMX_SettingsInit(lmkConfig.clkout[ (i & 2) ].dclk_freq, data, &lmxConfig);
			printLMXsettings(lmkConfig.clkout[ (i & 2) ].dclk_freq, &lmxConfig);		}
		printf("\n\r");
	}

	return XST_SUCCESS;
}



void reverse32bArray(u32 *src, int size) {
	u32 tmp[200];
	int i, j;

	//copy src into temp
	for(i = 0, j=size - 1; i < size; i++, j--) {
		tmp[i] = src[j];
	}

	//copy swapped array to original
	for(i=0; i< size; i++) {
		src[i] = tmp[i];
	}
	return;
}



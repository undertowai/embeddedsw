/*
 * main.h
 *
 *  Created on: Sep 17, 2017
 *      Author: johnmcd
 */

#ifndef SRC_MAIN_H_
#define SRC_MAIN_H_

/***************************** Include Files ********************************/
#include <metal_api.h>
#include "xrfdc.h"

/******************** Constant Definitions **********************************/

// Necessary to use this define when using jtagterminal but not SDK jtaguart console
//#define STRIP_CHAR_CR


// RFDC defines
#define RFDC_DEVICE_ID 	0
#define RFDC_BASE       0

// Number of Tiles and Blocks in device
#define NUM_TILES 4
#define NUM_BLOCKS 4
/**************************** Type Definitions *******************************/


/***************** Macros (Inline Functions) Definitions *********************/


/************************** Function Prototypes *****************************/


/************************** Variable Definitions ****************************/

extern XRFdc RFdcInst;      /* RFdc driver instance */


#endif /* SRC_MAIN_H_ */

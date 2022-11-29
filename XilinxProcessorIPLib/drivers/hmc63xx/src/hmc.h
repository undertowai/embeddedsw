#ifndef HMC_H
#define HMC_H

#include "spi.h"

#define IS_EXTERNAL_LO (1)

void hmc6300_def_init (XGpio_t *gpio, u8 ic, u32 freq, u8 isExternalLo);
void hmc6300_print_status (XGpio_t *gpio, u8 ic);
void hmc6300_powerup(XGpio_t *gpio, u8 ic, u8 powerup);
void hmc6300_enableFM(XGpio_t *gpio, u8 ic, u8 enable);
void hmc6300_SetIfGain (XGpio_t *gpio, u8 ic, u8 steps_1_3dB);
void hmc6300_RFVGAgain (XGpio_t *gpio, u8 ic, u8 steps_1_3dB);
void hmc6300_writeArray(XGpio_t *gpio, u8 ic, u8 array, u8 data);
void hmc6300_exp_init(XGpio_t *gpio, u8 ic, u8 conf);
void hmc6300_set_reset(XGpio_t *gpio);
void hmc6300_dump_regs(XGpio_t *gpio, u8 ic);
void hmc6300_dump_reg(XGpio_t *gpio, u8 ic, u8 array);
int hmc6300_check_def_config(XGpio_t *gpio, u8 ic);

void hmc6301_def_init (XGpio_t *gpio, u8 ic, u32 freq, u8 isExternalLo);
void hmc6301_print_status (XGpio_t *gpio, u8 ic);
void hmc6301_powerup(XGpio_t *gpio, u8 ic, u8 powerup);
void hmc6301_writeArray(XGpio_t *gpio, u8 ic, u8 array, u8 data);
void hmc6301_exp_init(XGpio_t *gpio, u8 ic, u8 conf);
void hmc6301_set_reset(XGpio_t *gpio);
void hmc6301_dump_regs(XGpio_t *gpio, u8 ic);
void hmc6301_dump_reg(XGpio_t *gpio, u8 ic, u8 array);
void hmc6301_attenuation(XGpio_t *gpio, u8 ic, u8 atti, u8 attq, u8 att2);
void hmc6301_SetIfGain (XGpio_t *gpio, u8 ic, u8 steps_1_3dB);
int hmc6301_check_def_config(XGpio_t *gpio, u8 ic);

#endif /* HMC_H */
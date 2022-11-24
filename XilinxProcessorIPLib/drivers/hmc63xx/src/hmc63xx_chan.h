#ifndef HMC63XX_CHAN_H
#define HMC63XX_CHAN_H

#include "metal_api.h"

typedef struct {
    u32 freq;
    u8 Fbdiv_Code;
    u8 vco_bandSel;
} hmc63xx_Channel_t;

hmc63xx_Channel_t *hmc63xx_GetChannel(u32 freq);

#endif /* HMC63XX_CHAN_H */
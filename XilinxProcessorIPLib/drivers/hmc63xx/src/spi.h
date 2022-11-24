#ifndef HMC6300_SPI_H
#define HMC6300_SPI_H

#include "axi_gpio.h"

void hmc6300_SpiCoreInit(XGpio_t *gpio);
int hmc63xx_spi_write(XGpio_t *gpio, u8 grp, u8 ic, u8 chipAddr, u8 array, u8 data);
int hmc63xx_spi_read(XGpio_t *gpio, u8 grp, u8 ic, u8 chipAddr, u8 array, u8 *data);
void hmc63xx_reset(XGpio_t *gpio, u8 grp, u8 reset);

#endif /* HMC6300_SPI_H */
#include <xstatus.h>

#include "axi_gpio.h"
#include "spi.h"

#define NUM_GROUPS (2)
#define NUM_SLAVES (8)

#define HMC6300_SCK_PIN (0)
#define HMC6300_MOSI_PIN (1)
#define HMC6300_MISO_PIN (2)
#define HMC6300_CS_PIN(chip) ((chip) + HMC6300_MISO_PIN + 1)
#define HMC63XX_RESET_PIN (31)

#define _SS(gpio, grp, ic, v) gpio_set(gpio, grp, HMC6300_CS_PIN(ic), v)
#define _SCK(gpio, grp, v) gpio_set(gpio, grp, HMC6300_SCK_PIN, v)
#define _MOSI(gpio, grp, v) gpio_set(gpio, grp, HMC6300_MOSI_PIN, v)
#define _MISO(gpio, grp) gpio_get(gpio, grp, HMC6300_MISO_PIN)
#define _RESET(gpio, grp, v) gpio_set(gpio, grp, HMC63XX_RESET_PIN, v)

#define BYTE_TO_BINARY_PATTERN "%c%c%c%c%c%c%c%c"
#define BYTE_TO_BINARY(byte)  \
  (byte & 0x80 ? '1' : '0'), \
  (byte & 0x40 ? '1' : '0'), \
  (byte & 0x20 ? '1' : '0'), \
  (byte & 0x10 ? '1' : '0'), \
  (byte & 0x08 ? '1' : '0'), \
  (byte & 0x04 ? '1' : '0'), \
  (byte & 0x02 ? '1' : '0'), \
  (byte & 0x01 ? '1' : '0') 

int hmc63xx_spi_op(XGpio_t *gpio, u8 grp, u8 ic, u8 rw, u8 chipAddr, u8 array, u8 data)
{
    s8 i = 0;
    u32 outputData = data | (array << 8) | ((rw & 0b1) << 14) | (chipAddr << 15);

    if (array & ~0b111111) {
        xil_printf("hmc63xx_spi_op: Invalid parameter: array=%d\n\r", array);
        return XST_FAILURE;
    }

    //xil_printf("hmc63xx_spi_op: ic=%d, rw=%d, array=%d, data= " BYTE_TO_BINARY_PATTERN "/r/n", ic, rw, array, BYTE_TO_BINARY(data));
    _SCK(gpio, grp, 0);
    _SS(gpio, grp, ic, 0);

    /* LSB First */
    for (i = 0; i < 18; i++) {
        _MOSI(gpio, grp, (outputData >> i) & 0x1);
        _SCK(gpio, grp, 1);
        _SCK(gpio, grp, 0);
    }

    _MOSI(gpio, grp, 0);
    _SS(gpio, grp, ic, 1);
    return 0;
}

int hmc63xx_spi_write(XGpio_t *gpio, u8 grp, u8 ic, u8 chipAddr, u8 array, u8 data)
{
    return hmc63xx_spi_op(gpio, grp, ic, 1, chipAddr, array, data);
}

int hmc63xx_spi_read(XGpio_t *gpio, u8 grp, u8 ic, u8 chipAddr, u8 array, u8 *data)
{
    u8 i = 0, _data = 0;
    hmc63xx_spi_op(gpio, grp, ic, 0, chipAddr, array, 0);

    _SCK(gpio, grp, 1);
    _SCK(gpio, grp, 0);
    _SS(gpio, grp, ic, 0);

    for (i = 0; i < 8; i++) {
        _SCK(gpio, grp, 1);
        _SCK(gpio, grp, 0);
        _data |= _MISO(gpio, grp) << i;
    }

    _SS(gpio, grp, ic, 1);
    *data = _data;

    return 0;
}

void hmc63xx_reset(XGpio_t *gpio, u8 grp, u8 reset)
{
    _RESET(gpio, grp, reset &0x1);
}

static void _hmc63xx_SpiCoreInit(XGpio_t *gpio, u8 grp)
{
    u8 ic;
    gpio_conf(gpio, grp, HMC6300_SCK_PIN, GPIO_OUT);
    _SCK(gpio, grp, 0);
    gpio_conf(gpio, grp, HMC6300_MOSI_PIN, GPIO_OUT);
    _MOSI(gpio, grp, 0);
    gpio_conf(gpio, grp, HMC6300_MISO_PIN, GPIO_IN);
    gpio_conf(gpio, grp, HMC63XX_RESET_PIN, GPIO_OUT);
    for (ic = 0; ic < NUM_SLAVES; ic++) {
        gpio_conf(gpio, grp, HMC6300_CS_PIN(ic), GPIO_OUT);
        _SS(gpio, grp, ic, 1);
    }

    //Deassert reset
    _RESET(gpio, grp, 0);
}

void hmc63xx_SpiCoreInit(XGpio_t *gpio)
{
    u8 grp;

    for (grp = 0; grp < NUM_GROUPS; grp++) {
        _hmc63xx_SpiCoreInit(gpio, grp);
    }
}



#include "axi_gpio.h"

#define XPAR_SPI_GPIO_BASEADDR (0)

typedef struct {
    UINTPTR io;
    UINTPTR config;
} gpio_base_t;

gpio_base_t gpio_base[] =
{
    /* First and Second gpio groups; See UG */
    {0, 0x4},
    {0x8, 0xC},
};

static void _gpio_set(XGpio_t *gpio, UINTPTR base, u32 pin, u32 value)
{
    u32 tmpVal;

	tmpVal = Xil_In32(gpio->io, base);
    if (value) {
        tmpVal |= 1 << pin;
    } else {
        tmpVal &= ~(1 << pin);
    }

    Xil_Out32(gpio->io, base, tmpVal);
}

static u32 _gpio_get(XGpio_t *gpio, UINTPTR base, u32 pin)
{
    u32 tmpVal;

	tmpVal = Xil_In32(gpio->io, base);
    //usleep(1);
    return (tmpVal >> pin) & 0x1;
}

void gpio_conf(XGpio_t *gpio, u8 group, u32 pin, u32 value)
{
    _gpio_set(gpio, gpio_base[group].config, pin, value);
}

void gpio_set(XGpio_t *gpio, u8 group, u32 pin, u32 value)
{
    _gpio_set(gpio, gpio_base[group].io, pin, value);   
}

u32 gpio_get(XGpio_t *gpio, u8 group, u32 pin)
{
    return _gpio_get(gpio, gpio_base[group].io, pin);
}
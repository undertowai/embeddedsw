#ifndef AXI_GPIO_H
#define AXI_GPIO_H

#define GPIO_OUT (0)
#define GPIO_IN  (1)

//TODO: Fix these
#include <metal_api.h>
#include <xstatus.h>

void gpio_conf(XGpio_t *gpio, u8 group, u32 pin, u32 value);
void gpio_set(XGpio_t *gpio, u8 group, u32 pin, u32 value);
u32 gpio_get(XGpio_t *gpio, u8 group, u32 value);

#endif /* AXI_GPIO_H */
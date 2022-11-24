
#include "hmc63xx_chan.h"

const hmc63xx_Channel_t channelArray_500MHz[] =
{
    {565, 0b010001, 0b00001},
    {570, 0b010010, 0b00001},
    {575, 0b010011, 0b00010},
    {580, 0b010100, 0b00010},
    {585, 0b010101, 0b00010},
    {590, 0b010110, 0b00011},
    {595, 0b010111, 0b00011},
    {600, 0b011000, 0b00100},
    {605, 0b011001, 0b00100},
    {610, 0b011010, 0b00101},
    {615, 0b011011, 0b00101},
    {620, 0b011100, 0b00101},
    {625, 0b011101, 0b00110},
    {630, 0b011110, 0b00110},
    {635, 0b011111, 0b00110},
    {640, 0b100000, 0b00111},
    {0, 0, 0}
};

hmc63xx_Channel_t *hmc63xx_GetChannel(u32 freq)
{
    u32 i = 0;
    for (i = 0; channelArray_500MHz[i].freq != 0; i++) {
        if (channelArray_500MHz[i].freq == freq) {
            return &channelArray_500MHz[i];
        }
    }
    return NULL;
}

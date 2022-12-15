#ifndef HMC63XX_REG_H
#define HMC63XX_REG_H

#include "metal_api.h"

#define _N(x) (sizeof(x) / sizeof(x[0]))

typedef struct {
    u8 data;
    u8 isSet;
} row_t;

#define _ROW_TEST_PARAM(row, param, conf) \
do { \
    if (((conf)->param) > ROW ## row ## _ ## param ## _MS) { \
        xil_printf("Incorrect Value: %s: %d\r\n", #param, ((conf)->param)); \
    } \
} while(0)

#define ROW_SET(rows, row, param, conf) \
do { \
    _ROW_TEST_PARAM(row, param, conf); \
    (rows)[row].isSet = 1; \
    ( (rows)[row].data |= (((conf)->param) & ROW ## row ## _ ## param ## _MS) << ROW ## row ## _ ## param ## _OF); \
} while (0)

#define ROW_GET(reg, row, param) \
    ( ( (reg) >> ROW ## row ## _ ## param ## _OF) & ROW ## row ## _ ## param ## _MS)

#define ROW_DUMP(rows, row, param) \
do { \
    u8 reg = rows[row]; \
    u8 v = ROW_GET(reg, row, param); \
    xil_printf("ROW" #row "." #param " = 0x%0x\r\n", v); \
} while(0)

#define SET_EN(x) ((x) ? 0b1 : 0b0)

#endif /* HMC63XX_REG_H */

#include "hmc6301_reg_file.h"
#include "hmc63xx_chan.h"
#include "spi.h"

#include "../configs/hmc6301_60G_conf.h"

#define NUM_ICS (8)

#define CHIP_ADDR (0b111)

#define hmc6301_spi_write(gpio, ic, array, data) hmc63xx_spi_write(gpio, 0, ic, CHIP_ADDR, array, data)
#define hmc6301_spi_read(gpio, ic, addr, row)    hmc63xx_spi_read(gpio, 0, ic, CHIP_ADDR, addr, row)
#define hmc6301_reset(gpio, v) hmc63xx_reset(gpio, 0, v)

#define hmc6301_write_row(gpio, ic, i) \
do { \
    ROW ## i ## _SETALL(rows, &confPerIc[ic].row ## i); \
    hmc6301_spi_write(gpio, ic, i, rows[i].data); \
} while(0)

static     hmc6301_reg_file_t confPerIc[NUM_ICS] = {0};

static void _hmc6301_powerup(hmc6301_row0_t *row, hmc6301_row1_t *row1, u8 powerup);
static int _hmc6301_attenuation(hmc6301_row2_t *row, u8 atti, u8 attq, u8 att2);
static int _hmc6301_SetIfGain (hmc6301_row5_t *row, u8 steps_1_3dB);

static void _hmc6301_powerup(hmc6301_row0_t *row, hmc6301_row1_t *row1, u8 powerup)
{
    u8 powerdown = powerup ? 0b0 : 0b1;

    row->ifvga_pwrdn = powerdown;
    row->tripler_pwrdn = powerdown;
    row->ifmixer_pwrdn = powerdown;
    row->mixer_pwrdn = powerdown;
    row->divider_pwrdn = powerdown;
    row->bbamp_pwrdn_q = powerdown;
    row->bbamp_pwrdn_i = powerdown;
    row->lna_pwrdwn = powerdown;

    //Active high to power down the ASK demodulator.
    row1->ask_pwrdn = 0b1;
    row1->if_bgmux_pwrdn = powerdown;
    row1->ifmix_pwrdn_q = powerdown;
    row1->ipc_pwrdwn = powerdown;
}

static int _hmc6301_SetIfGain (hmc6301_row5_t *row, u8 steps_1_3dB)
{
    const u8 maxGain = 0xF;
    u8 dB_2_val = maxGain - steps_1_3dB;

    if (steps_1_3dB > maxGain) {
        xil_printf("_hmc6301_SetIfGain: Invalid parameter: steps_1_3dB=%d\n\r", steps_1_3dB);
        return -1;
    }
    row->ifvga_vga_adj = dB_2_val;
    return 0;
}

static int _hmc6301_attenuation(hmc6301_row2_t *row, u8 atti, u8 attq, u8 att2)
{
    const u8 attIQTable[] = {
        /* 0dB */ 0b000, /* 1dB */ 0b001, /* 2dB */ 0b010, /* 3dB */ 0b011, /* 4dB */ 0b100, /* 5dB */ 0b101};
    const u8 attTable[] = {
        /* 0dB */ 0b00, /* 6dB */ 0b01, /* 12dB */ 0b10, /* 18dB */ 0b11 };

    if (atti > _N(attIQTable)) {
        xil_printf("Parameter overflow: atti\r\n");
        return -1;
    }

    if (attq > _N(attIQTable)) {
        xil_printf("Parameter overflow: attq\r\n");
        return -1;
    }

    if (att2 > _N(attTable)) {
        xil_printf("Parameter overflow: att2\r\n");
        return -1;
    }

    row->bbamp_atten2 = attTable[att2];
    row->bbamp_attenfi = attIQTable[atti];
    row->bbamp_attenfq = attIQTable[attq];

    return 0;
}

static void _hmc6301_setFreq(hmc6301_row20_t *row20, hmc6301_row22_t *row22, u32 freq)
{
    hmc63xx_Channel_t *channel = hmc63xx_GetChannel(freq);
    if (channel) {
        row20->Fbdiv_code = channel->Fbdiv_Code;
        row22->vco_bandSel = channel->vco_bandSel;
    } else {
        xil_printf("_hmc6301_setFreq: Invalid Freq\r\n");
    }
}

static void _hmc6301_init_config (hmc6301_reg_file_t *conf, u8 isExternalLo)
{
    //TODO
    conf->row1.bbamp_sell_ask = 0b0;
    conf->row1.bbamp_sigshort = 0b0;

    conf->row1.bbamp_atten1 = 0; 
    
    _hmc6301_powerup(&conf->row0, &conf->row1, TRUE);
    _hmc6301_attenuation(&conf->row2, 0, 0, 0);

    //TODO
    conf->row3.if_refsel = 0b1;
    conf->row3.lna_refsel = 0b1;
    conf->row3.bg_monitor_sel = 0b00;
    conf->row3.bbamp_selfastrec = 0b00;
    //Selects the low-pass corner of the baseband amplifiers; 
    //500MHz
    conf->row3.bbamp_selbw = 0b00;

    //Active high to enable the digital control of the IF VGA gain 
    conf->row4.enDigVGA = 0b1;
    conf->row4.ifvga_tune = 0b1001111;

    conf->row5.rfmix_tune = 0b1111;
    _hmc6301_SetIfGain(&conf->row5, 0xf);

    conf->row6.tripler_bias = 0b10111111;
    conf->row7.tripler_bias = 0b011011;
    //TODO
    conf->row7.fm_pwrdn = 0b0;
    conf->row7.bbamp_selfm = 0b0;
 
    // Controls the Q of the IF filter in the IF variable gain amplifier; ROW8[2:0] = 000 for the
    // highest Q and the highest gain.
    conf->row8.ifvga_q_cntrl = 0b000;
    //11 is the lowest gain
    conf->row8.lna_gain = 0b11;
    //100 for normal operation. 
    conf->row8.lna_bias = 0b100;

    //Enable separate power down for the IF mixer I/Q 0 for normal operation. 
    conf->row9.en_Sep_ifmix_pwrdn_q = 0b0;
    //Active high to enable the temperature sensor. 
    conf->row9.en_tempFlash = 0b1;
    //Active high to power down the temperature sensor. 
    conf->row9.enbar_TempS = 0b0;
    //Active high enable analog gain control of the LNA. 
    conf->row9.enAnaV_LNA = 0b1;

    conf->row16.enbar_synthBG = 0b0;
    conf->row16.en_synth_LDO = SET_EN(!isExternalLo);
    conf->row16.en_cp = SET_EN(!isExternalLo);
    conf->row16.en_cpTRIST = 0b0;
    conf->row16.en_cp_dump = SET_EN(!isExternalLo);
    conf->row16.en_cpCMFB = SET_EN(!isExternalLo);
    conf->row16.en_cpShort = 0b0;
    conf->row16.byp_synth_LDO = 0b0;

    conf->row17.en_FBDiv = SET_EN(!isExternalLo);
    conf->row17.en_FBDiv_cml2cmos = SET_EN(!isExternalLo);
    conf->row17.en_stick_div = 0b0;
    conf->row17.en_refBuf = SET_EN(!isExternalLo);
    //Enables dc coupling for reference clock buffer
    conf->row17.en_reBuf_DC = 0b1;
    conf->row17.en_vtune_flash = SET_EN(!isExternalLo);
    conf->row17.en_test_divOut = 0b0;
    conf->row17.en_lockd_clk = SET_EN(!isExternalLo);

    conf->row18.enbar_vcoGB = 0b0;
    conf->row18.en_vco_reg = SET_EN(!isExternalLo);
    conf->row18.en_vco = SET_EN(!isExternalLo);
    conf->row18.en_vcoPk = 0b0;
    conf->row18.en_extLO = SET_EN(isExternalLo);
    conf->row18.byp_vco_LDO = 0b0;
    //Active high to enable 250 MHz channel step size. 
    conf->row18.en_nb250m = 0b0;

    conf->row19.muxRef = 0b0;
    conf->row19.refsel_synthBG = 0b1;

    //conf->row20.Fbdiv_code = 0b0;

    conf->row21.vco_biasTrim = 0b0010;
    conf->row21.refsel_vcoBG = 0b1;

    //conf->row22.vco_bandSel = 0;

    conf->row23.vco_offset = 0b00010;
    conf->row23.ICP_BiasTrim = 0b011;
}

static void _hmc6301_write_config(row_t rows[ROWS_NUM], hmc6301_reg_file_t *conf)
{
    ROW0_SETALL(rows, &conf->row0);
    ROW1_SETALL(rows, &conf->row1);
    ROW2_SETALL(rows, &conf->row2);
    ROW3_SETALL(rows, &conf->row3);
    ROW4_SETALL(rows, &conf->row4);
    ROW5_SETALL(rows, &conf->row5);
    ROW6_SETALL(rows, &conf->row6);
    ROW7_SETALL(rows, &conf->row7);
    ROW8_SETALL(rows, &conf->row8);
    ROW9_SETALL(rows, &conf->row9);
    ROW16_SETALL(rows, &conf->row16);
    ROW17_SETALL(rows, &conf->row17);
    ROW18_SETALL(rows, &conf->row18);
    ROW19_SETALL(rows, &conf->row19);
    ROW20_SETALL(rows, &conf->row20);
    ROW21_SETALL(rows, &conf->row21);
    ROW22_SETALL(rows, &conf->row22);
    ROW23_SETALL(rows, &conf->row23);
}

/* === API === */

void hmc6301_def_init (XGpio_t *gpio, u8 ic, u32 freq, u8 isExternalLo)
{
    row_t rows[ROWS_NUM] = {0};
    u8 i;

    _hmc6301_init_config(&confPerIc[ic], isExternalLo);
    if (!isExternalLo) {
        _hmc6301_setFreq(&confPerIc[ic].row20, &confPerIc[ic].row22, freq);
    }
    _hmc6301_write_config(rows, &confPerIc[ic]);

    for (i = 0; i < ROWS_NUM; i++) {
        if (rows[i].isSet) {
            hmc6301_spi_write(gpio, ic, i, rows[i].data);
        }
    }
}

static void hmc6301_dump_regs_r(XGpio_t *gpio, u8 ic)
{
    u8 rows[ROWS_NUM];
    u8 i;

    xil_printf("Rows dump : \r\n");
    for (i = 0; i < ROWS_NUM; i++) {
        hmc6301_spi_read(gpio, ic, i, &rows[i]);
    }
    ROW1_DUMPALL(rows);
    ROW2_DUMPALL(rows);
    ROW3_DUMPALL(rows);
    ROW4_DUMPALL(rows);
    ROW5_DUMPALL(rows);
    ROW6_DUMPALL(rows);
    ROW7_DUMPALL(rows);
    ROW8_DUMPALL(rows);
    ROW9_DUMPALL(rows);
    ROW16_DUMPALL(rows);
    ROW17_DUMPALL(rows);
    ROW18_DUMPALL(rows);
    ROW19_DUMPALL(rows);
    ROW20_DUMPALL(rows);
    ROW21_DUMPALL(rows);
    ROW22_DUMPALL(rows);
    ROW23_DUMPALL(rows);
}

void hmc6301_print_status (XGpio_t *gpio, u8 ic)
{
    u8 row;
    u8 center, up, dn, lockdet;
    u8 tempS;

    hmc6301_spi_read(gpio, ic, 24, &row);

    center = ROW_GET(row, 24, center);
    up = ROW_GET(row, 24, up);
    dn = ROW_GET(row, 24, dn);
    lockdet = ROW_GET(row, 24, lockdet);

    hmc6301_spi_read(gpio, ic, 27, &row);
    tempS = ROW_GET(row, 27, tempS);

    xil_printf("=== HMC6300 Status ===\r\n");
    xil_printf("center=%d, up=%d, dn=%d, lockdet=%d\r\n", center, up, dn, lockdet);
    xil_printf("tempS=%d\r\n", tempS);

    hmc6301_dump_regs_r(gpio, ic);
}

void hmc6301_powerup(XGpio_t *gpio, u8 ic, u8 powerup)
{
    row_t rows[ROWS_NUM] = {0};

    _hmc6301_powerup(&confPerIc[ic].row0, &confPerIc[ic].row1, powerup);

    hmc6301_write_row(gpio, ic, 0);
    hmc6301_write_row(gpio, ic, 1);
}

void hmc6301_writeArray(XGpio_t *gpio, u8 ic, u8 array, u8 data)
{
    hmc6301_spi_write(gpio, ic, array, data);
}

static const u8 * hmc6301_exp_configs[] =
{
    hmc6301_60G_conf_data,
};

static const u8 hmc6301_exp_configs_len[] =
{
    hmc6301_60G_CONF_DATA_LEN,
};

void hmc6301_exp_init(XGpio_t *gpio, u8 ic, u8 conf)
{
    u8 i;
    for (i = 0; i < hmc6301_exp_configs_len[conf]; i++) {
        hmc6301_spi_write(gpio, ic, i, hmc6301_exp_configs[conf][i]);
    }
}

void hmc6301_set_reset(XGpio_t *gpio)
{
    hmc6301_reset(gpio, 1);
    usleep(1000);
    hmc6301_reset(gpio, 0);
}

void hmc6301_dump_reg(XGpio_t *gpio, u8 ic, u8 array)
{
    u8 row;
    hmc6301_spi_read(gpio, ic, array, &row);
    xil_printf("row[%d] = 0x%0x\r\n", array, row);
}

void hmc6301_dump_regs(XGpio_t *gpio, u8 ic)
{
    u8 i;

    xil_printf("6301 dump regs\r\n");
    for (i = 0; i < ROWS_NUM; i++) {
        hmc6301_dump_reg(gpio, ic, i);
    }
}

int hmc6301_attenuation(XGpio_t *gpio, u8 ic, u8 atti, u8 attq, u8 att2)
{
    row_t rows[ROWS_NUM] = {0};
    hmc6301_reg_file_t *conf = &confPerIc[ic];

    if (_hmc6301_attenuation(&conf->row2, atti, attq, att2)) {
        return -1;
    }

    hmc6301_write_row(gpio, ic, 2);
    return 0;
}

int hmc6301_SetIfGain (XGpio_t *gpio, u8 ic, u8 steps_1_3dB)
{
    row_t rows[ROWS_NUM] = {0};
    hmc6301_reg_file_t *conf = &confPerIc[ic];

    conf->row5.rfmix_tune = 0b1111;

    if (_hmc6301_SetIfGain(&conf->row5, steps_1_3dB)) {
        return -1;
    }

    hmc6301_write_row(gpio, ic, 5);
    return 0;
}

static void _hmc6301_read_regs(XGpio_t *gpio, u8 *rows, u8 ic)
{
    u8 i;

    for (i = 0; i < ROWS_NUM; i++) {
        hmc6301_spi_read(gpio, ic, i, &rows[i]);
    }
}

int hmc6301_check_def_config(XGpio_t *gpio, u8 ic)
{
    hmc6301_reg_file_t conf = {0};
    u8 rows_r[ROWS_NUM] = {0};
    row_t rows[ROWS_NUM] = {0};
    u8 i;

    _hmc6301_init_config(&conf, FALSE);
    _hmc6301_write_config(rows, &conf);
    _hmc6301_read_regs(gpio, rows_r, ic);

    for (i = 0; i < ROWS_NUM; i++) {

        if (i == 16 || i == 17 || i == 18) {
            continue;
        }        
        if (!rows[i].isSet) {
            continue;
        }
        if (rows_r[i] != rows[i].data) {
            return i+1;
        }
    }

    return 0;
}

void hmc6301_rmw (XGpio_t *gpio, u8 ic, u32 i, u32 val, u32 mask)
{
    u8 row;

    hmc6301_spi_read(gpio, ic, i, &row);
    row = (row & mask) | (val);
    hmc6301_spi_write(gpio, ic, 7, row);
}

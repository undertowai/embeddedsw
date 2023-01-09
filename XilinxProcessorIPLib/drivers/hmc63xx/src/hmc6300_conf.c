
#include "hmc6300_reg_file.h"
#include "hmc63xx_chan.h"
#include "spi.h"

#include "../configs/hmc6300_60G_conf.h"

#define NUM_ICS (8)

#define CHIP_ADDR (0b110)

#define hmc6300_spi_write(gpio, ic, array, data) hmc63xx_spi_write(gpio, 1, ic, CHIP_ADDR, array, data)
#define hmc6300_spi_read(gpio, ic, addr, row)    hmc63xx_spi_read(gpio, 1, ic, CHIP_ADDR, addr, row)
#define hmc6300_reset(gpio, v) hmc63xx_reset(gpio, 1, v)

#define hmc6300_write_row(gpio, ic, i) \
do { \
    ROW ## i ## _SETALL(rows, &confPerIc[ic].row ## i); \
    hmc6300_spi_write(gpio, ic, i, rows[i].data); \
} while(0)

static hmc6300_reg_file_t confPerIc[NUM_ICS] = {0};

static void _hmc6300_powerup(hmc6300_row4_t *row, u8 powerup)
{
    u8 powerdown = powerup ? 0b0 : 0b1;

    row->divider_pwrdn = powerdown;
    row->driver_pwrdn = powerdown;
    row->if_upmixer_pwrdn = powerdown;
    row->ifvga_pwrdn = powerdown;
    row->pa_pwrdn = powerdown;
    row->rfvga_pwrdn = powerdown;
    row->tripler_pwrdn = powerdown;
    row->upmixer_pwrdn = powerdown;
}

static int _hmc6300_SetIfGain (hmc6300_row7_t *row, u8 steps_1_3dB)
{
    const u8 maxGain = 0xD;
    u8 dB_2_val = maxGain - steps_1_3dB;
    
    if (steps_1_3dB > maxGain) {
        xil_printf("_hmc6300_SetIfGain: Invalid parameter: steps_1_3dB=%d\n\r", steps_1_3dB);
        return -1;
    }
    row->ifvga_vga_adj = dB_2_val;
    return 0;
}

static int _hmc6300_RFVGAgain (hmc6300_row11_t *row, u8 steps_1_3dB)
{
    const u8 maxGain = 0xF;
    u8 dB_2_val = maxGain - steps_1_3dB;

    if (steps_1_3dB > maxGain) {
        xil_printf("_hmc6300_RFVGAgain: Invalid parameter: steps_1_3dB=%d\n\r", steps_1_3dB);
        return -1;
    }
    row->RFVGAgain = dB_2_val;
    return 0;
}

static void _hmc6300_setFreq(hmc6300_row20_t *row20, hmc6300_row22_t *row22, u32 freq)
{
    hmc63xx_Channel_t *channel = hmc63xx_GetChannel(freq);
    if (channel) {
        row20->Fbdiv_code = channel->Fbdiv_Code;
        row22->vco_bandSel = channel->vco_bandSel;
    } else {
        xil_printf("_hmc6301_setFreq: Invalid Freq\r\n");
    }
}

static void _hmc6300_init_config (hmc6300_reg_file_t *conf, u8 isExternalLo)
{
    conf->row1.pa_sel_vref = 0b010;
    conf->row1.pa_sel_vgbs = 0b1100;
    conf->row1.ifvga_q_cntrl = 0b1;

    conf->row2.pa_sel_alc_dac = 0b1111;
    conf->row2.pa_sep_pa_pwrdn_fast = 0b0;
    conf->row2.pa_pwrdwn_fast = 0b0;
    /*  active high for Tx single-ended output. */
    conf->row2.pa_se_sel = 0b0;
    conf->row2.power_det_pwrdn = 0b1;

    conf->row3.driver_bias = 0b111;
    conf->row3.driver_bias2 = 0b101;
    conf->row3.en_ifmix_HiCG = 0b1;
    conf->row3.en_tempflash = 0b1;

    _hmc6300_powerup(&conf->row4, TRUE);

    conf->row5.tripler_bias = 0xbf;

    conf->row6.tripler_bias = 0x3b;

    conf->row7.ifvga_tune = ROW7_ifvga_tune_DEF;
    _hmc6300_SetIfGain(&conf->row7, 0x3);

    conf->row8.if_upmixer_tune = 0b1111;
    conf->row8.ifvga_bias = 0b1000;

    /* Controls the Q of the IF filter in the baseband to IF upmixer. */
    conf->row9.ifvga_q_cntrl = 0b111;

    conf->row10.enable_FM = 0b0;
    conf->row10.if_refsel = 0b1;
    conf->row10.bg_monitor = 0b0;
    conf->row10.enDig_IFVGA_Gain_Control = 0b0;
    conf->row10.ipc_pwrdn = 0b0;
    conf->row10.if_bgmux_pwrdn = 0b0;
    conf->row10.upmix_cal_pwrdn = 0b1;
    conf->row10.TempSensor_pwrdn = 0b0;

    conf->row11.enRFVGA_Ana = 0b0;
    conf->row11.RFVGA_ICtrl = ROW11_RFVGA_ICtrl_DEf;
    _hmc6300_RFVGAgain(&conf->row11, 0xf);

    conf->row12.upmix_cal = 0x0;

    conf->row16.byp_synth_LDO = 0b1;
    conf->row16.en_cpShort = 0b1;
    conf->row16.en_cpCMFB = SET_EN(!isExternalLo);
    conf->row16.en_cp_dump = SET_EN(!isExternalLo);
    conf->row16.en_cpTRIST = 0b0;
    conf->row16.en_cp = SET_EN(!isExternalLo);
    conf->row16.en_synth_LDO = SET_EN(!isExternalLo);
    conf->row16.enbar_synthBG = 0b0;

    conf->row17.en_lockd_clk = SET_EN(!isExternalLo);
    conf->row17.en_test_divOut = 0b0;
    conf->row17.en_vtune_flash = SET_EN(!isExternalLo);
    conf->row17.en_reBuf_DC = 0b0;
    conf->row17.en_refBuf = SET_EN(!isExternalLo);
    conf->row17.en_stick_div = 0b0;
    conf->row17.en_FBDiv_cml2cmos = SET_EN(!isExternalLo);
    conf->row17.en_FBDiv = SET_EN(!isExternalLo);

    conf->row18.en_nb250m = 0b1;
    conf->row18.byp_vco_LDO = 0b0;
    conf->row18.en_extLO = SET_EN(isExternalLo);
    conf->row18.en_vcoPk = 0b0;
    conf->row18.en_vco = SET_EN(!isExternalLo);
    conf->row18.en_vco_reg = SET_EN(!isExternalLo);
    conf->row18.enbar_vcoGB = 0b0;

    conf->row19.refsel_synthBG = 0b1;
    conf->row19.muxRef = 0b0;

    conf->row20.Fbdiv_code = 0;

    conf->row21.vco_biasTrim = 0b0010;
    conf->row21.refsel_vcoBG = 0b1;

    conf->row22.vco_bandSel = 0;

    conf->row23.ICP_BiasTrim = 0b011;
    conf->row23.vco_offset = 0b00010;
}

static void _hmc6300_write_config(row_t rows[ROWS_NUM], hmc6300_reg_file_t *conf)
{
    ROW1_SETALL(rows, &conf->row1);
    ROW2_SETALL(rows, &conf->row2);
    ROW3_SETALL(rows, &conf->row3);
    ROW4_SETALL(rows, &conf->row4);
    ROW5_SETALL(rows, &conf->row5);
    ROW6_SETALL(rows, &conf->row6);
    ROW7_SETALL(rows, &conf->row7);
    ROW8_SETALL(rows, &conf->row8);
    ROW9_SETALL(rows, &conf->row9);
    ROW10_SETALL(rows, &conf->row10);
    ROW11_SETALL(rows, &conf->row11);
    ROW12_SETALL(rows, &conf->row12);
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

void hmc6300_def_init (XGpio_t *gpio, u8 ic, u32 freq, u8 isExternalLo)
{
    row_t rows[ROWS_NUM] = {0};
    u8 i;

    _hmc6300_init_config(&confPerIc[ic], isExternalLo);
    if (!isExternalLo) {
        _hmc6300_setFreq(&confPerIc[ic].row20, &confPerIc[ic].row22, freq);
    }
    _hmc6300_write_config(rows, &confPerIc[ic]);

    for (i = 0; i < ROWS_NUM; i++) {
        if (rows[i].isSet) {
            hmc6300_spi_write(gpio, ic, i, rows[i].data);
        }
    }
}

static void hmc6300_dump_regs_r(XGpio_t *gpio, u8 ic)
{
    u8 rows[ROWS_NUM];
    u8 i;

    xil_printf("Rows dump : \r\n");
    for (i = 0; i < ROWS_NUM; i++) {
        hmc6300_spi_read(gpio, ic, i, &rows[i]);
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
    ROW10_DUMPALL(rows);
    ROW11_DUMPALL(rows);
    ROW12_DUMPALL(rows);
    ROW16_DUMPALL(rows);
    ROW17_DUMPALL(rows);
    ROW18_DUMPALL(rows);
    ROW19_DUMPALL(rows);
    ROW20_DUMPALL(rows);
    ROW21_DUMPALL(rows);
    ROW22_DUMPALL(rows);
    ROW23_DUMPALL(rows);
}

void hmc6300_print_status (XGpio_t *gpio, u8 ic)
{
    u8 row;
    u8 center, up, dn, lockdet;
    u8 tempS;

    hmc6300_spi_read(gpio, ic, 24, &row);

    center = ROW_GET(row, 24, center);
    up = ROW_GET(row, 24, up);
    dn = ROW_GET(row, 24, dn);
    lockdet = ROW_GET(row, 24, lockdet);

    hmc6300_spi_read(gpio, ic, 27, &row);
    tempS = ROW_GET(row, 27, tempS);

    xil_printf("=== HMC6300 Status ===\r\n");
    xil_printf("center=%d, up=%d, dn=%d, lockdet=%d\r\n", center, up, dn, lockdet);
    xil_printf("tempS=%d\r\n", tempS);
    hmc6300_dump_regs_r(gpio, ic);
}

void hmc6300_powerup(XGpio_t *gpio, u8 ic, u8 powerup)
{
    row_t rows[ROWS_NUM] = {0};

    _hmc6300_powerup(&confPerIc[ic].row4, powerup);

    hmc6300_write_row(gpio, ic, 4);
}

void hmc6300_enableFM(XGpio_t *gpio, u8 ic, u8 enable)
{
    row_t rows[ROWS_NUM] = {0};

    confPerIc[ic].row10.enable_FM = enable;

    hmc6300_write_row(gpio, ic, 10);
}

int hmc6300_SetIfGain (XGpio_t *gpio, u8 ic, u8 steps_1_3dB)
{
    u8 row;
    row_t rows[ROWS_NUM] = {0};

    confPerIc[ic].row7.ifvga_tune = ROW7_ifvga_tune_DEF;
    if (_hmc6300_SetIfGain(&confPerIc[ic].row7, steps_1_3dB)) {
        return -1;
    }

    hmc6300_write_row(gpio, ic, 7);

    hmc6300_spi_read(gpio, ic, 7, &row);
    if (row != rows[7].data) {
        return -1;
    }
    return 0;
}

int hmc6300_RFVGAgain (XGpio_t *gpio, u8 ic, u8 steps_1_3dB)
{
    u8 row;
    row_t rows[ROWS_NUM] = {0};
    hmc6300_reg_file_t *conf = &confPerIc[ic];

    conf->row11.RFVGA_ICtrl = ROW11_RFVGA_ICtrl_DEf;
    conf->row11.enRFVGA_Ana = 0b0;
    if (_hmc6300_RFVGAgain(&conf->row11, steps_1_3dB)) {
        return -1;
    }

    //printf("Setting hmc6300 row 11 to %02x requested %d\n", conf->row11.RFVGAgain << 4 , steps_1_3dB);
    hmc6300_write_row(gpio, ic, 11);

    hmc6300_spi_read(gpio, ic, 11, &row);
    if (row != rows[11].data) {
        return -1;
    }
    return 0;
}

void hmc6300_writeArray(XGpio_t *gpio, u8 ic, u8 array, u8 data)
{
    hmc6300_spi_write(gpio, ic, array, data);
}

static const u8 * hmc6300_exp_configs[] =
{
    hmc6300_60G_conf_data,
};

static const u8 hmc6300_exp_configs_len[] =
{
    hmc6300_60G_CONF_DATA_LEN,
};

void hmc6300_exp_init(XGpio_t *gpio, u8 ic, u8 conf)
{
    u8 i;
    for (i = 0; i < hmc6300_exp_configs_len[conf]; i++) {
        hmc6300_spi_write(gpio, ic, i, hmc6300_exp_configs[conf][i]);
    }
}

void hmc6300_set_reset(XGpio_t *gpio)
{
    hmc6300_reset(gpio, 1);
    usleep(1000);
    hmc6300_reset(gpio, 0);
}

void hmc6300_dump_reg(XGpio_t *gpio, u8 ic, u8 array)
{
    u8 row;
    hmc6300_spi_read(gpio, ic, array, &row);
    xil_printf("row[%d] = 0x%0x\r\n", array, row);
}

void hmc6300_dump_regs(XGpio_t *gpio, u8 ic)
{
    u8 i;

    xil_printf("6300 [%d] dump regs\r\n", ic);
    for (i = 0; i < ROWS_NUM; i++) {
        hmc6300_dump_reg(gpio, ic, i);
    }
}

static void _hmc6300_read_regs(XGpio_t *gpio, u8 *rows, u8 ic)
{
    u8 i;

    for (i = 0; i < ROWS_NUM; i++) {
        hmc6300_spi_read(gpio, ic, i, &rows[i]);
    }
}

int hmc6300_check_def_config(XGpio_t *gpio, u8 ic)
{
    hmc6300_reg_file_t conf = {0};
    u8 rows_r[ROWS_NUM] = {0};
    row_t rows[ROWS_NUM] = {0};
    u8 i;

    _hmc6300_init_config(&conf, FALSE);
    _hmc6300_write_config(rows, &conf);
    _hmc6300_read_regs(gpio, rows_r, ic);

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

int hmc6300_rmw (XGpio_t *gpio, u8 ic, u32 i, u32 val, u32 mask)
{
    u8 row, row_prev;

    hmc6300_spi_read(gpio, ic, i, &row);
    row_prev = row;
    if (mask == 0xff && val == 0x0) {
        return row_prev;
    }
    row = (row & mask) | (val);
    hmc6300_spi_write(gpio, ic, i, row);

    return row_prev;
}

#ifndef HMC6300_REG_FILE_H
#define HMC6300_REG_FILE_H

#include "hmc63xx_reg.h"

//ROW0 not used
typedef struct {
    u8 unused;
} hmc6300_row0_t;


/* ============ ROW1 ============ */
typedef struct {
    /*
    Controls the bias current for the power amplifier output transistors
    ROW1, Bits[2:0] = 010 for normal operation. 
    */
    u8 pa_sel_vref;
    /*
    Controls the regulator for the base voltage of the power amplifier output transistors.
    ROW1, Bits[7:3] = 1100 for normal operation. 
    */
    u8 ifvga_q_cntrl;
    u8 pa_sel_vgbs;
} hmc6300_row1_t;

#define ROW1_pa_sel_vref_MS (0b111)
#define ROW1_pa_sel_vref_OF (0)
#define ROW1_pa_sel_vref_DEF (0b010)

#define ROW1_ifvga_q_cntrl_MS (0b1)
#define ROW1_ifvga_q_cntrl_OF (3)

#define ROW1_pa_sel_vgbs_MS (0b1111)
#define ROW1_pa_sel_vgbs_OF (4)
#define ROW1_pa_sel_vgbs_DEF (0b1100)

#define ROW1_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 1, pa_sel_vref, conf); \
    ROW_SET(rows, 1, ifvga_q_cntrl, conf); \
    ROW_SET(rows, 1, pa_sel_vgbs, conf); \
} while(0)

#define ROW1_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 1, pa_sel_vref); \
    ROW_DUMP(rows, 1, ifvga_q_cntrl); \
    ROW_DUMP(rows, 1, pa_sel_vgbs    ); \
} while(0)

/* ============ ROW2 ============ */
typedef struct {
    //Active low to enable Tx power detector.
    u8 power_det_pwrdn;
    /*
    Control for Tx output interface; active low for differential Tx output; active high for Tx single-ended output.
    */
    u8 pa_se_sel;
    //Active high for normal operation.
    u8 pa_pwrdwn_fast;
    //Active high for normal operation.
    u8 pa_sep_pa_pwrdn_fast;
    /*
    Factory diagnostics; ROW2.
    Bits[7:4] = 1111 for normal operation.
    */
    u8 pa_sel_alc_dac;
} hmc6300_row2_t;

#define ROW2_power_det_pwrdn_MS (0b1)
#define ROW2_power_det_pwrdn_OF (0)

#define ROW2_pa_se_sel_MS (0b1)
#define ROW2_pa_se_sel_OF (1)

#define ROW2_pa_pwrdwn_fast_MS (0b1)
#define ROW2_pa_pwrdwn_fast_OF (2)

#define ROW2_pa_sep_pa_pwrdn_fast_MS (0b1)
#define ROW2_pa_sep_pa_pwrdn_fast_OF (3)

#define ROW2_pa_sel_alc_dac_MS (0b1111)
#define ROW2_pa_sel_alc_dac_OF (4)
#define ROW2_pa_sel_alc_dac_DEF (0b1111)

#define ROW2_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 2, power_det_pwrdn, conf); \
    ROW_SET(rows, 2, pa_se_sel, conf); \
    ROW_SET(rows, 2, pa_pwrdwn_fast, conf); \
    ROW_SET(rows, 2, pa_sep_pa_pwrdn_fast, conf); \
    ROW_SET(rows, 2, pa_sel_alc_dac, conf); \
} while(0)

#define ROW2_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 2, power_det_pwrdn); \
    ROW_DUMP(rows, 2, pa_se_sel); \
    ROW_DUMP(rows, 2, pa_pwrdwn_fast); \
    ROW_DUMP(rows, 2, pa_sep_pa_pwrdn_fast); \
    ROW_DUMP(rows, 2, pa_sel_alc_dac); \
} while(0)

/* ============ ROW3 ============ */
typedef struct {
    u8 en_tempflash;
    u8 en_ifmix_HiCG;
    u8 driver_bias2;
    u8 driver_bias;
} hmc6300_row3_t;

#define ROW3_en_tempflash_MS (0b1)
#define ROW3_en_tempflash_OF (0)

#define ROW3_en_ifmix_HiCG_MS (0b1)
#define ROW3_en_ifmix_HiCG_OF (1)

#define ROW3_driver_bias2_MS (0b111)
#define ROW3_driver_bias2_OF (2)
#define ROW3_driver_bias2_DEF (0b101)

#define ROW3_driver_bias_MS (0b111)
#define ROW3_driver_bias_OF (5)
#define ROW3_driver_bias_DEF (0b111)

#define ROW3_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 3, en_tempflash, conf); \
    ROW_SET(rows, 3, en_ifmix_HiCG, conf); \
    ROW_SET(rows, 3, driver_bias2, conf); \
    ROW_SET(rows, 3, driver_bias, conf); \
} while(0)

#define ROW3_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 3, en_tempflash); \
    ROW_DUMP(rows, 3, en_ifmix_HiCG); \
    ROW_DUMP(rows, 3, driver_bias2); \
    ROW_DUMP(rows, 3, driver_bias); \
} while(0)

/* ============ ROW4 ============ */
typedef struct {
    u8 if_upmixer_pwrdn;
    u8 tripler_pwrdn;
    u8 rfvga_pwrdn;
    u8 pa_pwrdn;
    u8 divider_pwrdn;
    u8 ifvga_pwrdn;
    u8 upmixer_pwrdn;
    u8 driver_pwrdn;
} hmc6300_row4_t;

#define ROW4_if_upmixer_pwrdn_MS (0b1)
#define ROW4_if_upmixer_pwrdn_OF (0)

#define ROW4_tripler_pwrdn_MS (0b1)
#define ROW4_tripler_pwrdn_OF (1)

#define ROW4_rfvga_pwrdn_MS (0b1)
#define ROW4_rfvga_pwrdn_OF (2)

#define ROW4_pa_pwrdn_MS (0b1)
#define ROW4_pa_pwrdn_OF (3)

#define ROW4_divider_pwrdn_MS (0b1)
#define ROW4_divider_pwrdn_OF (4)

#define ROW4_ifvga_pwrdn_MS (0b1)
#define ROW4_ifvga_pwrdn_OF (5)

#define ROW4_upmixer_pwrdn_MS (0b1)
#define ROW4_upmixer_pwrdn_OF (6)

#define ROW4_driver_pwrdn_MS (0b1)
#define ROW4_driver_pwrdn_OF (7)

#define ROW4_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 4, if_upmixer_pwrdn, conf); \
    ROW_SET(rows, 4, tripler_pwrdn, conf); \
    ROW_SET(rows, 4, rfvga_pwrdn, conf); \
    ROW_SET(rows, 4, pa_pwrdn, conf); \
    ROW_SET(rows, 4, divider_pwrdn, conf); \
    ROW_SET(rows, 4, ifvga_pwrdn, conf); \
    ROW_SET(rows, 4, upmixer_pwrdn, conf); \
    ROW_SET(rows, 4, driver_pwrdn, conf); \
} while(0)

#define ROW4_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 4, if_upmixer_pwrdn); \
    ROW_DUMP(rows, 4, tripler_pwrdn); \
    ROW_DUMP(rows, 4, rfvga_pwrdn); \
    ROW_DUMP(rows, 4, pa_pwrdn); \
    ROW_DUMP(rows, 4, divider_pwrdn); \
    ROW_DUMP(rows, 4, ifvga_pwrdn); \
    ROW_DUMP(rows, 4, upmixer_pwrdn); \
    ROW_DUMP(rows, 4, driver_pwrdn); \
} while(0)

/* ============ ROW5 ============ */
typedef struct {
    u8 tripler_bias;
} hmc6300_row5_t;

#define ROW5_tripler_bias_MS (0b11111111)
#define ROW5_tripler_bias_OF (0)
#define ROW5_tripler_bias_DEF (0b11111111)

#define ROW5_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 5, tripler_bias, conf); \
} while(0)

#define ROW5_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 5, tripler_bias); \
} while(0)

/* ============ ROW6 ============ */
typedef struct {
    u8 tripler_bias;
} hmc6300_row6_t;

#define ROW6_tripler_bias_MS (0b111111)
#define ROW6_tripler_bias_OF (2)
#define ROW6_tripler_bias_DEF (0b111011)

#define ROW6_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 6, tripler_bias, conf); \
} while(0)

#define ROW6_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 6, tripler_bias); \
} while(0)

/* ============ ROW7 ============ */
typedef struct {
    u8 ifvga_vga_adj;
    u8 ifvga_tune;
} hmc6300_row7_t;

#define ROW7_ifvga_tune_MS (0b1111)
#define ROW7_ifvga_tune_OF (0)
#define ROW7_ifvga_tune_DEF (0b1111)

#define ROW7_ifvga_vga_adj_MS (0b1111)
#define ROW7_ifvga_vga_adj_OF (4)

#define ROW7_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 7, ifvga_vga_adj, conf); \
    ROW_SET(rows, 7, ifvga_tune, conf); \
} while(0)

#define ROW7_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 7, ifvga_vga_adj); \
    ROW_DUMP(rows, 7, ifvga_tune); \
} while(0)

/* ============ ROW8 ============ */
typedef struct {
    u8 if_upmixer_tune;
    u8 ifvga_bias;
} hmc6300_row8_t;

#define ROW8_if_upmixer_tune_MS (0b1111)
#define ROW8_if_upmixer_tune_OF (0)
#define ROW8_if_upmixer_tune_DEF (0b1111)

#define ROW8_ifvga_bias_MS (0b1111)
#define ROW8_ifvga_bias_OF (4)
#define ROW8_ifvga_bias_DEF (0b1000)

#define ROW8_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 8, if_upmixer_tune, conf); \
    ROW_SET(rows, 8, ifvga_bias, conf); \
} while(0)

#define ROW8_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 8, if_upmixer_tune); \
    ROW_DUMP(rows, 8, ifvga_bias); \
} while(0)

/* ============ ROW9 ============ */
typedef struct {
    u8 ifvga_q_cntrl;
} hmc6300_row9_t;

#define ROW9_ifvga_q_cntrl_MS (0b111)
#define ROW9_ifvga_q_cntrl_OF (5)

#define ROW9_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 9, ifvga_q_cntrl, conf); \
} while(0)

#define ROW9_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 9, ifvga_q_cntrl); \
} while(0)

/* ============ ROW10 ============ */
typedef struct {
    u8 TempSensor_pwrdn;
    u8 upmix_cal_pwrdn;
    u8 if_bgmux_pwrdn;
    u8 ipc_pwrdn;
    u8 enDig_IFVGA_Gain_Control;
    u8 bg_monitor;
    u8 if_refsel;
    u8 enable_FM;
} hmc6300_row10_t;

#define ROW10_TempSensor_pwrdn_MS (0b1)
#define ROW10_TempSensor_pwrdn_OF (0)

#define ROW10_upmix_cal_pwrdn_MS (0b1)
#define ROW10_upmix_cal_pwrdn_OF (1)

#define ROW10_if_bgmux_pwrdn_MS (0b1)
#define ROW10_if_bgmux_pwrdn_OF (2)

#define ROW10_ipc_pwrdn_MS (0b1)
#define ROW10_ipc_pwrdn_OF (3)

#define ROW10_enDig_IFVGA_Gain_Control_MS (0b1)
#define ROW10_enDig_IFVGA_Gain_Control_OF (4)

#define ROW10_bg_monitor_MS (0b1)
#define ROW10_bg_monitor_OF (5)

#define ROW10_if_refsel_MS (0b1)
#define ROW10_if_refsel_OF (6)

#define ROW10_enable_FM_MS (0b1)
#define ROW10_enable_FM_OF (7)

#define ROW10_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 10, TempSensor_pwrdn, conf); \
    ROW_SET(rows, 10, upmix_cal_pwrdn, conf); \
    ROW_SET(rows, 10, if_bgmux_pwrdn, conf); \
    ROW_SET(rows, 10, ipc_pwrdn, conf); \
    ROW_SET(rows, 10, enDig_IFVGA_Gain_Control, conf); \
    ROW_SET(rows, 10, bg_monitor, conf); \
    ROW_SET(rows, 10, if_refsel, conf); \
    ROW_SET(rows, 10, enable_FM, conf); \
} while(0)

#define ROW10_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 10, TempSensor_pwrdn); \
    ROW_DUMP(rows, 10, upmix_cal_pwrdn); \
    ROW_DUMP(rows, 10, if_bgmux_pwrdn); \
    ROW_DUMP(rows, 10, ipc_pwrdn); \
    ROW_DUMP(rows, 10, enDig_IFVGA_Gain_Control); \
    ROW_DUMP(rows, 10, bg_monitor); \
    ROW_DUMP(rows, 10, if_refsel); \
    ROW_DUMP(rows, 10, enable_FM); \
} while(0)

/* ============ ROW11 ============ */
typedef struct {
    u8 RFVGA_ICtrl;
    u8 enRFVGA_Ana;
    u8 RFVGAgain;
} hmc6300_row11_t;

#define ROW11_RFVGA_ICtrl_MS (0b111)
#define ROW11_RFVGA_ICtrl_OF (0)
#define ROW11_RFVGA_ICtrl_DEf (0b011)

#define ROW11_enRFVGA_Ana_MS (0b1)
#define ROW11_enRFVGA_Ana_OF (3)

#define ROW11_RFVGAgain_MS (0b1111)
#define ROW11_RFVGAgain_OF (4)

#define ROW11_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 11, RFVGA_ICtrl, conf); \
    ROW_SET(rows, 11, enRFVGA_Ana, conf); \
    ROW_SET(rows, 11, RFVGAgain, conf); \
} while(0)

#define ROW11_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 11, RFVGA_ICtrl); \
    ROW_DUMP(rows, 11, enRFVGA_Ana); \
    ROW_DUMP(rows, 11, RFVGAgain); \
} while(0)

/* ============ ROW12 ============ */
typedef struct {
    u8 upmix_cal;
} hmc6300_row12_t;

#define ROW12_upmix_cal_MS (0b11111111)
#define ROW12_upmix_cal_OF (0)

#define ROW12_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 12, upmix_cal, conf); \
} while(0)

#define ROW12_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 12, upmix_cal); \
} while(0)

/* ============ ROW13 ============ */
typedef struct {
    u8 unused;
} hmc6300_row13_t;

/* ============ ROW14 ============ */
typedef struct {
    u8 unused;
} hmc6300_row14_t;

/* ============ ROW15 ============ */
typedef struct {
    u8 unused;
} hmc6300_row15_t;

/* ============ ROW16 ============ */
typedef struct {
    u8 enbar_synthBG;
    u8 en_synth_LDO;
    u8 en_cp;
    u8 en_cpTRIST;
    u8 en_cp_dump;
    u8 en_cpCMFB;
    u8 en_cpShort;
    u8 byp_synth_LDO;
} hmc6300_row16_t;

#define ROW16_enbar_synthBG_MS (0b1)
#define ROW16_enbar_synthBG_OF (0)

#define ROW16_en_synth_LDO_MS (0b1)
#define ROW16_en_synth_LDO_OF (1)

#define ROW16_en_cp_MS (0b1)
#define ROW16_en_cp_OF (2)

#define ROW16_en_cpTRIST_MS (0b1)
#define ROW16_en_cpTRIST_OF (3)

#define ROW16_en_cp_dump_MS (0b1)
#define ROW16_en_cp_dump_OF (4)

#define ROW16_en_cpCMFB_MS (0b1)
#define ROW16_en_cpCMFB_OF (5)

#define ROW16_en_cpShort_MS (0b1)
#define ROW16_en_cpShort_OF (6)

#define ROW16_byp_synth_LDO_MS (0b1)
#define ROW16_byp_synth_LDO_OF (7)

#define ROW16_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 16, enbar_synthBG, conf); \
    ROW_SET(rows, 16, en_synth_LDO, conf); \
    ROW_SET(rows, 16, en_cp, conf); \
    ROW_SET(rows, 16, en_cpTRIST, conf); \
    ROW_SET(rows, 16, en_cp_dump, conf); \
    ROW_SET(rows, 16, en_cpCMFB, conf); \
    ROW_SET(rows, 16, en_cpShort, conf); \
    ROW_SET(rows, 16, byp_synth_LDO, conf); \
} while(0)

#define ROW16_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 16, enbar_synthBG); \
    ROW_DUMP(rows, 16, en_synth_LDO); \
    ROW_DUMP(rows, 16, en_cp); \
    ROW_DUMP(rows, 16, en_cpTRIST); \
    ROW_DUMP(rows, 16, en_cp_dump); \
    ROW_DUMP(rows, 16, en_cpCMFB); \
    ROW_DUMP(rows, 16, en_cpShort); \
    ROW_DUMP(rows, 16, byp_synth_LDO); \
} while(0)

/* ============ ROW17 ============ */
typedef struct {
    u8 en_FBDiv;
    u8 en_FBDiv_cml2cmos;
    u8 en_stick_div;
    u8 en_refBuf;
    u8 en_reBuf_DC;
    u8 en_vtune_flash;
    u8 en_test_divOut;
    u8 en_lockd_clk;
} hmc6300_row17_t;

#define ROW17_en_FBDiv_MS (0b1)
#define ROW17_en_FBDiv_OF (0)

#define ROW17_en_FBDiv_cml2cmos_MS (0b1)
#define ROW17_en_FBDiv_cml2cmos_OF (1)

#define ROW17_en_stick_div_MS (0b1)
#define ROW17_en_stick_div_OF (2)

#define ROW17_en_refBuf_MS (0b1)
#define ROW17_en_refBuf_OF (3)

#define ROW17_en_reBuf_DC_MS (0b1)
#define ROW17_en_reBuf_DC_OF (4)

#define ROW17_en_vtune_flash_MS (0b1)
#define ROW17_en_vtune_flash_OF (5)

#define ROW17_en_test_divOut_MS (0b1)
#define ROW17_en_test_divOut_OF (6)

#define ROW17_en_lockd_clk_MS (0b1)
#define ROW17_en_lockd_clk_OF (0)

#define ROW17_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 17, en_FBDiv, conf); \
    ROW_SET(rows, 17, en_FBDiv_cml2cmos, conf); \
    ROW_SET(rows, 17, en_stick_div, conf); \
    ROW_SET(rows, 17, en_refBuf, conf); \
    ROW_SET(rows, 17, en_reBuf_DC, conf); \
    ROW_SET(rows, 17, en_vtune_flash, conf); \
    ROW_SET(rows, 17, en_test_divOut, conf); \
    ROW_SET(rows, 17, en_lockd_clk, conf); \
} while(0)

#define ROW17_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 17, en_FBDiv); \
    ROW_DUMP(rows, 17, en_FBDiv_cml2cmos); \
    ROW_DUMP(rows, 17, en_stick_div); \
    ROW_DUMP(rows, 17, en_refBuf); \
    ROW_DUMP(rows, 17, en_reBuf_DC); \
    ROW_DUMP(rows, 17, en_vtune_flash); \
    ROW_DUMP(rows, 17, en_test_divOut); \
    ROW_DUMP(rows, 17, en_lockd_clk); \
} while(0)

/* ============ ROW18 ============ */
typedef struct {
    u8 enbar_vcoGB;
    u8 en_vco_reg;
    u8 en_vco;
    u8 en_vcoPk;
    u8 en_extLO;
    u8 byp_vco_LDO;
    u8 en_nb250m;
} hmc6300_row18_t;

#define ROW18_enbar_vcoGB_MS (0b1)
#define ROW18_enbar_vcoGB_OF (0)

#define ROW18_en_vco_reg_MS (0b1)
#define ROW18_en_vco_reg_OF (1)

#define ROW18_en_vco_MS (0b1)
#define ROW18_en_vco_OF (2)

#define ROW18_en_vcoPk_MS (0b1)
#define ROW18_en_vcoPk_OF (3)

#define ROW18_en_extLO_MS (0b1)
#define ROW18_en_extLO_OF (4)

#define ROW18_byp_vco_LDO_MS (0b1)
#define ROW18_byp_vco_LDO_OF (5)

#define ROW18_en_nb250m_MS (0b1)
#define ROW18_en_nb250m_OF (6)

#define ROW18_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 18, enbar_vcoGB, conf); \
    ROW_SET(rows, 18, en_vco_reg, conf); \
    ROW_SET(rows, 18, en_vco, conf); \
    ROW_SET(rows, 18, en_vcoPk, conf); \
    ROW_SET(rows, 18, en_extLO, conf); \
    ROW_SET(rows, 18, byp_vco_LDO, conf); \
    ROW_SET(rows, 18, en_nb250m, conf); \
} while(0)

#define ROW18_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 18, enbar_vcoGB); \
    ROW_DUMP(rows, 18, en_vco_reg); \
    ROW_DUMP(rows, 18, en_vco); \
    ROW_DUMP(rows, 18, en_vcoPk); \
    ROW_DUMP(rows, 18, en_extLO); \
    ROW_DUMP(rows, 18, byp_vco_LDO); \
    ROW_DUMP(rows, 18, en_nb250m); \
} while(0)

/* ============ ROW19 ============ */
typedef struct {
    u8 muxRef;
    u8 refsel_synthBG;
} hmc6300_row19_t;

#define ROW19_muxRef_MS (0b1)
#define ROW19_muxRef_OF (0)

#define ROW19_refsel_synthBG_MS (0b1)
#define ROW19_refsel_synthBG_OF (1)

#define ROW19_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 19, muxRef, conf); \
    ROW_SET(rows, 19, refsel_synthBG, conf); \
} while(0)

#define ROW19_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 19, muxRef); \
    ROW_DUMP(rows, 19, refsel_synthBG); \
} while(0)


/* ============ ROW20 ============ */
typedef struct {
    u8 Fbdiv_code;
} hmc6300_row20_t;

#define ROW20_Fbdiv_code_MS (0b1111111)
#define ROW20_Fbdiv_code_OF (0)

#define ROW20_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 20, Fbdiv_code, conf); \
} while(0)

#define ROW20_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 20, Fbdiv_code); \
} while(0)

/* ============ ROW21 ============ */
typedef struct {
    u8 vco_biasTrim;
    u8 refsel_vcoBG;
} hmc6300_row21_t;

#define ROW21_vco_biasTrim_MS (0b1111)
#define ROW21_vco_biasTrim_OF (0)

#define ROW21_refsel_vcoBG_MS (0b1)
#define ROW21_refsel_vcoBG_OF (4)

#define ROW21_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 21, vco_biasTrim, conf); \
    ROW_SET(rows, 21, refsel_vcoBG, conf); \
} while(0)

#define ROW21_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 21, vco_biasTrim); \
    ROW_DUMP(rows, 21, refsel_vcoBG); \
} while(0)

/* ============ ROW22 ============ */
typedef struct {
    u8 vco_bandSel;
} hmc6300_row22_t;

#define ROW22_vco_bandSel_MS (0b11111)
#define ROW22_vco_bandSel_OF (0)

#define ROW22_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 22, vco_bandSel, conf); \
} while(0)

#define ROW22_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 22, vco_bandSel); \
} while(0)

/* ============ ROW23 ============ */
typedef struct {
    u8 vco_offset;
    u8 ICP_BiasTrim;
} hmc6300_row23_t;

#define ROW23_vco_offset_MS (0b11111)
#define ROW23_vco_offset_OF (0)

#define ROW23_ICP_BiasTrim_MS (0b111)
#define ROW23_ICP_BiasTrim_OF (5)

#define ROW23_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 23, vco_offset, conf); \
    ROW_SET(rows, 23, ICP_BiasTrim, conf); \
} while(0)

#define ROW23_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 23, vco_offset); \
    ROW_DUMP(rows, 23, ICP_BiasTrim); \
} while(0)

/* ============ ROW24 ============ */
typedef struct {
    u8 center;
    u8 up;
    u8 dn;
    u8 lockdet;
} hmc6300_row24_t;

#define ROW24_center_MS (0b1)
#define ROW24_center_OF (0)

#define ROW24_up_MS (0b1)
#define ROW24_up_OF (1)

#define ROW24_dn_MS (0b1)
#define ROW24_dn_OF (2)

#define ROW24_lockdet_MS (0b1)
#define ROW24_lockdet_OF (3)

/* ============ ROW25 ============ */
typedef struct {
    u8 vtune_flashp;
} hmc6300_row25_t;

#define ROW25_vtune_flashp_MS (0b11111111)
#define ROW25_vtune_flashp_OF (0)

/* ============ ROW26 ============ */
typedef struct {
    u8 vtune_flashn;
} hmc6300_row26_t;

#define ROW26_vtune_flashn_MS (0b11111111)
#define ROW26_vtune_flashn_OF (0)

/* ============ ROW27 ============ */
typedef struct {
    u8 tempS;
} hmc6300_row27_t;

#define ROW27_tempS_MS (0b11111)
#define ROW27_tempS_OF (0)

typedef struct {
    hmc6300_row0_t row0;
    hmc6300_row1_t row1;
    hmc6300_row2_t row2;
    hmc6300_row3_t row3;
    hmc6300_row4_t row4;
    hmc6300_row5_t row5;
    hmc6300_row6_t row6;
    hmc6300_row7_t row7;
    hmc6300_row8_t row8;
    hmc6300_row9_t row9;
    hmc6300_row10_t row10;
    hmc6300_row11_t row11;
    hmc6300_row12_t row12;
    hmc6300_row13_t row13;
    hmc6300_row14_t row14;
    hmc6300_row15_t row15;
    hmc6300_row16_t row16;
    hmc6300_row17_t row17;
    hmc6300_row18_t row18;
    hmc6300_row19_t row19;
    hmc6300_row20_t row20;
    hmc6300_row21_t row21;
    hmc6300_row22_t row22;
    hmc6300_row23_t row23;
    hmc6300_row24_t row24;
    hmc6300_row25_t row25;
    hmc6300_row26_t row26;
    hmc6300_row27_t row27;
} hmc6300_reg_file_t;

#define ROWS_NUM (28)

#endif /* HMC6300_REG_FILE_H */

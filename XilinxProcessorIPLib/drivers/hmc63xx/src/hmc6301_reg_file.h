#ifndef HMC56301_REG_FILE_H
#define HMC56301_REG_FILE_H

#include "hmc63xx_reg.h"

/* ============ ROW0 ============ */
typedef struct {
    u8 ifvga_pwrdn;
    u8 tripler_pwrdn;
    u8 ifmixer_pwrdn;
    u8 mixer_pwrdn;
    u8 divider_pwrdn;
    u8 bbamp_pwrdn_q;
    u8 bbamp_pwrdn_i;
    u8 lna_pwrdwn;
} hmc6301_row0_t;

#define ROW0_ifvga_pwrdn_MS (0b1)
#define ROW0_ifvga_pwrdn_OF (0)

#define ROW0_tripler_pwrdn_MS (0b1)
#define ROW0_tripler_pwrdn_OF (1)

#define ROW0_ifmixer_pwrdn_MS (0b1)
#define ROW0_ifmixer_pwrdn_OF (2)

#define ROW0_mixer_pwrdn_MS (0b1)
#define ROW0_mixer_pwrdn_OF (3)

#define ROW0_divider_pwrdn_MS (0b1)
#define ROW0_divider_pwrdn_OF (4)

#define ROW0_bbamp_pwrdn_q_MS (0b1)
#define ROW0_bbamp_pwrdn_q_OF (5)

#define ROW0_bbamp_pwrdn_i_MS (0b1)
#define ROW0_bbamp_pwrdn_i_OF (6)

#define ROW0_lna_pwrdwn_MS (0b1)
#define ROW0_lna_pwrdwn_OF (7)

#define ROW0_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 0, ifvga_pwrdn, conf); \
    ROW_SET(rows, 0, tripler_pwrdn, conf); \
    ROW_SET(rows, 0, ifmixer_pwrdn, conf); \
    ROW_SET(rows, 0, mixer_pwrdn, conf); \
    ROW_SET(rows, 0, divider_pwrdn, conf); \
    ROW_SET(rows, 0, bbamp_pwrdn_q, conf); \
    ROW_SET(rows, 0, bbamp_pwrdn_i, conf); \
    ROW_SET(rows, 0, lna_pwrdwn, conf); \
} while(0)

#define ROW0_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 0, ifvga_pwrdn); \
    ROW_DUMP(rows, 0, tripler_pwrdn); \
    ROW_DUMP(rows, 0, ifmixer_pwrdn); \
    ROW_DUMP(rows, 0, mixer_pwrdn); \
    ROW_DUMP(rows, 0, divider_pwrdn); \
    ROW_DUMP(rows, 0, bbamp_pwrdn_q); \
    ROW_DUMP(rows, 0, bbamp_pwrdn_i); \
    ROW_DUMP(rows, 0, lna_pwrdwn); \
} while(0)

/* ============ ROW1 ============ */
typedef struct {
    u8 bbamp_sigshort;
    u8 bbamp_sell_ask;
    u8 bbamp_atten1;
    u8 ask_pwrdn;
    u8 if_bgmux_pwrdn;
    u8 ifmix_pwrdn_q;
    u8 ipc_pwrdwn;
} hmc6301_row1_t;

#define ROW1_bbamp_sigshort_MS (0b1)
#define ROW1_bbamp_sigshort_OF (0)

#define ROW1_bbamp_sell_ask_MS (0b1)
#define ROW1_bbamp_sell_ask_OF (1)

#define ROW1_bbamp_atten1_MS (0b11)
#define ROW1_bbamp_atten1_OF (2)

#define ROW1_ask_pwrdn_MS (0b1)
#define ROW1_ask_pwrdn_OF (4)

#define ROW1_if_bgmux_pwrdn_MS (0b1)
#define ROW1_if_bgmux_pwrdn_OF (5)

#define ROW1_ifmix_pwrdn_q_MS (0b1)
#define ROW1_ifmix_pwrdn_q_OF (6)

#define ROW1_ipc_pwrdwn_MS (0b1)
#define ROW1_ipc_pwrdwn_OF (7)

#define ROW1_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 1, bbamp_sigshort, conf); \
    ROW_SET(rows, 1, bbamp_sell_ask, conf); \
    ROW_SET(rows, 1, bbamp_atten1, conf); \
    ROW_SET(rows, 1, ask_pwrdn, conf); \
    ROW_SET(rows, 1, if_bgmux_pwrdn, conf); \
    ROW_SET(rows, 1, ifmix_pwrdn_q, conf); \
    ROW_SET(rows, 1, ipc_pwrdwn, conf); \
} while(0)

#define ROW1_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 1, bbamp_sigshort); \
    ROW_DUMP(rows, 1, bbamp_sell_ask); \
    ROW_DUMP(rows, 1, bbamp_atten1); \
    ROW_DUMP(rows, 1, ask_pwrdn); \
    ROW_DUMP(rows, 1, if_bgmux_pwrdn); \
    ROW_DUMP(rows, 1, ifmix_pwrdn_q); \
    ROW_DUMP(rows, 1, ipc_pwrdwn); \
} while(0)

/* ============ ROW2 ============ */
typedef struct {
    u8 bbamp_atten2;
    u8 bbamp_attenfq;
    u8 bbamp_attenfi;
} hmc6301_row2_t;

#define ROW2_bbamp_atten2_MS (0b11)
#define ROW2_bbamp_atten2_OF (0)

#define ROW2_bbamp_attenfq_MS (0b111)
#define ROW2_bbamp_attenfq_OF (2)

#define ROW2_bbamp_attenfi_MS (0b111)
#define ROW2_bbamp_attenfi_OF (5)

#define ROW2_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 2, bbamp_atten2, conf); \
    ROW_SET(rows, 2, bbamp_attenfq, conf); \
    ROW_SET(rows, 2, bbamp_attenfi, conf); \
} while(0)

#define ROW2_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 2, bbamp_atten2); \
    ROW_DUMP(rows, 2, bbamp_attenfq); \
    ROW_DUMP(rows, 2, bbamp_attenfi); \
} while(0)

/* ============ ROW3 ============ */
typedef struct {
    u8 lna_refsel;
    u8 if_refsel;
    u8 bg_monitor_sel;
    u8 bbamp_selfastrec;
    u8 bbamp_selbw;
} hmc6301_row3_t;

#define ROW3_lna_refsel_MS (0b1)
#define ROW3_lna_refsel_OF (0)

#define ROW3_if_refsel_MS (0b1)
#define ROW3_if_refsel_OF (1)

#define ROW3_bg_monitor_sel_MS (0b11)
#define ROW3_bg_monitor_sel_OF (2)

#define ROW3_bbamp_selfastrec_MS (0b11)
#define ROW3_bbamp_selfastrec_OF (4)

#define ROW3_bbamp_selbw_MS (0b11)
#define ROW3_bbamp_selbw_OF (6)

#define ROW3_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 3, lna_refsel, conf); \
    ROW_SET(rows, 3, if_refsel, conf); \
    ROW_SET(rows, 3, bg_monitor_sel, conf); \
    ROW_SET(rows, 3, bbamp_selfastrec, conf); \
    ROW_SET(rows, 3, bbamp_selbw, conf); \
} while(0)

#define ROW3_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 3, lna_refsel); \
    ROW_DUMP(rows, 3, if_refsel); \
    ROW_DUMP(rows, 3, bg_monitor_sel); \
    ROW_DUMP(rows, 3, bbamp_selfastrec); \
    ROW_DUMP(rows, 3, bbamp_selbw); \
} while(0)

/* ============ ROW4 ============ */
typedef struct {
    u8 enDigVGA;
    u8 ifvga_tune;
} hmc6301_row4_t;

#define ROW4_enDigVGA_MS (0b1)
#define ROW4_enDigVGA_OF (0)

#define ROW4_ifvga_tune_MS (0b1111111)
#define ROW4_ifvga_tune_OF (1)

#define ROW4_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 4, enDigVGA, conf); \
    ROW_SET(rows, 4, ifvga_tune, conf); \
} while(0)

#define ROW4_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 4, enDigVGA); \
    ROW_DUMP(rows, 4, ifvga_tune); \
} while(0)

/* ============ ROW5 ============ */
typedef struct {
    u8 rfmix_tune;
    u8 ifvga_vga_adj;
} hmc6301_row5_t;

#define ROW5_rfmix_tune_MS (0b1111)
#define ROW5_rfmix_tune_OF (0)

#define ROW5_ifvga_vga_adj_MS (0b1111)
#define ROW5_ifvga_vga_adj_OF (4)

#define ROW5_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 5, rfmix_tune, conf); \
    ROW_SET(rows, 5, ifvga_vga_adj, conf); \
} while(0)

#define ROW5_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 5, rfmix_tune); \
    ROW_DUMP(rows, 5, ifvga_vga_adj); \
} while(0)

/* ============ ROW6 ============ */
typedef struct {
    u8 tripler_bias;
} hmc6301_row6_t;

#define ROW6_tripler_bias_MS (0b11111111)
#define ROW6_tripler_bias_OF (0)

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
    u8 fm_pwrdn;
    u8 bbamp_selfm;
    u8 tripler_bias;
} hmc6301_row7_t;

#define ROW7_fm_pwrdn_MS (0b1)
#define ROW7_fm_pwrdn_OF (0)

#define ROW7_bbamp_selfm_MS (0b1)
#define ROW7_bbamp_selfm_OF (1)

#define ROW7_tripler_bias_MS (0b111111)
#define ROW7_tripler_bias_OF (2)

#define ROW7_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 7, fm_pwrdn, conf); \
    ROW_SET(rows, 7, bbamp_selfm, conf); \
    ROW_SET(rows, 7, tripler_bias, conf); \
} while(0)

#define ROW7_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 7, fm_pwrdn); \
    ROW_DUMP(rows, 7, bbamp_selfm); \
    ROW_DUMP(rows, 7, tripler_bias); \
} while(0)

/* ============ ROW8 ============ */
typedef struct {
    u8 ifvga_q_cntrl;
    u8 lna_gain;
    u8 lna_bias;
} hmc6301_row8_t;

#define ROW8_ifvga_q_cntrl_MS (0b111)
#define ROW8_ifvga_q_cntrl_OF (0)

#define ROW8_lna_gain_MS (0b11)
#define ROW8_lna_gain_OF (3)

#define ROW8_lna_bias_MS (0b111)
#define ROW8_lna_bias_OF (5)

#define ROW8_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 8, ifvga_q_cntrl, conf); \
    ROW_SET(rows, 8, lna_gain, conf); \
} while(0)

#define ROW8_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 8, ifvga_q_cntrl); \
    ROW_DUMP(rows, 8, lna_gain); \
} while(0)

/* ============ ROW9 ============ */
typedef struct {
    u8 en_Sep_ifmix_pwrdn_q;
    u8 en_tempFlash;
    u8 enbar_TempS;
    u8 enAnaV_LNA;
} hmc6301_row9_t;

#define ROW9_en_Sep_ifmix_pwrdn_q_MS (0b1)
#define ROW9_en_Sep_ifmix_pwrdn_q_OF (4)

#define ROW9_en_tempFlash_MS (0b1)
#define ROW9_en_tempFlash_OF (5)

#define ROW9_enbar_TempS_MS (0b1)
#define ROW9_enbar_TempS_OF (6)

#define ROW9_enAnaV_LNA_MS (0b1)
#define ROW9_enAnaV_LNA_OF (7)

#define ROW9_SETALL(rows, conf) \
do { \
    ROW_SET(rows, 9, en_Sep_ifmix_pwrdn_q, conf); \
    ROW_SET(rows, 9, en_tempFlash, conf); \
    ROW_SET(rows, 9, enbar_TempS, conf); \
    ROW_SET(rows, 9, enAnaV_LNA, conf); \
} while(0)

#define ROW9_DUMPALL(rows) \
do { \
    ROW_DUMP(rows, 9, en_Sep_ifmix_pwrdn_q); \
    ROW_DUMP(rows, 9, en_tempFlash); \
    ROW_DUMP(rows, 9, enbar_TempS); \
    ROW_DUMP(rows, 9, enAnaV_LNA); \
} while(0)

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
} hmc6301_row16_t;

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
} hmc6301_row17_t;

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
#define ROW17_en_lockd_clk_OF (7)

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
} hmc6301_row18_t;

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
} hmc6301_row19_t;

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
} hmc6301_row20_t;

#define ROW20_Fbdiv_code_MS (0b111111)
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
} hmc6301_row21_t;

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
} hmc6301_row22_t;

#define ROW22_vco_bandSel_MS (0b111111)
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
} hmc6301_row23_t;

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
} hmc6301_row24_t;

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
} hmc6301_row25_t;

#define ROW25_vtune_flashp_MS (0b11111111)
#define ROW25_vtune_flashp_OF (0)

/* ============ ROW26 ============ */
typedef struct {
    u8 vtune_flashn;
} hmc6301_row26_t;

#define ROW26_vtune_flashn_MS (0b11111111)
#define ROW26_vtune_flashn_OF (0)

/* ============ ROW27 ============ */
typedef struct {
    u8 tempS;
} hmc6301_row27_t;

#define ROW27_tempS_MS (0b11111)
#define ROW27_tempS_OF (0)

typedef struct {
    hmc6301_row0_t row0;
    hmc6301_row1_t row1;
    hmc6301_row2_t row2;
    hmc6301_row3_t row3;
    hmc6301_row4_t row4;
    hmc6301_row5_t row5;
    hmc6301_row6_t row6;
    hmc6301_row7_t row7;
    hmc6301_row8_t row8;
    hmc6301_row9_t row9;
    hmc6301_row16_t row16;
    hmc6301_row17_t row17;
    hmc6301_row18_t row18;
    hmc6301_row19_t row19;
    hmc6301_row20_t row20;
    hmc6301_row21_t row21;
    hmc6301_row22_t row22;
    hmc6301_row23_t row23;
    hmc6301_row24_t row24;
    hmc6301_row25_t row25;
    hmc6301_row26_t row26;
    hmc6301_row27_t row27;
} hmc6301_reg_file_t;

#define ROWS_NUM (28)

#endif /* HMC56301_REG_FILE_H */
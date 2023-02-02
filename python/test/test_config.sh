
test_setup() {

    test_config=$1
    clk_config=$2

    lmk_config=$(get_config $clk_config lmk "\"\"")
    lmx2820_config=$(get_config $clk_config lmx2820 "\"\"")
    rf_pwr_config="../hmc/configs/rf_power.json"
    rf_pwr_config_pre="../hmc/configs/rf_power_pre.json"

    [[ $lmk_config != "" ]] && lmk_config="--lmk ../rfdc/configs/$lmk_config"
    [[ $lmx2820_config != "" ]] && lmx2820_config="--lmx2820 ../lmx/$lmx2820_config"

    adc_dac_hw_loppback=$(get_config $test_config adc_dac_hw_loppback False)
    adc_dac_sw_loppback=$(get_config $test_config adc_dac_sw_loppback False)

    if [ $adc_dac_hw_loppback == "False" ] && [ $adc_dac_sw_loppback == "False" ]; then
        mode="RF"
    elif [ $adc_dac_hw_loppback == "True" ] && [ $adc_dac_sw_loppback == "False" ]; then
        mode="hw_loopback"
    else
        mode="sw_loopback"
    fi

    echo "******************* MODE = $mode *******************"

    #Init CLK 104
    echo "******************* Configuring CLK 104 *******************"
    $py ../rfdc/rfdc_clk.py --clk_104 $lmk_config
    [[ $? != 0 ]] && exit 1

    case $mode in
        "RF")
            # Setup RF scenario:
            # Init LO
            # Init RF RX/TX
            # Shut down RX outputs
            # Init RFDC
            # Enable RF RX/TX

            #Init LO lmx2820
            echo "******************* Configuring LO lmx2820 (pre step, Mute = On) *******************"
            $py ../lmx/lmx.py $lmx2820_config --mute

            #Init HMC (Pre-init stage, to let rfdc calibrate)
            echo "******************* Configuring RF RX/TX (pre step) *******************"
            $py ../hmc/hmc.py --cfg $test_config --rf_cfg $rf_pwr_config_pre
            [[ $? != 0 ]] && exit 1

            #Init RFDC (Calibration)
            echo "******************* Configuring RFDC *******************"
            $py ../rfdc/rfdc_clk.py --rfdc
            [[ $? != 0 ]] && exit 1

            #Init HMC (Post-init stage)
            echo "******************* Configuring RF RX/TX (post step) *******************"
            $py ../hmc/hmc.py --cfg $test_config --rf_cfg $rf_pwr_config
            [[ $? != 0 ]] && exit 1

            echo "******************* Configuring LO lmx2820 (post step, Mute = Off) *******************"
            $py ../lmx/lmx.py

            ;;
        "hw_loopback")
            # Setup HW loopback scenario:
            # Export BRAM content
            # Zero BRAM, so DAC outputs near zero
            # Init RFDC
            # Load BRAM

            # Data will be stored as ./bram0.npy, ./bram1.npy
            echo "******************* Exporting and erasing BRAM *******************"
            export_path="."
            $py ../dac/player.py --export $export_path
            $py ../dac/player.py --zero

            #Enable ADC/DAC sync
            $py ../axi/gpio.py --adc_dac_sync 255

            #Init RFDC (Calibration)
            echo "******************* Configuring RFDC *******************"
            $py ../rfdc/rfdc_clk.py --rfdc
            [[ $? != 0 ]] && exit 1

            #Disable ADC/DAC sync
            $py ../axi/gpio.py --adc_dac_sync 0

            #Load exported BRAM back
            echo "******************* Loading BRAM content *******************"
            $py ../dac/player.py --bram0 "$export_path/bram0.npy" --bram1 "$export_path/bram1.npy"

            rm "./bram0.npy" "$export_path/bram1.npy"
            ;;
        "sw_loopback")
            ;;
    esac
}
class Hw:
    MAX_RX_CHAINS = 0x8
    BUFFERS_IN_BRAM = 0x8
    SAMPLES_PER_FLIT = 0x8
    BYTES_PER_SAMPLE = 0x2
    CAPTURE_WAIT_TIME_CORRECTION = 1.0
    CPU_PAGE_SIZE=4096
    HW_INTEGRATOR_WINDOW_SIZE=1
    DDR_BPS_MAX = 500 * 1e6 * 8 * BYTES_PER_SAMPLE #Bytes per sec
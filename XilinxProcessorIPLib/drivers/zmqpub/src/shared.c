#include <stdint.h>
#include <signal.h>
#include <stdlib.h>
#include <stdio.h>

#include "main.h"

void siginthandler(int param)
{

    printf("SIGINT caught, exiting ...\r\n");
    MainLoop_SigintRecv();
}

int MainLoopInit (const char *port,
                    const char *topic,
                    const char *_sync_gpio_name,
                    uint32_t _fs,
                    uint32_t _debug)
{
    signal(SIGINT, siginthandler);
    return MainLoopInit_cpp(port, topic, _sync_gpio_name, _fs, _debug);
}

int MainLoopDestroy (void)
{
    return MainLoopDestroy_cpp();
}

int MainLoop (  uint32_t *ddr_id_array,
                const char **dmaNameArray,
                uint64_t *dmaAddrArray,
                uint64_t *dmaLenArray,
                uint32_t dmaNumInst,
                uint32_t waitTimeMs,
                uint32_t txn,
                uint32_t *rxn,
                uint32_t rxn_len)
{
    return MainLoop_cpp(ddr_id_array, dmaNameArray, dmaAddrArray, dmaLenArray, dmaNumInst, waitTimeMs, txn, rxn, rxn_len);
}
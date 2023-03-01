#include <stdint.h>
#include <signal.h>
#include <stdlib.h>

#include "main.h"

void siginthandler(int param)
{
    MainLoopDestroy();
    exit(1);
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

int MainLoop (const char **dmaNameArray,
                uint64_t *dmaAddrArray,
                uint64_t *dmaLenArray,
                uint32_t dmaNumInst,
                uint32_t waitTimeMs,
                uint32_t txn,
                uint32_t *rxn,
                uint32_t rxn_len)
{
    return MainLoop_cpp(dmaNameArray, dmaAddrArray, dmaLenArray, dmaNumInst, waitTimeMs, txn, rxn, rxn_len);
}
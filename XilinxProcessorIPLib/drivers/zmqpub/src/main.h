#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

int MainLoopInit_cpp (const char *port,
                    const char *topic,
                    const char *_sync_gpio_name,
                    uint32_t _fs,
                    uint32_t _debug);

int MainLoopDestroy_cpp (void);

int MainLoop_cpp (const char **dmaNameArray,
                uint64_t *dmaAddrArray,
                uint64_t *dmaLenArray,
                uint32_t dmaNumInst,
                uint32_t waitTimeMs,
                uint32_t txn,
                uint32_t *rxn,
                uint32_t rxn_len);

#ifdef __cplusplus
};
#endif

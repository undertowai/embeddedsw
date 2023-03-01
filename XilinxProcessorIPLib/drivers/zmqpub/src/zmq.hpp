
#pragma once

int ZmqInit(std::string port, std::string _topic);
int ZmqDestroy(void);
int ZmqPublish(uint32_t sn,
                uint32_t txn,
                std::vector<uint32_t> rxn,
                uint32_t fs,
                std::vector<void *> &iq_data,
                std::vector<uint32_t> &iq_data_size);
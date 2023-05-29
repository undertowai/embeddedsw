
#pragma once

int ZmqInit(std::string port, std::string _topic);
int ZmqDestroy(void);
int ZmqPublish(uint32_t sn,
                std::vector<uint32_t> txn,
                std::vector<uint32_t> rxn,
                uint32_t fs,
                DdrMng::IqData &iq_data_v);
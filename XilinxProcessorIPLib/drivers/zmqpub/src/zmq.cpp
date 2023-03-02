#include <iostream>
#include <zmq_addon.hpp>
#include <chrono>
#include <thread>
#include <stdint.h>

static zmq::context_t ctx;
static zmq::socket_t *sock;
std::string topic;

int ZmqInit(std::string port, std::string _topic)
{
    topic = _topic;
    sock = new zmq::socket_t (ctx, zmq::socket_type::pub);
    std::string addr("tcp://*:");
    addr += port;

    sock->bind(addr);
    const std::string last_endpoint = sock->get(zmq::sockopt::last_endpoint);
    std::cout << "Connecting to " << last_endpoint << std::endl;
    return 0;
}

int ZmqDestroy(void)
{
    delete sock;
    return 0;
}

int ZmqPublish(uint32_t sn,
                uint32_t txn,
                std::vector<uint32_t> rxn,
                uint32_t fs,
                std::vector<void *> &iq_data,
                std::vector<uint32_t> &iq_data_size)
{
    uint32_t freq = 0;
    uint64_t sent_time = 0;
    uint32_t num_streams = rxn.size() * 2;
    std::vector<zmq::const_buffer> send_msgs;
    const int VERSION = 2;

    {
        send_msgs.push_back(zmq::buffer(topic));
        send_msgs.push_back(zmq::buffer(std::to_string(VERSION)));
        send_msgs.push_back(zmq::buffer(std::to_string(sn)));
        send_msgs.push_back(zmq::buffer(std::to_string(txn)));
        send_msgs.push_back(zmq::buffer(rxn));
        send_msgs.push_back(zmq::buffer(std::to_string(fs)));
        send_msgs.push_back(zmq::buffer(std::to_string(freq)));
        send_msgs.push_back(zmq::buffer(std::to_string(sent_time)));
        for (int i  = 0; i < num_streams; i++) {
            send_msgs.push_back( zmq::buffer(iq_data[i], iq_data_size[i]) );
        }
    };

    zmq::send_multipart(*sock, send_msgs);
    return 0;
}

import pickle
import time
import zmq

class Inet:
    TOPIC_FILTER = 10001
    PORT = 5556

    def __init__(self):
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://0.0.0.0:%s" % self.PORT)

    def publish(self, seq_idx, tx_array, sampling_freq, frequency, rx_array, rx_iq_data):
        self.publisher.send_multipart(
            [
                bytes(str(self.TOPIC_FILTER), "utf-8"),
                bytes(str(seq_idx), "utf-8"),
                pickle.dumps(tx_array),
                pickle.dumps(rx_array),
                bytes(str(sampling_freq), "utf-8"),
                bytes(str(frequency), "utf-8"),
                bytes(str(time.time_ns() / 1_000_000_000), "utf-8"),
                pickle.dumps(rx_iq_data)
            ]
        )
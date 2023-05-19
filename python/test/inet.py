
import pickle
import time
import zmq

class Inet:
    TOPIC_FILTER = "10001"
    PORT = "5556"

    def __init__(self):
        pass

    def init_publisher(self):
        context = zmq.Context()
        self.publisher = context.socket(zmq.PUB)
        self.publisher.bind("tcp://0.0.0.0:%s" % self.PORT)

    def publish(self, version, seq_idx, tx_array, sampling_freq, frequency, rx_array, rx_iq_data):
        self.publisher.send_multipart(
            [
                bytes(str(self.TOPIC_FILTER), "utf-8"),
                bytes(str(version), "utf-8"),
                bytes(str(seq_idx), "utf-8"),
                pickle.dumps(tx_array),
                pickle.dumps(rx_array),
                bytes(str(sampling_freq), "utf-8"),
                bytes(str(frequency), "utf-8"),
                bytes(str(time.time_ns() / 1_000_000_000), "utf-8"),
                pickle.dumps(rx_iq_data)
            ]
        )
        """
        Example subscriber :

            def convert_recv_data(self, data):
                [topic, version, sn, txarray, rxarray, fs, freq, sent_time, *iq_data] = data

                version = int(version.decode('utf-8'))

                if version == 1:
                    iq_data = pickle.loads(iq_data[0])
                    rxarray = pickle.loads(rxarray)
                    txarray = pickle.loads(txarray)
                elif version == 2:
                    rxarray = np.frombuffer(rxarray, dtype=np.uint32)
                    txarray = np.frombuffer(txarray, dtype=np.uint32)

                    iq_data = list(iq_data)
                    iq_data = list(map(lambda iq: np.frombuffer(iq, dtype=np.int16), iq_data))

                    iq_data_out = []
                    for i in range(0, len(iq_data), 2):
                        iq_data_out.append( (iq_data[i], iq_data[i+1]) )
                    iq_data = iq_data_out
                else:
                    assert False


                return [topic, sn, txarray, rxarray, fs, freq, sent_time, iq_data]
        """
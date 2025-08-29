# shared/grpcConnectionPooling.py
import threading
from pathlib import Path
import grpc

from passkit.io.member import a_rpc_pb2_grpc as member_grpc
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc
from passkit.io.core import a_rpc_templates_pb2_grpc as templates_grpc
from passkit.io.event_tickets import a_rpc_pb2_grpc as events_grpc
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc
import threading
import grpc
from pathlib import Path
import constants


def _credentials() -> grpc.ChannelCredentials:
    with open(constants.CA_FILE, "rb") as f:
        ca = f.read()
    with open(constants.CERT_FILE, "rb") as f:
        cert = f.read()
    with open(constants.KEY_FILE, "rb") as f:
        key = f.read()
    return grpc.ssl_channel_credentials(root_certificates=ca,
                                        private_key=key,
                                        certificate_chain=cert)


class ChannelPool:
    def __init__(self, size: int = constants.POOL_SIZE):
        self._lock = threading.Lock()
        self._idx = 0
        creds = _credentials()
        self._channels = [grpc.secure_channel(
            constants.GRPC_HOST, creds) for _ in range(size)]

    def get(self) -> grpc.Channel:
        with self._lock:
            ch = self._channels[self._idx]
            self._idx = (self._idx + 1) % len(self._channels)
            return ch

    def close(self):
        for ch in self._channels:
            ch.close()
        self._channels.clear()

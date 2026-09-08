"""Mutual-TLS gRPC connections and round-robin pooling."""

from __future__ import annotations

import threading

import grpc
from cryptography.hazmat.primitives import serialization
from passkit.io.analytics.a_rpc_pb2_grpc import AnalyticsStub
from passkit.io.core.a_rpc_certificates_pb2_grpc import CertificatesStub
from passkit.io.core.a_rpc_distribution_pb2_grpc import DistributionStub
from passkit.io.core.a_rpc_images_pb2_grpc import ImagesStub
from passkit.io.core.a_rpc_messages_pb2_grpc import MessagesStub
from passkit.io.core.a_rpc_others_pb2_grpc import IntegrationsStub, UsersStub
from passkit.io.core.a_rpc_templates_pb2_grpc import TemplatesStub
from passkit.io.event_tickets.a_rpc_pb2_grpc import EventTicketsStub
from passkit.io.flights.a_rpc_pb2_grpc import FlightsStub
from passkit.io.member.a_rpc_pb2_grpc import MembersStub
from passkit.io.raw.a_rpc_pb2_grpc import RawStub
from passkit.io.scheduler.a_rpc_pb2_grpc import SchedulerStub
from passkit.io.single_use_coupons.a_rpc_pb2_grpc import SingleUseCouponsStub

from quickstarts.config import Config

STUB_CLASSES = {
    "analytics": AnalyticsStub,
    "certificates": CertificatesStub,
    "distribution": DistributionStub,
    "images": ImagesStub,
    "messages": MessagesStub,
    "integrations": IntegrationsStub,
    "users": UsersStub,
    "templates": TemplatesStub,
    "event_tickets": EventTicketsStub,
    "flights": FlightsStub,
    "members": MembersStub,
    "raw": RawStub,
    "scheduler": SchedulerStub,
    "coupons": SingleUseCouponsStub,
}


def _private_key(path, passphrase: str | None) -> bytes:
    pem = path.read_bytes()
    if b"ENCRYPTED" not in pem:
        return pem
    if not passphrase:
        raise ValueError("PASSKIT_PASSPHRASE is required for the encrypted private key")
    key = serialization.load_pem_private_key(pem, password=passphrase.encode())
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


class Connection:
    def __init__(self, config: Config):
        credentials = grpc.ssl_channel_credentials(
            root_certificates=config.root_certificate.read_bytes(),
            private_key=_private_key(config.private_key, config.passphrase),
            certificate_chain=config.certificate.read_bytes(),
        )
        self.channel = grpc.secure_channel(config.address, credentials)
        self.stubs = {name: cls(self.channel) for name, cls in STUB_CLASSES.items()}

    def close(self) -> None:
        self.channel.close()


class ConnectionPool:
    def __init__(self, config: Config):
        size = 1 if config.connection_mode == "single" else config.pool_size
        self._connections = [Connection(config) for _ in range(size)]
        self._index = 0
        self._lock = threading.Lock()

    def service(self, name: str):
        with self._lock:
            connection = self._connections[self._index]
            self._index = (self._index + 1) % len(self._connections)
        return connection.stubs[name]

    def close(self) -> None:
        for connection in self._connections:
            connection.close()

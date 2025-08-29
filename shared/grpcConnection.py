# shared/grpcConnection.py
from dataclasses import dataclass
from typing import Tuple
import grpc
import constants

from passkit.io.member import a_rpc_pb2_grpc as member_grpc
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc
from passkit.io.core import a_rpc_templates_pb2_grpc as templates_grpc
from passkit.io.event_tickets import a_rpc_pb2_grpc as events_grpc
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc


@dataclass
class Stubs:
    members: member_grpc.MembersStub
    coupons: coupons_grpc.SingleUseCouponsStub
    events: events_grpc.EventTicketsStub
    flights: flights_grpc.FlightsStub
    templates: templates_grpc.TemplatesStub


def _load_certs() -> Tuple[bytes, bytes, bytes]:
    with open(constants.CA_FILE, "rb") as f:
        ca = f.read()
    with open(constants.CERT_FILE, "rb") as f:
        cert = f.read()
    with open(constants.KEY_FILE, "rb") as f:
        key = f.read()
    return ca, cert, key


def create_channel() -> grpc.Channel:
    ca, cert, key = _load_certs()
    creds = grpc.ssl_channel_credentials(
        root_certificates=ca,
        private_key=key,
        certificate_chain=cert,
    )
    # Optional channel options (keepalive etc.) can go here if needed
    return grpc.secure_channel(constants.GRPC_HOST, creds)


def create_stubs(channel: grpc.Channel) -> Stubs:
    """Build all commonly used stubs for a given channel."""
    return Stubs(
        members=member_grpc.MembersStub(channel),
        coupons=coupons_grpc.SingleUseCouponsStub(channel),
        events=events_grpc.EventTicketsStub(channel),
        flights=flights_grpc.FlightsStub(channel),
        templates=templates_grpc.TemplatesStub(channel),
    )


def connect() -> Tuple[grpc.Channel, Stubs]:
    """Return a secure channel and all service stubs (single-channel workflow)."""
    channel = create_channel()
    return channel, create_stubs(channel)

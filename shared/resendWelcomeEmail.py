# core/resendWelcomeEmail.py
import grpc
from typing import Optional
from passkit.io.core import a_rpc_distribution_pb2_grpc as distribution_grpc
from passkit.io.common import distribution_pb2

# Valid protocol strings as per your build:
VALID_PROTOCOLS = {"FLIGHT_PROTOCOL", "MEMBERSHIP",
                   "SINGLE_USE_COUPON", "EVENT_TICKETING"}


def run(
    channel: grpc.Channel,
    protocol: str,
    *,
    member_id: Optional[str] = None,
    coupon_id: Optional[str] = None,
    boarding_pass_id: Optional[str] = None,
    ticket_id: Optional[str] = None,
) -> None:
    """
    Resend welcome email for the given protocol/object.
    protocol: one of "FLIGHT_PROTOCOL", "MEMBERSHIP", "SINGLE_USE_COUPON", "EVENT_TICKETING"

    Provide the matching ID:
      - MEMBERSHIP        -> member_id
      - SINGLE_USE_COUPON -> coupon_id
      - FLIGHT_PROTOCOL   -> boarding_pass_id
      - EVENT_TICKETING   -> ticket_id
    """
    if protocol not in VALID_PROTOCOLS:
        raise ValueError(f"protocol must be one of {sorted(VALID_PROTOCOLS)}")

    # Choose the required id based on protocol
    id_field_name, id_value = None, None
    if protocol == "MEMBERSHIP":
        id_field_name, id_value = "memberId", member_id
    elif protocol == "SINGLE_USE_COUPON":
        id_field_name, id_value = "couponId", coupon_id
    elif protocol == "FLIGHT_PROTOCOL":
        id_field_name, id_value = "boardingPassId", boarding_pass_id
    elif protocol == "EVENT_TICKETING":
        id_field_name, id_value = "ticketId", ticket_id

    if not id_value:
        raise ValueError(
            f"{id_field_name} is required for protocol {protocol}")

    stub = distribution_grpc.DistributionStub(channel)

    req = distribution_pb2.EmailDistributionRequest()
    # protocol is a *string* in your build
    req.protocol = protocol

    # Set the correct id field if present; otherwise fall back to a generic 'id'
    if hasattr(req, id_field_name):
        setattr(req, id_field_name, id_value)
    elif hasattr(req, "id"):
        req.id = id_value
    else:
        raise RuntimeError(
            f"EmailDistributionRequest has neither '{id_field_name}' nor 'id' field on this build."
        )

    stub.sendWelcomeEmail(req)

    print(f"Resent welcome email for {protocol} ({id_field_name}={id_value})")

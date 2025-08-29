# coupons/updateCoupon.py
import grpc
from typing import Optional
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, coupon_pb2
from passkit.io.common.personal_pb2 import Person


def run(
    channel: grpc.Channel,
    campaign_id: str,
    coupon_id: str,
    *,
    offer_id: Optional[str] = None,
    display_name: str = "Percy PassKit",
    forename: str = "Percy",
    surname: str = "PassKit",
    email: Optional[str] = None,
) -> str:
    """
    Update a coupon's recipient/person details 
    Returns the updated coupon id.
    """
    if not campaign_id:
        raise ValueError("campaign_id is required")
    if not coupon_id:
        raise ValueError("coupon_id is required")

    stub = coupons_grpc.SingleUseCouponsStub(channel)

    # Build person update
    person = Person()
    person.displayName = display_name
    person.forename = forename
    person.surname = surname
    if email:
        person.emailAddress = email

    # Build coupon update
    coupon = coupon_pb2.Coupon()
    if hasattr(coupon, "id"):
        coupon.id = coupon_id
    elif hasattr(coupon, "couponId"):
        coupon.couponId = coupon_id
    if hasattr(coupon, "campaignId"):
        coupon.campaignId = campaign_id
    if offer_id and hasattr(coupon, "offerId"):
        coupon.offerId = offer_id

    coupon.person.CopyFrom(person)

    resp = stub.updateCoupon(coupon)

    updated_id = getattr(resp, "id", "") or getattr(resp, "couponId", "")
    print("Updated coupon:", updated_id)
    return updated_id

# coupons/createCoupon.py
import grpc
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, coupon_pb2
from passkit.io.common.personal_pb2 import Person


def run(
    channel: grpc.Channel,
    campaign_id: str,
    offer_id: str,
    recipient_email: str,
    *,
    display_name: str = "Percy PassKit",
    forename: str = "Percy",
    surname: str = "PassKit",
) -> str:
    """
    Create a coupon for a recipient under a given campaign/offer.
    Returns the created coupon id.
    """
    if not campaign_id:
        raise ValueError("campaign_id is required")
    if not offer_id:
        raise ValueError("offer_id is required")
    if not recipient_email:
        raise ValueError("recipient_email is required")

    stub = coupons_grpc.SingleUseCouponsStub(channel)

    # Build recipient
    person = Person()
    person.displayName = display_name
    person.forename = forename
    person.surname = surname
    person.emailAddress = recipient_email

    # Build coupon
    coupon = coupon_pb2.Coupon()
    coupon.campaignId = campaign_id
    coupon.offerId = offer_id
    coupon.person.CopyFrom(person)

    resp = stub.createCoupon(coupon)

    coupon_id = getattr(resp, "id", "")
    print("Created coupon:", coupon_id)
    return coupon_id


# Optional standalone test
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        # fill with real ids/email to test
        run(ch, campaign_id="", offer_id="", recipient_email="test@example.com")
    finally:
        pool.close()

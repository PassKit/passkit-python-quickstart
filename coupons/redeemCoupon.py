# coupons/redeemCoupon.py
import grpc
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, coupon_pb2


def run(channel: grpc.Channel, campaign_id: str, coupon_id: str, *, offer_id: str | None = None) -> str:
    """
    Redeem a coupon using the Coupon message.
    Returns the redeemed coupon id.
    """
    if not coupon_id:
        raise ValueError("coupon_id is required")
    if not campaign_id:
        raise ValueError("campaign_id is required")

    stub = coupons_grpc.SingleUseCouponsStub(channel)

    coupon = coupon_pb2.Coupon()
    # Set identifiers using whatever fields exist in your build
    if hasattr(coupon, "id"):
        coupon.id = coupon_id
    elif hasattr(coupon, "couponId"):
        coupon.couponId = coupon_id

    if hasattr(coupon, "campaignId"):
        coupon.campaignId = campaign_id
    if offer_id and hasattr(coupon, "offerId"):
        coupon.offerId = offer_id

    resp = stub.redeemCoupon(coupon)

    redeemed_id = getattr(resp, "id", "") or getattr(resp, "couponId", "")
    print("Redeemed coupon:", redeemed_id)
    return redeemed_id


# Optional standalone test
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_CAMPAIGN_ID = ""
    TEST_COUPON_ID = ""
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_CAMPAIGN_ID, TEST_COUPON_ID)
    finally:
        pool.close()

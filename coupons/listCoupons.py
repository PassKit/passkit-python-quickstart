import grpc
from typing import List
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, coupon_pb2


def run(channel: grpc.Channel, campaign_id: str, *, timeout: float = 30.0) -> List[str]:
    """
    Stream coupons for a given campaignId and return a list of coupon IDs.
    Uses listCouponsByCouponCampaign(ListRequest).
    """
    if not campaign_id:
        raise ValueError("campaign_id is required")

    stub = coupons_grpc.SingleUseCouponsStub(channel)

    # Build request
    req = coupon_pb2.ListRequest()
    if hasattr(req, "couponCampaignId"):
        req.couponCampaignId = campaign_id
    elif hasattr(req, "campaignId"):
        req.campaignId = campaign_id
    else:
        raise RuntimeError("ListRequest has no campaign id field")

    coupon_ids: List[str] = []
    try:
        for item in stub.listCouponsByCouponCampaign(req, timeout=timeout):
            cid = getattr(item, "id", "") or getattr(
                getattr(item, "coupon", object()), "id", "")
            if cid:
                coupon_ids.append(cid)
                print("Received coupon:", cid)
            else:
                # fallback log if structure is different
                print("Received:", item)
        print("Stream ended successfully.")
    except grpc.RpcError as e:
        print(f"gRPC Error while listing coupons: {e.code()} - {e.details()}")

    return coupon_ids


# Optional standalone test
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_CAMPAIGN_ID = ""  # set a real campaign id to test
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_CAMPAIGN_ID)
    finally:
        pool.close()

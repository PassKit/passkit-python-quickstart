# coupons/deleteCampaign.py
import grpc
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, campaign_pb2


def run(channel: grpc.Channel, campaign_id: str) -> None:
    """
    Delete a coupon campaign by ID.
    """
    if not campaign_id:
        raise ValueError("campaign_id is required")

    stub = coupons_grpc.SingleUseCouponsStub(channel)
    req = campaign_pb2.CouponCampaign()
    req.id = campaign_id

    stub.deleteCouponCampaign(req)

    print("Campaign has been deleted:", campaign_id)


# Optional: standalone test
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_CAMPAIGN_ID = ""  # set a real campaign id to test
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_CAMPAIGN_ID)
    finally:
        pool.close()

# coupons/createCampaign.py
import grpc
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, campaign_pb2
from passkit.io.common.project_pb2 import ProjectStatus  # enum values


def run(channel: grpc.Channel, name: str = "Quickstart Campaign") -> str:
    """
    Create a coupon campaign and return its id.
    """
    stub = coupons_grpc.SingleUseCouponsStub(channel)

    campaign = campaign_pb2.CouponCampaign()
    campaign.name = name
    # status is a repeated enum field — use extend with enum values
    campaign.status.extend([
        ProjectStatus.PROJECT_ACTIVE_FOR_OBJECT_CREATION,
        ProjectStatus.PROJECT_DRAFT,
    ])
    if hasattr(campaign, "timezone"):
        campaign.timezone = "Europe/London"

    resp = stub.createCouponCampaign(campaign)

    cid = getattr(resp, "id", "")
    print("Created coupon campaign:", cid)
    return cid


if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch)
    finally:
        pool.close()

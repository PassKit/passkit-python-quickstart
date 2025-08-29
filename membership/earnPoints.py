# membership/earnPoints.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc as member_grpc, member_pb2


def run(
    channel: grpc.Channel,
    member_id: str,
    *,
    points: int = 100,
    secondary_points: int = 0,
    tier_points: int = 0,
) -> str:
    """
    Earn points for a member.
    Returns the member id (from the response).
    """
    if not member_id:
        raise ValueError("member_id is required")

    stub = member_grpc.MembersStub(channel)

    req = member_pb2.EarnBurnPointsRequest()
    req.id = member_id
    req.points = points
    req.secondaryPoints = secondary_points
    req.tierPoints = tier_points

    resp = stub.earnPoints(req)

    resp_id = getattr(resp, "id", "")
    print(f"Member {resp_id} has earned {points} points")
    return resp_id


# Optional: run standalone for testing (set a real member id first)
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_MEMBER_ID = ""  # set this
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_MEMBER_ID, points=100)
    finally:
        pool.close()

# membership/checkIn.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc as member_grpc, member_pb2


def run(
    channel: grpc.Channel,
    member_id: str,
    *,
    lat: float = 0.0,
    lon: float = 0.0,
    address: str = "",
) -> str:
    """
    Check in a member at a location.
    Returns the member id from the response.
    """
    if not member_id:
        raise ValueError("member_id is required")

    stub = member_grpc.MembersStub(channel)

    req = member_pb2.MemberCheckInOutRequest()
    req.memberId = member_id
    req.lat = lat
    req.lon = lon
    if address:
        req.address = address

    resp = stub.checkInMember(req)

    resp_id = getattr(resp, "id", "")
    print(f"Member {resp_id} successfully checked in")
    return resp_id


# Optional: standalone test harness
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_MEMBER_ID = ""  # set a real member id
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_MEMBER_ID, lat=22.2819, lon=114.1589, address="Hong Kong")
    finally:
        pool.close()

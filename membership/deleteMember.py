# membership/deleteMember.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc as member_grpc, member_pb2


def run(channel: grpc.Channel, member_id: str) -> None:
    """
    Delete a member by id. Doesn't return anything.
    """
    if not member_id:
        raise ValueError("member_id is required")

    stub = member_grpc.MembersStub(channel)

    req = member_pb2.Member()
    req.id = member_id

    stub.deleteMember(req)

    print("Member has been deleted:", member_id)


# Optional standalone test
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_MEMBER_ID = ""  # set a real member id to test
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_MEMBER_ID)
    finally:
        pool.close()

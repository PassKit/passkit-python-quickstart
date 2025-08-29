# membership/deleteProgram.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc as member_grpc, program_pb2


def run(channel: grpc.Channel, program_id: str) -> None:
    """
    Delete a membership/loyalty program by ID.
    """
    if not program_id:
        raise ValueError("program_id is required")

    stub = member_grpc.MembersStub(channel)

    req = program_pb2.Program()
    req.id = program_id

    stub.deleteProgram(req)

    print("Program has been deleted:", program_id)


# Optional: standalone test
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_PROGRAM_ID = ""  # set a real program id to test
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_PROGRAM_ID)
    finally:
        pool.close()

# membership/createProgram.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc, program_pb2
from passkit.io.common.project_pb2 import ProjectStatus


def run(channel: grpc.Channel) -> str:
    stub = a_rpc_pb2_grpc.MembersStub(channel)

    program = program_pb2.Program()
    program.name = "Quickstart Membership Program"
    program.status.extend([
        ProjectStatus.PROJECT_ACTIVE_FOR_OBJECT_CREATION,
        ProjectStatus.PROJECT_DRAFT,
    ])
    resp = stub.createProgram(program)

    program_id = getattr(resp, "id", "")
    print("Created membership program:", program_id)
    return program_id


# Only run directly if this file is executed standalone
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    pool = ChannelPool(size=1)
    try:
        run(pool.get())
    finally:
        pool.close()

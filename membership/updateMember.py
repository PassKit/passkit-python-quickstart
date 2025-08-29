# membership/updateMember.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc as member_grpc, member_pb2
from passkit.io.common import personal_pb2


def run(
    channel: grpc.Channel,
    program_id: str,
    tier_id: str,
    member_id: str,
    *,
    display_name: str = "Loyal Larry",
    email: str | None = None,
) -> str:
    """
    Update a member's details.
    Requires existing program_id, tier_id, and member_id.
    Returns the updated member id.
    """
    if not member_id:
        raise ValueError("member_id is required")
    if not program_id:
        raise ValueError("program_id is required")
    if not tier_id:
        raise ValueError("tier_id is required")

    stub = member_grpc.MembersStub(channel)

    member = member_pb2.Member()
    member.id = member_id
    member.programId = program_id
    member.tierId = tier_id

    person = personal_pb2.Person()
    person.displayName = display_name
    if email:
        person.emailAddress = email
    member.person.CopyFrom(person)

    resp = stub.updateMember(member)

    updated_id = getattr(resp, "id", "")
    print(f"Member {updated_id} has been updated")
    return updated_id


# Optional: standalone test harness
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    TEST_PROGRAM_ID = ""
    TEST_TIER_ID = ""
    TEST_MEMBER_ID = ""
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        run(ch, TEST_PROGRAM_ID, TEST_TIER_ID, TEST_MEMBER_ID,
            display_name="Loyal Larry", email=None)
    finally:
        pool.close()

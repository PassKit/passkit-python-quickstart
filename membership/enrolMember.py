# membership/enrolMember.py
import grpc
from passkit.io.member import a_rpc_pb2_grpc as member_grpc, member_pb2
from passkit.io.common.personal_pb2 import Person


def run(channel: grpc.Channel, program_id: str, tier_id: str, email: str) -> str:
    """
    Enrol a member into the given Program/Tier.
    Returns the created member id (used by later runs).
    """
    if not program_id:
        raise ValueError("program_id is required")
    if not tier_id:
        raise ValueError("tier_id is required")
    if not email:
        raise ValueError("email is required")

    stub = member_grpc.MembersStub(channel)

    member = member_pb2.Member()
    member.programId = program_id
    member.tierId = tier_id

    person = Person()
    person.displayName = "Percy PassKit"
    person.surname = "PassKit"
    person.forename = "Percy"
    person.emailAddress = email
    member.person.CopyFrom(person)

    resp = stub.enrolMember(member)

    member_id = getattr(resp, "id", "")
    print(f"Member enrolled successfully: {member_id}")
    if member_id:
        print(f"Pass preview: https://pub1.pskt.io/{member_id}")
    return member_id


# Allow standalone testing (optional)
if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    # WARNING: you'll need to set these to real values to test directly
    TEST_PROGRAM_ID = ""
    TEST_TIER_ID = ""
    TEST_EMAIL = "percy@example.com"

    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        mid = run(ch, TEST_PROGRAM_ID, TEST_TIER_ID, TEST_EMAIL)
        print("Created member id:", mid)
    finally:
        pool.close()

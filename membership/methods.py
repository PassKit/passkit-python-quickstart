"""Reusable membership examples collected behind one consistent interface."""

from passkit.io.common.common_objects_pb2 import Id
from passkit.io.common.filter_pb2 import Filters
from passkit.io.member.a_rpc_pb2_grpc import MembersStub
from passkit.io.member.member_pb2 import (
    ChangeTierRequest,
    ListRequest,
    MemberRecordByExternalIdRequest,
    SetPointsRequest,
)
from passkit.io.member.tier_pb2 import TierRequestInput

from membership.burnPoints import run as burn_points
from membership.checkInMember import run as check_in_member
from membership.checkOutMember import run as check_out_member
from membership.createProgram import run as create_program
from membership.createTier import run as create_tier
from membership.deleteMember import run as delete_member
from membership.deleteProgram import run as delete_program
from membership.earnPoints import run as earn_points
from membership.enrolMember import run as enrol_member
from membership.updateMember import run as update_member


def _stub(channel):
    return channel if isinstance(channel, MembersStub) else MembersStub(channel)


def get_program(channel, program_id: str):
    return _stub(channel).getProgram(Id(id=program_id))


def list_programs(channel):
    return list(_stub(channel).listPrograms(Filters(limit=-1)))


def get_tier(channel, program_id: str, tier_id: str):
    return _stub(channel).getTier(TierRequestInput(programId=program_id, tierId=tier_id))


def list_tiers(channel, program_id: str):
    request = ListRequest(programId=program_id, filters=Filters(limit=-1))
    return list(_stub(channel).listTiers(request))


def get_member_by_id(channel, member_id: str):
    return _stub(channel).getMemberRecordById(Id(id=member_id))


def get_member_by_external_id(channel, program_id: str, external_id: str):
    return _stub(channel).getMemberRecordByExternalId(
        MemberRecordByExternalIdRequest(programId=program_id, externalId=external_id)
    )


def list_members(channel, program_id: str):
    request = ListRequest(programId=program_id, filters=Filters(limit=-1))
    return list(_stub(channel).listMembers(request))


def count_members(channel, program_id: str):
    return _stub(channel).countMembers(ListRequest(programId=program_id))


def change_member_tier(channel, member_id: str, program_id: str, tier_id: str):
    return _stub(channel).changeMemberTier(
        ChangeTierRequest(memberId=member_id, programId=program_id, tierId=tier_id)
    )


def set_points(channel, member_id: str, program_id: str, points: float):
    return _stub(channel).setPoints(
        SetPointsRequest(id=member_id, programId=program_id, points=points)
    )


def list_member_events(channel, member_id: str):
    return list(_stub(channel).listEventsForMember(Id(id=member_id)))


def delete_member_events(channel, member_id: str):
    return _stub(channel).deleteEventsForMember(Id(id=member_id))


__all__ = [
    "burn_points",
    "change_member_tier",
    "check_in_member",
    "check_out_member",
    "count_members",
    "create_program",
    "create_tier",
    "delete_member",
    "delete_member_events",
    "delete_program",
    "earn_points",
    "enrol_member",
    "get_member_by_external_id",
    "get_member_by_id",
    "get_program",
    "get_tier",
    "list_member_events",
    "list_members",
    "list_programs",
    "list_tiers",
    "set_points",
    "update_member",
]

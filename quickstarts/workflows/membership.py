"""Membership and loyalty lifecycle example."""

from passkit.io.common.common_objects_pb2 import Id
from passkit.io.common.filter_pb2 import FieldFilter, FilterGroup, Filters, Operator
from passkit.io.common.personal_pb2 import Person
from passkit.io.common.project_pb2 import ProjectStatus
from passkit.io.common.protocols_pb2 import PassProtocol
from passkit.io.member.member_pb2 import (
    EarnBurnPointsRequest,
    ListRequest,
    Member,
    MemberCheckInOutRequest,
    MemberRecordByExternalIdRequest,
)
from passkit.io.member.program_pb2 import BalanceType, PointsType, Program
from passkit.io.member.tier_pb2 import Tier

from quickstarts.workflow import Workflow


class MembershipWorkflow(Workflow):
    protocol = PassProtocol.MEMBERSHIP

    def execute(self) -> dict[str, str]:
        print("Creating membership images and templates")
        self.create_images()
        bronze_template = self.create_template("Python Quickstart Bronze", "#CD7F32")
        silver_template = self.create_template("Python Quickstart Silver", "#C0C0C0")

        print("Creating membership program and tiers")
        program = Program(
            name="Python Quickstart Loyalty Program",
            status=[
                ProjectStatus.PROJECT_DRAFT,
                ProjectStatus.PROJECT_ACTIVE_FOR_OBJECT_CREATION,
            ],
            pointsType=PointsType(balanceType=BalanceType.BALANCE_TYPE_INT),
        )
        program_id = self.service("members").createProgram(program).id
        self.remember(
            "membership program",
            lambda: self.service("members").deleteProgram(Id(id=program_id)),
        )

        bronze_tier = (
            self.service("members")
            .createTier(
                Tier(
                    id="bronze",
                    name="Bronze",
                    tierIndex=1,
                    programId=program_id,
                    passTemplateId=bronze_template,
                    timezone="Europe/London",
                )
            )
            .id
        )
        silver_tier = (
            self.service("members")
            .createTier(
                Tier(
                    id="silver",
                    name="Silver",
                    tierIndex=2,
                    programId=program_id,
                    passTemplateId=silver_template,
                    timezone="Europe/London",
                )
            )
            .id
        )

        print("Enrolling and updating members")
        email = self.config.recipient_email or "python.member@dummy.passkit.com"
        bronze_external_id = "python-quickstart-bronze"
        bronze = Member(
            programId=program_id,
            tierId=bronze_tier,
            externalId=bronze_external_id,
            person=Person(
                displayName="Bronze Member",
                forename="Bronze",
                surname="Member",
                emailAddress=email,
            ),
        )
        bronze_id = self.service("members").enrolMember(bronze).id
        silver_id = (
            self.service("members")
            .enrolMember(
                Member(
                    programId=program_id,
                    tierId=silver_tier,
                    externalId="python-quickstart-silver",
                    person=Person(
                        displayName="Silver Member",
                        forename="Silver",
                        surname="Member",
                        emailAddress=email,
                    ),
                )
            )
            .id
        )

        self.service("members").checkInMember(
            MemberCheckInOutRequest(
                memberId=bronze_id,
                address="London, UK",
                lat=51.5074,
                lon=-0.1278,
            )
        )
        self.service("members").checkOutMember(
            MemberCheckInOutRequest(memberId=bronze_id, address="London, UK")
        )
        self.service("members").earnPoints(
            EarnBurnPointsRequest(id=bronze_id, programId=program_id, points=100)
        )
        self.service("members").burnPoints(
            EarnBurnPointsRequest(id=bronze_id, programId=program_id, points=25)
        )
        bronze.id = bronze_id
        bronze.person.displayName = "Updated Bronze Member"
        self.service("members").updateMember(bronze)

        print("Reading, listing, and counting members")
        self.service("members").getMemberRecordById(Id(id=bronze_id))
        self.service("members").getMemberRecordByExternalId(
            MemberRecordByExternalIdRequest(programId=program_id, externalId=bronze_external_id)
        )
        filters = Filters(
            limit=-1,
            filterGroups=[
                FilterGroup(
                    condition=Operator.AND,
                    fieldFilters=[
                        FieldFilter(
                            filterField="passStatus",
                            filterValue="PASS_ISSUED",
                            filterOperator="eq",
                        )
                    ],
                )
            ],
        )
        request = ListRequest(programId=program_id, filters=filters)
        list(self.service("members").listMembers(request))
        self.service("members").countMembers(request)
        list(self.service("members").listEventsForMember(Id(id=bronze_id)))

        print(f"Created membership passes: {bronze_id}, {silver_id}")
        return {"bronzePassId": bronze_id, "silverPassId": silver_id}

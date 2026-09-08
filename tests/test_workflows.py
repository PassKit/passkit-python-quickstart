import tempfile
import unittest
from pathlib import Path

from passkit.io.common.common_objects_pb2 import Id, PassBundle
from passkit.io.common.template_pb2 import PassTemplate
from passkit.io.flights.boarding_pass_pb2 import BoardingPassesResponse
from passkit.io.image.image_pb2 import ImageIds

from quickstarts.config import Config
from quickstarts.workflows.coupons import CouponsWorkflow
from quickstarts.workflows.event_tickets import EventTicketsWorkflow
from quickstarts.workflows.flights import FlightsWorkflow
from quickstarts.workflows.membership import MembershipWorkflow


class FakeStub:
    def __init__(self, calls):
        self.calls = calls
        self.counter = 0

    def __getattr__(self, method):
        def call(request):
            self.calls.append((method, request))
            self.counter += 1
            if method == "createImages":
                return ImageIds(
                    icon="icon",
                    logo="logo",
                    appleLogo="apple",
                    hero="hero",
                    eventStrip="event-strip",
                    strip="strip",
                )
            if method == "getDefaultTemplate":
                return PassTemplate()
            if method == "createBoardingPass":
                return BoardingPassesResponse(
                    boardingPasses=[PassBundle(id="boarding-pass", url="https://example.test/pass")]
                )
            if method.startswith("list"):
                return iter(())
            return Id(id=f"id-{self.counter}")

        return call


class FakePool:
    def __init__(self):
        self.calls = []
        self.stubs = {}

    def service(self, name):
        return self.stubs.setdefault(name, FakeStub(self.calls))


def config() -> Config:
    missing = Path(tempfile.gettempdir()) / "unused.pem"
    return Config(
        address="grpc.pub1.passkit.io:443",
        root_certificate=missing,
        private_key=missing,
        certificate=missing,
        passphrase=None,
        connection_mode="pool",
        pool_size=2,
        keep_assets=False,
        recipient_email=None,
        apple_certificate="pass.com.example.airline",
        carrier_code="YY",
        origin="YY4",
        destination="ADP",
    )


class WorkflowTests(unittest.TestCase):
    def exercise(self, workflow_class, required_methods):
        pool = FakePool()
        result = workflow_class(pool, config()).execute()
        called = {method for method, _request in pool.calls}
        self.assertTrue(required_methods <= called)
        self.assertTrue(result)

    def test_membership_lifecycle(self):
        self.exercise(
            MembershipWorkflow,
            {
                "createProgram",
                "createTier",
                "enrolMember",
                "earnPoints",
                "burnPoints",
                "listMembers",
            },
        )

    def test_coupon_lifecycle(self):
        pool = FakePool()
        result = CouponsWorkflow(pool, config()).execute()
        called = {method for method, _request in pool.calls}
        self.assertTrue(
            {
                "createCouponCampaign",
                "createCouponOffer",
                "createCoupon",
                "redeemCoupon",
                "voidCoupon",
            }
            <= called
        )
        offers = [request for method, request in pool.calls if method == "createCouponOffer"]
        self.assertTrue(all(len(offer.offerShortTitle) <= 10 for offer in offers))
        self.assertTrue(result)

    def test_event_ticket_lifecycle(self):
        self.exercise(
            EventTicketsWorkflow,
            {
                "createProduction",
                "createVenue",
                "createEvent",
                "createTicketType",
                "issueTicket",
                "redeemTicket",
            },
        )

    def test_flight_lifecycle(self):
        self.exercise(
            FlightsWorkflow,
            {
                "createCarrier",
                "createPort",
                "createFlight",
                "createFlightDesignator",
                "createBoardingPass",
            },
        )

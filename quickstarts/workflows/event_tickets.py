"""Event-ticket lifecycle example."""

from datetime import datetime, timedelta, timezone

from passkit.io.common.common_objects_pb2 import Id
from passkit.io.common.filter_pb2 import Filters
from passkit.io.common.personal_pb2 import Person
from passkit.io.common.project_pb2 import ProjectStatus
from passkit.io.common.protocols_pb2 import PassProtocol
from passkit.io.event_tickets.event_pb2 import Event
from passkit.io.event_tickets.production_pb2 import Production
from passkit.io.event_tickets.ticket_pb2 import (
    IssueTicketRequest,
    OrderNumberRequest,
    RedeemTicketRequest,
    Ticket,
    TicketId,
    TicketListRequest,
    TicketNumberRequest,
    ValidateTicketRequest,
)
from passkit.io.event_tickets.ticket_type_pb2 import TicketType
from passkit.io.event_tickets.venue_pb2 import Venue

from quickstarts.workflow import Workflow, timestamp


class EventTicketsWorkflow(Workflow):
    protocol = PassProtocol.EVENT_TICKETING

    def execute(self) -> dict[str, str]:
        print("Creating event-ticket images and template")
        self.create_images()
        template_id = self.create_template("Python Quickstart Event Ticket", "#CD7F32")

        print("Creating production, venue, event, and ticket type")
        production_id = (
            self.service("event_tickets")
            .createProduction(
                Production(
                    name="Python Quickstart Production",
                    finePrint="Quickstart demonstration only.",
                    status=[
                        ProjectStatus.PROJECT_DRAFT,
                        ProjectStatus.PROJECT_ACTIVE_FOR_OBJECT_CREATION,
                    ],
                )
            )
            .id
        )
        self.remember(
            "production",
            lambda: self.service("event_tickets").deleteProduction(Production(id=production_id)),
        )
        venue_id = (
            self.service("event_tickets")
            .createVenue(
                Venue(
                    name="Python Quickstart Venue",
                    address="123 Quickstart Street, London",
                    timezone="Europe/London",
                )
            )
            .id
        )
        self.remember(
            "venue",
            lambda: self.service("event_tickets").deleteVenue(Venue(id=venue_id)),
        )

        start = datetime.now(timezone.utc) + timedelta(days=7)
        event_id = (
            self.service("event_tickets")
            .createEvent(
                Event(
                    production=Production(id=production_id, name="Python Quickstart Production"),
                    venue=Venue(id=venue_id, name="Python Quickstart Venue"),
                    doorsOpen=timestamp(start - timedelta(hours=1)),
                    scheduledStartDate=timestamp(start),
                    relevantDate=timestamp(start),
                    endDate=timestamp(start + timedelta(hours=3)),
                )
            )
            .id
        )
        self.remember(
            "event",
            lambda: self.service("event_tickets").deleteEvent(Event(id=event_id)),
        )
        ticket_type_id = (
            self.service("event_tickets")
            .createTicketType(
                TicketType(
                    name="Python Quickstart General Admission",
                    productionId=production_id,
                    beforeRedeemPassTemplateId=template_id,
                )
            )
            .id
        )
        self.remember(
            "ticket type",
            lambda: self.service("event_tickets").deleteTicketType(TicketType(id=ticket_type_id)),
        )

        print("Issuing and updating ticket")
        ticket_number = "PY-1001"
        order_number = "PY-ORDER-1001"
        ticket_id = (
            self.service("event_tickets")
            .issueTicket(
                IssueTicketRequest(
                    eventId=event_id,
                    ticketTypeId=ticket_type_id,
                    ticketNumber=ticket_number,
                    orderNumber=order_number,
                    person=Person(
                        displayName="Python Ticket Holder",
                        emailAddress=self.config.recipient_email
                        or "python.ticket@dummy.passkit.com",
                    ),
                )
            )
            .id
        )
        self.remember(
            "ticket",
            lambda: self.service("event_tickets").deleteTicket(TicketId(ticketId=ticket_id)),
        )
        self.service("event_tickets").updateTicket(
            Ticket(id=ticket_id, person=Person(displayName="Updated Ticket Holder"))
        )

        print("Reading, listing, validating, and redeeming ticket")
        self.service("event_tickets").getTicketById(Id(id=ticket_id))
        self.service("event_tickets").getTicketByTicketNumber(
            TicketNumberRequest(productionId=production_id, ticketNumber=ticket_number)
        )
        self.service("event_tickets").getTicketsByOrderNumber(
            OrderNumberRequest(productionId=production_id, orderNumber=order_number)
        )
        list(
            self.service("event_tickets").listTickets(
                TicketListRequest(
                    productionId=production_id,
                    eventId=event_id,
                    filters=Filters(limit=-1),
                )
            )
        )
        self.service("event_tickets").countTickets(
            TicketListRequest(productionId=production_id, eventId=event_id)
        )
        self.service("event_tickets").validateTicket(
            ValidateTicketRequest(maxNumberOfValidations=3, ticket=TicketId(ticketId=ticket_id))
        )
        self.service("event_tickets").redeemTicket(
            RedeemTicketRequest(ticket=TicketId(ticketId=ticket_id))
        )

        print(f"Created event ticket: {ticket_id}")
        return {"eventTicketId": ticket_id}

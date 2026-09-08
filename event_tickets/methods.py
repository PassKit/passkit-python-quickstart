"""Reusable, focused examples for the PassKit Event Tickets API."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import grpc
from passkit.io.common.common_objects_pb2 import Id
from passkit.io.common.filter_pb2 import Filters
from passkit.io.common.personal_pb2 import Person
from passkit.io.common.project_pb2 import ProjectStatus
from passkit.io.event_tickets.a_rpc_pb2_grpc import EventTicketsStub
from passkit.io.event_tickets.event_pb2 import Event, EventListRequest
from passkit.io.event_tickets.production_pb2 import Production, ProductionCopyRequest
from passkit.io.event_tickets.ticket_pb2 import (
    EventTicketPassRequest,
    IssueTicketRequest,
    OrderNumberRequest,
    RedeemByOrderNumber,
    RedeemTicketRequest,
    Ticket,
    TicketId,
    TicketListRequest,
    TicketNumberRequest,
    ValidateTicketRequest,
)
from passkit.io.event_tickets.ticket_type_pb2 import TicketType, TicketTypeListRequest
from passkit.io.event_tickets.venue_pb2 import Venue

from quickstarts.workflow import timestamp


def _stub(channel_or_stub: grpc.Channel | EventTicketsStub) -> EventTicketsStub:
    """Accept either a channel or a pooled EventTicketsStub."""
    if isinstance(channel_or_stub, EventTicketsStub):
        return channel_or_stub
    return EventTicketsStub(channel_or_stub)


def create_production(channel: grpc.Channel, name: str = "Python Quickstart Production") -> str:
    response = _stub(channel).createProduction(
        Production(
            name=name,
            finePrint="Quickstart demonstration only.",
            status=[
                ProjectStatus.PROJECT_DRAFT,
                ProjectStatus.PROJECT_ACTIVE_FOR_OBJECT_CREATION,
            ],
        )
    )
    return response.id


def create_venue(channel: grpc.Channel, name: str = "Python Quickstart Venue") -> str:
    response = _stub(channel).createVenue(
        Venue(name=name, address="123 Quickstart Street, London", timezone="Europe/London")
    )
    return response.id


def create_event(channel: grpc.Channel, production_id: str, venue_id: str) -> str:
    start = datetime.now(timezone.utc) + timedelta(days=7)
    response = _stub(channel).createEvent(
        Event(
            production=Production(id=production_id),
            venue=Venue(id=venue_id),
            doorsOpen=timestamp(start - timedelta(hours=1)),
            scheduledStartDate=timestamp(start),
            relevantDate=timestamp(start),
            endDate=timestamp(start + timedelta(hours=3)),
        )
    )
    return response.id


def create_ticket_type(channel: grpc.Channel, production_id: str, template_id: str) -> str:
    response = _stub(channel).createTicketType(
        TicketType(
            name="Python Quickstart General Admission",
            productionId=production_id,
            beforeRedeemPassTemplateId=template_id,
        )
    )
    return response.id


def issue_ticket(
    channel: grpc.Channel,
    event_id: str,
    ticket_type_id: str,
    *,
    ticket_number: str,
    order_number: str,
    email: str,
) -> str:
    response = _stub(channel).issueTicket(
        IssueTicketRequest(
            eventId=event_id,
            ticketTypeId=ticket_type_id,
            ticketNumber=ticket_number,
            orderNumber=order_number,
            person=Person(displayName="Python Ticket Holder", emailAddress=email),
        )
    )
    return response.id


def update_ticket(channel: grpc.Channel, ticket_id: str, display_name: str) -> object:
    return _stub(channel).updateTicket(
        Ticket(id=ticket_id, person=Person(displayName=display_name))
    )


def get_production(channel: grpc.Channel, production_id: str) -> object:
    return _stub(channel).getProduction(Id(id=production_id))


def update_production(channel: grpc.Channel, production: Production) -> object:
    return _stub(channel).updateProduction(production)


def list_productions(channel: grpc.Channel) -> list[object]:
    return list(_stub(channel).listProductions(Filters(limit=-1)))


def copy_production(channel: grpc.Channel, production_id: str, name: str) -> object:
    return _stub(channel).copyProduction(ProductionCopyRequest(id=production_id, name=name))


def get_venue(channel: grpc.Channel, venue_id: str) -> object:
    return _stub(channel).getVenueById(Id(id=venue_id))


def update_venue(channel: grpc.Channel, venue: Venue) -> object:
    return _stub(channel).updateVenue(venue)


def list_venues(channel: grpc.Channel) -> list[object]:
    return list(_stub(channel).listVenues(Filters(limit=-1)))


def get_event(channel: grpc.Channel, event_id: str) -> object:
    return _stub(channel).getEventById(Id(id=event_id))


def update_event(channel: grpc.Channel, event: Event) -> object:
    return _stub(channel).updateEvent(event)


def list_events(channel: grpc.Channel, production_id: str) -> list[object]:
    return list(_stub(channel).listEvents(EventListRequest(productionId=production_id)))


def get_ticket_type(channel: grpc.Channel, ticket_type_id: str) -> object:
    return _stub(channel).getTicketTypeById(Id(id=ticket_type_id))


def update_ticket_type(channel: grpc.Channel, ticket_type: TicketType) -> object:
    return _stub(channel).updateTicketType(ticket_type)


def list_ticket_types(channel: grpc.Channel, production_id: str) -> list[object]:
    return list(_stub(channel).listTicketTypes(TicketTypeListRequest(productionId=production_id)))


def issue_ticket_by_id(channel: grpc.Channel, ticket: Ticket) -> object:
    return _stub(channel).issueTicketById(ticket)


def get_event_ticket_pass(channel: grpc.Channel, ticket_id: str) -> object:
    return _stub(channel).getEventTicketPass(EventTicketPassRequest(ticketId=Id(id=ticket_id)))


def redeem_tickets_by_order_number(
    channel: grpc.Channel, production_id: str, order_number: str
) -> object:
    return _stub(channel).redeemTicketsByOrderNumber(
        RedeemByOrderNumber(productionId=production_id, orderNumber=order_number)
    )


def delete_tickets_by_order_number(
    channel: grpc.Channel, production_id: str, order_number: str
) -> object:
    return _stub(channel).deleteTicketsByOrderNumber(
        OrderNumberRequest(productionId=production_id, orderNumber=order_number)
    )


def get_ticket_by_id(channel: grpc.Channel, ticket_id: str) -> object:
    return _stub(channel).getTicketById(Id(id=ticket_id))


def get_ticket_by_number(channel: grpc.Channel, production_id: str, ticket_number: str) -> object:
    return _stub(channel).getTicketByTicketNumber(
        TicketNumberRequest(productionId=production_id, ticketNumber=ticket_number)
    )


def get_tickets_by_order_number(
    channel: grpc.Channel, production_id: str, order_number: str
) -> object:
    return _stub(channel).getTicketsByOrderNumber(
        OrderNumberRequest(productionId=production_id, orderNumber=order_number)
    )


def list_tickets(channel: grpc.Channel, production_id: str, event_id: str) -> list[object]:
    request = TicketListRequest(
        productionId=production_id, eventId=event_id, filters=Filters(limit=-1)
    )
    return list(_stub(channel).listTickets(request))


def count_tickets(channel: grpc.Channel, production_id: str, event_id: str) -> object:
    return _stub(channel).countTickets(
        TicketListRequest(productionId=production_id, eventId=event_id)
    )


def validate_ticket(channel: grpc.Channel, ticket_id: str, maximum: int = 3) -> object:
    return _stub(channel).validateTicket(
        ValidateTicketRequest(maxNumberOfValidations=maximum, ticket=TicketId(ticketId=ticket_id))
    )


def redeem_ticket(channel: grpc.Channel, ticket_id: str) -> object:
    return _stub(channel).redeemTicket(RedeemTicketRequest(ticket=TicketId(ticketId=ticket_id)))


def delete_ticket(channel: grpc.Channel, ticket_id: str) -> object:
    return _stub(channel).deleteTicket(TicketId(ticketId=ticket_id))


def delete_ticket_type(channel: grpc.Channel, ticket_type_id: str) -> object:
    return _stub(channel).deleteTicketType(TicketType(id=ticket_type_id))


def delete_event(channel: grpc.Channel, event_id: str) -> object:
    return _stub(channel).deleteEvent(Event(id=event_id))


def delete_venue(channel: grpc.Channel, venue_id: str) -> object:
    return _stub(channel).deleteVenue(Venue(id=venue_id))


def delete_production(channel: grpc.Channel, production_id: str) -> object:
    return _stub(channel).deleteProduction(Production(id=production_id))

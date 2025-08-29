# flights/createFlight.py
import grpc
import datetime
from typing import Optional, Tuple

from google.protobuf import timestamp_pb2, duration_pb2
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc, flight_pb2
from passkit.io.core import a_rpc_templates_pb2_grpc as templates_grpc
from passkit.io.common import template_pb2
import constants


def _parse_iso(iso: str) -> datetime.datetime:
    dt = datetime.datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _iso_no_tz(dt: datetime.datetime) -> str:
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "")


def _set_date_message(container, field_name: str, dt: datetime.datetime) -> bool:
    """Set container.<field_name> as a date-like message (year/month/day) or fallback."""
    if not hasattr(container, field_name):
        return False
    f = container.DESCRIPTOR.fields_by_name.get(field_name)
    if f is None:
        return False

    # Message with year/month/day fields
    msg = getattr(container, field_name)
    wrote = False
    if hasattr(msg, "year"):
        msg.year = dt.year
        wrote = True
    if hasattr(msg, "month"):
        msg.month = dt.month
        wrote = True
    if hasattr(msg, "day"):
        msg.day = dt.day
        wrote = True
    if wrote:
        return True

    # String fallback "YYYY-MM-DD"
    if f.type == f.TYPE_STRING:
        setattr(container, field_name, dt.date().isoformat())
        return True

    # Integer fallback yyyymmdd
    if f.type in (f.TYPE_INT32, f.TYPE_INT64, f.TYPE_UINT32, f.TYPE_UINT64):
        setattr(container, field_name, dt.year *
                10000 + dt.month * 100 + dt.day)
        return True

    return False


def _fmt_io_local(dt: datetime.datetime) -> str:
    # Use the datetime's own wall-clock components; drop any tz info
    return f"{dt.year:04d}-{dt.month:02d}-{dt.day:02d}T{dt.hour:02d}:{dt.minute:02d}:{dt.second:02d}"


def _set_time_submsg_datetime(container, field_name: str, dt: datetime.datetime) -> bool:
    if not hasattr(container, field_name):
        return False
    sub = getattr(container, field_name)

    # Preferred: submessage with a 'dateTime' string field in ioLocalDate format
    if hasattr(sub, "dateTime"):
        sub.dateTime = _fmt_io_local(dt)
        return True

    # Fallbacks (only if there is no .dateTime field at all)
    f = container.DESCRIPTOR.fields_by_name.get(field_name)
    if f and f.type == f.TYPE_STRING:
        setattr(container, field_name, _fmt_io_local(dt))
        return True
    if f and f.message_type and f.message_type.full_name.endswith("google.type.TimeOfDay"):
        tod = getattr(container, field_name)
        if hasattr(tod, "hours"):
            tod.hours = dt.hour
        if hasattr(tod, "minutes"):
            tod.minutes = dt.minute
        if hasattr(tod, "seconds"):
            tod.seconds = dt.second
        return True
    return False


def _ensure_template(channel: grpc.Channel, explicit_id: str | None) -> str:
    if explicit_id:
        return explicit_id
    tstub = templates_grpc.TemplatesStub(channel)
    req = template_pb2.DefaultTemplateRequest()
    req.protocol = "FLIGHT_PROTOCOL"
    req.revision = 1
    tmpl = tstub.getDefaultTemplate(req)
    tmpl.name = getattr(constants, "FLIGHT_TEMPLATE_NAME", "ABC Flight Ticket")
    tmpl.description = getattr(
        constants, "FLIGHT_TEMPLATE_DESCRIPTION", "Quickstart Flights")
    tmpl.timezone = getattr(constants, "FLIGHT_TIMEZONE", "Europe/London")
    resp = tstub.createTemplate(tmpl)
    print(f"Template {resp.id} successfully created")
    return resp.id


def run(
    channel: grpc.Channel,
    *,
    carrier_code: str,
    flight_number: str,
    origin_iata: str,
    destination_iata: str,
    pass_template_id: str | None = None,
    departure_iso: str | None = None,
):
    stub = flights_grpc.FlightsStub(channel)

    tmpl_id = _ensure_template(channel, pass_template_id)

    dep_dt = _parse_iso(departure_iso or constants.FLIGHT_DEPARTURE_ISO)
    # Example offsets to build other times
    boarding_dt = dep_dt - \
        datetime.timedelta(minutes=getattr(
            constants, "BOARDING_MIN_BEFORE_DEP", 60))
    gate_close_dt = dep_dt - \
        datetime.timedelta(minutes=getattr(
            constants, "GATE_CLOSE_MIN_BEFORE_DEP", 60))
    arrive_dt = dep_dt + \
        datetime.timedelta(minutes=getattr(
            constants, "ARRIVAL_MIN_AFTER_DEP", 60))

    flt = flight_pb2.Flight()
    flt.carrierCode = carrier_code
    flt.flightNumber = flight_number
    flt.boardingPoint = origin_iata
    flt.deplaningPoint = destination_iata
    flt.passTemplateId = tmpl_id

    # Optional terminals/gates
    if hasattr(flt, "departureTerminal"):
        flt.departureTerminal = getattr(constants, "DEPARTURE_TERMINAL", "1")
    if hasattr(flt, "arrivalTerminal"):
        flt.arrivalTerminal = getattr(constants, "ARRIVAL_TERMINAL", "3")
    if hasattr(flt, "departureGate"):
        flt.departureGate = getattr(constants, "DEPARTURE_GATE", "A3")
    if hasattr(flt, "arrivalGate"):
        flt.arrivalGate = getattr(constants, "ARRIVAL_GATE", "A1")

    # REQUIRED: date message (year/month/day)
    if not _set_date_message(flt, "departureDate", dep_dt):
        raise RuntimeError(
            "Could not set Flight.departureDate (expected a message with year/month/day or similar).")

    # Time submessages with 'dateTime' string
    _set_time_submsg_datetime(flt, "scheduledDepartureTime", dep_dt)
    _set_time_submsg_datetime(flt, "estimatedDepartureTime", dep_dt)
    _set_time_submsg_datetime(flt, "boardingTime",           boarding_dt)
    _set_time_submsg_datetime(flt, "gateClosingTime",        gate_close_dt)
    _set_time_submsg_datetime(flt, "scheduledArrivalTime",   arrive_dt)
    _set_time_submsg_datetime(flt, "estimatedArrivalTime",   arrive_dt)

    # --- create ---
    try:
        resp = stub.createFlight(flt)
        flight_id = getattr(resp, "id", "") or getattr(resp, "flightId", "")
        print(
            f"Created flight: {flight_id} ({carrier_code}{flight_number} {origin_iata}->{destination_iata} on {dep_dt.date()})"
        )
        return flight_id or None, False
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            print(
                f"Flight {carrier_code}{flight_number} {origin_iata}->{destination_iata} already exists on {dep_dt.date()}"
            )
            return None, True
        raise

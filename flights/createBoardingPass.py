# flights/createBoardingPass.py
import grpc
import datetime
from typing import Optional, Tuple

from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc
from passkit.io.flights import boarding_pass_pb2, passenger_pb2
import constants


def _parse_iso_date(iso: str) -> datetime.date:
    dt = datetime.datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.date()


def _set_passenger_details(
    pax: passenger_pb2.Passenger,
    *,
    forename: str,
    surname: str,
    email: str,
) -> bool:
    """
    Populate the required PassengerDetails submessage on Passenger.
    Handles either 'passengerDetails' or 'details' field names.
    """
    # Find the details field name this build uses
    details_field = None
    if hasattr(pax, "passengerDetails"):
        details_field = "passengerDetails"
    elif hasattr(pax, "details"):
        details_field = "details"

    if not details_field:
        return False

    details = getattr(pax, details_field)

    # Set common fields if they exist in your schema
    if hasattr(details, "forename"):
        details.forename = forename
    if hasattr(details, "surname"):
        details.surname = surname
    if hasattr(details, "emailAddress"):
        details.emailAddress = email
    # Nice-to-have: displayName if present
    if hasattr(details, "displayName"):
        details.displayName = f"{forename} {surname}"
    # Optional fallbacks some builds use
    if hasattr(details, "givenName") and not getattr(details, "givenName", ""):
        details.givenName = forename
    if hasattr(details, "familyName") and not getattr(details, "familyName", ""):
        details.familyName = surname
    return True


def _set_date_message(container, field_name: str, d: datetime.date) -> bool:
    """Set container.<field_name> as {year,month,day} or common fallbacks."""
    if not hasattr(container, field_name):
        return False
    f = container.DESCRIPTOR.fields_by_name.get(field_name)
    if f is None:
        return False

    # Preferred: message with year/month/day
    msg = getattr(container, field_name)
    wrote = False
    if hasattr(msg, "year"):
        msg.year = d.year
        wrote = True
    if hasattr(msg, "month"):
        msg.month = d.month
        wrote = True
    if hasattr(msg, "day"):
        msg.day = d.day
        wrote = True
    if wrote:
        return True

    # String fallback "YYYY-MM-DD"
    if f.type == f.TYPE_STRING:
        setattr(container, field_name, d.isoformat())
        return True

    # Integer fallback yyyymmdd
    if f.type in (f.TYPE_INT32, f.TYPE_INT64, f.TYPE_UINT32, f.TYPE_UINT64):
        setattr(container, field_name, d.year * 10000 + d.month * 100 + d.day)
        return True

    return False


def run(
    channel: grpc.Channel,
    *,
    carrier_code: str,
    flight_number: str,
    origin_iata: str,
    destination_iata: str,
    departure_iso: Optional[str] = None,
    pnr: Optional[str] = None,          # <-- now Optional
    sequence_number: str = "1",
    pax_forename: str = "Larry",
    pax_surname: str = "Loyalty",
    pax_email: str = "",
) -> Tuple[Optional[str], bool]:
    """
    Create a boarding pass. Returns (boarding_pass_id, existed=False).
    """
    stub = flights_grpc.FlightsStub(channel)

    dep_date = _parse_iso_date(departure_iso or constants.FLIGHT_DEPARTURE_ISO)

    # Auto PNR if not provided: "<CARRIER><FLIGHT>"
    effective_pnr = (pnr or f"{carrier_code}{flight_number}").replace(" ", "")

    # Passenger
    pax = passenger_pb2.Passenger()
    # top-level fields (kept if your schema has them)
    if hasattr(pax, "forename"):
        pax.forename = pax_forename
    if hasattr(pax, "surname"):
        pax.surname = pax_surname
    if hasattr(pax, "emailAddress"):
        pax.emailAddress = pax_email

    # REQUIRED: PassengerDetails submessage
    if not _set_passenger_details(
        pax, forename=pax_forename, surname=pax_surname, email=pax_email
    ):
        raise RuntimeError(
            "This build requires Passenger.passengerDetails/details, but it wasn't found."
        )

    bpr = boarding_pass_pb2.BoardingPassRecord()
    bpr.carrierCode = carrier_code
    bpr.flightNumber = flight_number
    bpr.boardingPoint = origin_iata
    bpr.deplaningPoint = destination_iata
    if hasattr(bpr, "operatingCarrierPNR"):
        bpr.operatingCarrierPNR = effective_pnr      # <-- here
    if hasattr(bpr, "sequenceNumber"):
        bpr.sequenceNumber = sequence_number

    if not _set_date_message(bpr, "departureDate", dep_date):
        raise RuntimeError("Could not set BoardingPassRecord.departureDate")

    bpr.passenger.CopyFrom(pax)

    # optional extras...
    if hasattr(bpr, "seatNumber"):
        bpr.seatNumber = getattr(constants, "BP_SEAT_NUMBER", "")
    if hasattr(bpr, "boardingZone"):
        bpr.boardingZone = getattr(constants, "BP_BOARDING_ZONE", "")
    if hasattr(bpr, "cabinClass"):
        bpr.cabinClass = getattr(constants, "BP_CABIN_CLASS", "")

    resp = stub.createBoardingPass(bpr)
    bp_id = getattr(resp, "id", "") or getattr(resp, "boardingPassId", "")
    print(
        f"Created boarding pass: {bp_id} ({carrier_code}{flight_number} {origin_iata}->{destination_iata} on {dep_date})")
    return bp_id or None, False

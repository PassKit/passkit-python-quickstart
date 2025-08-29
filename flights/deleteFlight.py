# flights/deleteFlight.py
import grpc
import datetime
from passkit.io.flights import flight_pb2, a_rpc_pb2_grpc


def run(channel: grpc.Channel, *, carrier_code: str, flight_number: str,
        origin_iata: str, destination_iata: str, departure_iso: str) -> None:
    """Delete a Flight given its carrier, flight number, route, and departure date."""
    stub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Parse departure date
    dep_dt = datetime.datetime.fromisoformat(departure_iso)
    if dep_dt.tzinfo is None:
        dep_dt = dep_dt.replace(tzinfo=datetime.timezone.utc)

    flt = flight_pb2.Flight()
    flt.carrierCode = carrier_code
    flt.flightNumber = flight_number
    flt.boardingPoint = origin_iata
    flt.deplaningPoint = destination_iata

    # Set date (year/month/day) if supported
    if hasattr(flt, "departureDate"):
        if hasattr(flt.departureDate, "year"):
            flt.departureDate.year = dep_dt.year
            flt.departureDate.month = dep_dt.month
            flt.departureDate.day = dep_dt.day
        else:
            try:
                flt.departureDate = dep_dt.date().isoformat()
            except Exception:
                pass

    try:
        resp = stub.deleteFlight(flt)
        print(
            f"Deleted flight {carrier_code}{flight_number} {origin_iata}->{destination_iata} on {dep_dt.date()}")
        return resp
    except grpc.RpcError as e:
        print(f"Cleanup: failed to delete flight: {e.details()}")

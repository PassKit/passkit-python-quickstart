# flights/deleteFlightDesignator.py
import grpc
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc, flight_designator_pb2


def run(
    channel: grpc.Channel,
    *,
    carrier_code: str,
    flight_number: str,
    revision: int,
) -> None:
    """
    Delete a flight designator using FlightDesignatorRequest (required: revision).
    Falls back to deleting with FlightDesignator if needed.
    """
    if not carrier_code or not flight_number:
        raise ValueError("carrier_code and flight_number are required")

    stub = flights_grpc.FlightsStub(channel)

    # Preferred: FlightDesignatorRequest with flat fields
    Req = getattr(flight_designator_pb2, "FlightDesignatorRequest", None)
    if Req is not None:
        req = Req()
        # common shapes:
        if hasattr(req, "carrierCode"):
            req.carrierCode = carrier_code
        if hasattr(req, "flightNumber"):
            req.flightNumber = flight_number
        if hasattr(req, "revision"):
            req.revision = revision

        # some builds nest a FlightDesignator inside the Request
        if hasattr(req, "flightDesignator"):
            fd = getattr(req, "flightDesignator")
            if hasattr(fd, "carrierCode"):
                fd.carrierCode = carrier_code
            if hasattr(fd, "flightNumber"):
                fd.flightNumber = flight_number
            if hasattr(fd, "revision"):
                fd.revision = revision

        try:
            stub.deleteFlightDesignator(req)
            print(
                f"Deleted flight designator: {carrier_code}{flight_number} (rev {revision})")
            return
        except AttributeError:
            stub.DeleteFlightDesignator(req)
            print(
                f"Deleted flight designator: {carrier_code}{flight_number} (rev {revision})")
            return

    # Fallback: older shape using FlightDesignator directly
    fd = flight_designator_pb2.FlightDesignator()
    if hasattr(fd, "carrierCode"):
        fd.carrierCode = carrier_code
    if hasattr(fd, "flightNumber"):
        fd.flightNumber = flight_number
    if hasattr(fd, "revision"):
        fd.revision = revision

    stub.deleteFlightDesignator(fd)

    print(
        f"Deleted flight designator: {carrier_code}{flight_number} (rev {revision})")

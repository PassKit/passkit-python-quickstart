"""Reusable flight examples collected behind one consistent interface."""

from passkit.io.common.common_objects_pb2 import Id
from passkit.io.flights.a_rpc_pb2_grpc import FlightsStub
from passkit.io.flights.airport_pb2 import AirportCode
from passkit.io.flights.boarding_pass_pb2 import BoardingPassRequest
from passkit.io.flights.carrier_pb2 import CarrierCode

from flights.createAirport import run as create_airport
from flights.createBoardingPass import run as create_boarding_pass
from flights.createCarrier import run as create_carrier
from flights.createFlight import run as create_flight
from flights.createFlightDesignator import run as create_flight_designator
from flights.deleteAirport import run as delete_airport
from flights.deleteCarrier import run as delete_carrier
from flights.deleteFlight import run as delete_flight
from flights.deleteFlightDesignator import run as delete_flight_designator


def _stub(channel):
    return channel if isinstance(channel, FlightsStub) else FlightsStub(channel)


def get_carrier(channel, carrier_code: str):
    return _stub(channel).getCarrier(CarrierCode(carrierCode=carrier_code))


def update_carrier(channel, carrier):
    return _stub(channel).updateCarrier(carrier)


def get_airport(channel, airport_code: str):
    return _stub(channel).getPort(AirportCode(airportCode=airport_code))


def update_airport(channel, airport):
    return _stub(channel).updatePort(airport)


def get_flight(channel, request):
    return _stub(channel).getFlight(request)


def update_flight(channel, flight):
    return _stub(channel).updateFlight(flight)


def get_flight_designator(channel, request):
    return _stub(channel).getFlightDesignator(request)


def update_flight_designator(channel, designator):
    return _stub(channel).updateFlightDesignator(designator)


def get_boarding_pass_record(channel, request):
    return _stub(channel).getBoardingPassRecord(request)


def get_boarding_pass(channel, pass_id: str):
    return _stub(channel).getBoardingPass(BoardingPassRequest(passId=Id(id=pass_id)))


def update_boarding_pass(channel, boarding_pass):
    return _stub(channel).updateBoardingPass(boarding_pass)


__all__ = [
    "create_airport",
    "create_boarding_pass",
    "create_carrier",
    "create_flight",
    "create_flight_designator",
    "delete_airport",
    "delete_carrier",
    "delete_flight",
    "delete_flight_designator",
    "get_airport",
    "get_boarding_pass",
    "get_boarding_pass_record",
    "get_carrier",
    "get_flight",
    "get_flight_designator",
    "update_airport",
    "update_boarding_pass",
    "update_carrier",
    "update_flight",
    "update_flight_designator",
]

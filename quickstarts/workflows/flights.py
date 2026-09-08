"""Flight boarding-pass lifecycle example."""

from datetime import date, datetime, timedelta, timezone
from random import randint

import grpc
from passkit.io.common.common_objects_pb2 import Date, Id, LocalDateTime, Time
from passkit.io.common.personal_pb2 import Person
from passkit.io.common.protocols_pb2 import PassProtocol
from passkit.io.flights.airport_pb2 import AirportCode, Port
from passkit.io.flights.boarding_pass_pb2 import (
    BoardingPassRecord,
    BoardingPassRecordRequest,
)
from passkit.io.flights.carrier_pb2 import Carrier, CarrierCode
from passkit.io.flights.flight_designator_pb2 import (
    FlightDesignator,
    FlightDesignatorRequest,
)
from passkit.io.flights.flight_pb2 import Flight, FlightRequest
from passkit.io.flights.passenger_pb2 import Passenger

from quickstarts.workflow import Workflow


def passkit_date(value: date) -> Date:
    return Date(year=value.year, month=value.month, day=value.day)


def local_time(value: datetime) -> LocalDateTime:
    return LocalDateTime(dateTime=value.strftime("%Y-%m-%dT%H:%M:%S"))


class FlightsWorkflow(Workflow):
    protocol = PassProtocol.FLIGHT_PROTOCOL

    def execute(self) -> dict[str, str]:
        print("Creating flight images and template")
        self.create_images()
        template_id = self.create_template("Python Quickstart Flight", "#FFEA6C")
        carrier = self.config.carrier_code
        origin = self.config.origin
        destination = self.config.destination
        flight_number = str(randint(100, 999))
        departure = datetime.now(timezone.utc) + timedelta(days=7)
        departure_date = passkit_date(departure.date())

        print("Creating or reusing carrier and airports")
        carrier_created = self._create_or_reuse_carrier(carrier)
        if carrier_created:
            self.remember(
                f"carrier {carrier}",
                lambda: self.service("flights").deleteCarrier(CarrierCode(carrierCode=carrier)),
            )
        for code, created in (
            (
                origin,
                self._create_or_reuse_port(origin, "YYYY", "Origin", "Europe/London"),
            ),
            (
                destination,
                self._create_or_reuse_port(destination, "VHHH", "Destination", "Asia/Hong_Kong"),
            ),
        ):
            if created:
                self.remember(
                    f"airport {code}",
                    lambda value=code: self.service("flights").deletePort(
                        AirportCode(airportCode=value)
                    ),
                )

        print("Creating flight and flight designator")
        request = FlightRequest(
            carrierCode=carrier,
            flightNumber=flight_number,
            boardingPoint=origin,
            deplaningPoint=destination,
            departureDate=departure_date,
        )
        self.service("flights").createFlight(
            Flight(
                carrierCode=carrier,
                flightNumber=flight_number,
                boardingPoint=origin,
                deplaningPoint=destination,
                departureDate=departure_date,
                scheduledDepartureTime=local_time(departure),
                boardingTime=local_time(departure - timedelta(minutes=45)),
                gateClosingTime=local_time(departure - timedelta(minutes=15)),
                scheduledArrivalTime=local_time(departure + timedelta(hours=8)),
                passTemplateId=template_id,
            )
        )
        self.remember("flight", lambda: self.service("flights").deleteFlight(request))

        times = {
            "scheduledDepartureTime": Time(hour=13),
            "boardingTime": Time(hour=12, minute=15),
            "gateClosingTime": Time(hour=12, minute=45),
            "scheduledArrivalTime": Time(hour=21),
        }
        designator = FlightDesignator(
            carrierCode=carrier,
            flightNumber=flight_number,
            revision=1,
            active=True,
            origin=origin,
            destination=destination,
            passTemplateId=template_id,
        )
        for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
            getattr(designator.schedule, day).CopyFrom(
                getattr(designator.schedule, day).__class__(**times)
            )
        self.service("flights").createFlightDesignator(designator)
        designator_request = FlightDesignatorRequest(
            carrierCode=carrier, flightNumber=flight_number, revision=1
        )
        self.remember(
            "flight designator",
            lambda: self.service("flights").deleteFlightDesignator(designator_request),
        )
        self.service("flights").getFlight(request)
        self.service("flights").getFlightDesignator(designator_request)

        print("Creating and reading boarding pass")
        response = self.service("flights").createBoardingPass(
            BoardingPassRecord(
                operatingCarrierPNR=f"PY{flight_number}",
                boardingPoint=origin,
                deplaningPoint=destination,
                carrierCode=carrier,
                flightNumber=flight_number,
                departureDate=departure_date,
                passenger=Passenger(
                    passengerDetails=Person(
                        displayName="Python Passenger",
                        forename="Python",
                        surname="Passenger",
                        emailAddress=self.config.recipient_email
                        or "python.flight@dummy.passkit.com",
                    )
                ),
                sequenceNumber=123,
                seatNumber="12A",
                **{"class": "Economy"},
            )
        )
        boarding_pass = response.boardingPasses[0]
        boarding_request = BoardingPassRecordRequest(passId=Id(id=boarding_pass.id))
        self.remember(
            "boarding pass",
            lambda: self.service("flights").deleteBoardingPass(boarding_request),
        )
        self.service("flights").getBoardingPassRecord(boarding_request)

        print(f"Created boarding pass: {boarding_pass.id}")
        return {"boardingPassId": boarding_pass.id, "boardingPassUrl": boarding_pass.url}

    def _create_or_reuse_carrier(self, code: str) -> bool:
        try:
            self.service("flights").createCarrier(
                Carrier(
                    airlineName="Python Quickstart Airline",
                    iataCarrierCode=code,
                    passTypeIdentifier=self.config.apple_certificate,
                )
            )
            return True
        except grpc.RpcError as error:
            if error.code() != grpc.StatusCode.ALREADY_EXISTS:
                raise
            self.service("flights").getCarrier(CarrierCode(carrierCode=code))
            print(f"Carrier {code} already exists; reusing it.")
            return False

    def _create_or_reuse_port(self, code: str, icao: str, city: str, timezone_name: str) -> bool:
        try:
            self.service("flights").createPort(
                Port(
                    iataAirportCode=code,
                    icaoAirportCode=icao,
                    airportName=f"Python Quickstart {city} Airport",
                    cityName=city,
                    countryCode="GB" if city == "Origin" else "HK",
                    timezone=timezone_name,
                )
            )
            return True
        except grpc.RpcError as error:
            if error.code() != grpc.StatusCode.ALREADY_EXISTS:
                raise
            self.service("flights").getPort(AirportCode(airportCode=code))
            print(f"Airport {code} already exists; reusing it.")
            return False

import grpc
import io.flights.flight_designator_pb2 as flight_designator_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import datetime


def create_flight_designator():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Create flight designator
    flightDesignator = flight_designator_pb2.FlightDesignator()
    flightDesignator.CarrierCode = ""
    flightDesignator.FlightNumber = "1234"
    flightDesignator.Revision = 0
    flightDesignator.Schedule("ADP")
    flightDesignator.PassTemplateId = ""  # Created when creating flight
    flightDesignator.Origin = "YYY"
    flightDesignator.Origin = "ADP"

    boardingTime = datetime.time(13, 0, 0)
    scheduledDeparture = datetime.time(14, 0, 0)
    scheduledArrival = datetime.time(15, 0, 0)
    gateTime = datetime.time(13, 30, 0)

    flightTimes = flight_designator_pb2.FlightTimes()
    flightTimes.BoardingTime = boardingTime
    flightTimes.ScheduledDepartureTime = scheduledDeparture
    flightTimes.ScheduledArrivalTime = scheduledArrival
    flightTimes.GateClosingTime = gateTime

    schedule = flight_designator_pb2.FlightsSchedule()
    schedule.Monday = flightTimes
    schedule.Tuesday = flightTimes
    schedule.Wednesday = flightTimes
    schedule.Thursday = flightTimes
    schedule.Friday = flightTimes
    schedule.Saturday = flightTimes
    schedule.Sunday = flightTimes

    flightDesignator.Schedule = schedule

    response = flightsStub.createFlightDesignator(flightDesignator)
    print(response)


create_flight_designator()

import grpc
import passkit_io.flights.flight_designator_pb2 as flight_designator_pb2
import passkit_io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import datetime


def create_flight_designator():
 # Read the CA, certificate, and private key files
    with open('../certs/ca-chain.pem', 'rb') as ca_file:
        root_certificates = ca_file.read()

    with open('../certs/certificate.pem', 'rb') as cert_file:
        certificate_chain = cert_file.read()

    with open('../certs/key.pem', 'rb') as key_file:
        private_key = key_file.read()

    # Create SSL credentials for gRPC
    credentials = grpc.ssl_channel_credentials(
        root_certificates=root_certificates,
        private_key=private_key,
        certificate_chain=certificate_chain
    )

    # Create a secure gRPC channel
    channel = grpc.secure_channel('grpc.pub1.passkit.io:443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Create flight designator
    flightDesignator = flight_designator_pb2.FlightDesignator()
    flightDesignator.carrierCode = ""
    flightDesignator.flightNumber = "1234"
    flightDesignator.revision = 0
    flightDesignator.schedule("ADP")
    flightDesignator.passTemplateId = ""  # Created when creating flight
    flightDesignator.origin = "YYY"
    flightDesignator.origin = "ADP"

    boardingTime = datetime.time(13, 0, 0)
    scheduledDeparture = datetime.time(14, 0, 0)
    scheduledArrival = datetime.time(15, 0, 0)
    gateTime = datetime.time(13, 30, 0)

    flightTimes = flight_designator_pb2.FlightTimes()
    flightTimes.boardingTime = boardingTime
    flightTimes.scheduledDepartureTime = scheduledDeparture
    flightTimes.scheduledArrivalTime = scheduledArrival
    flightTimes.gateClosingTime = gateTime

    schedule = flight_designator_pb2.FlightsSchedule()
    schedule.monday = flightTimes
    schedule.tuesday = flightTimes
    schedule.wednesday = flightTimes
    schedule.thursday = flightTimes
    schedule.friday = flightTimes
    schedule.saturday = flightTimes
    schedule.sunday = flightTimes

    flightDesignator.Schedule.CopyFrom(schedule)

    response = flightsStub.createFlightDesignator(flightDesignator)
    print(response)


create_flight_designator()

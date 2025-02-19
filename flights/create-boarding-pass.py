import grpc
import passkit_io.flights.boarding_pass_pb2 as boarding_pass_pb2
import passkit_io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import passkit_io.flights.passenger_pb2 as passenger_pb2
import datetime


def create_boarding_pass():
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

    # Create boarding pass
    boardingPass = boarding_pass_pb2.BoardingPassRecord()
    boardingPass.carrierCode = ""
    boardingPass.boardingPoint = "ATH"
    boardingPass.deplaningPoint = "LHR"
    boardingPass.operatingCarrierPNR = ""
    boardingPass.flightNumber = "1234"
    boardingPass.sequenceNumber = "1"

    departureDate = datetime.datetime.now(datetime.timezone.utc)
    passenger = passenger_pb2.Passenger
    passenger.forename = "Larry"
    passenger.surname = "Loyalty"
    passenger.emailAddress = ""

    boardingPass.passenger.CopyFrom(passenger)
    boardingPass.departureDate = departureDate
    response = flightsStub.createBoardingPass(boardingPass)
    print(response)


create_boarding_pass()

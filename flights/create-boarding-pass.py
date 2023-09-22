import grpc
import io.flights.boarding_pass_pb2 as boarding_pass_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import io.flights.passenger_pb2 as passenger_pb2
import datetime


def create_boarding_pass():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Create boarding pass
    boardingPass = boarding_pass_pb2.BoardingPassRecord()
    boardingPass.CarrierCode = ""
    boardingPass.BoardingPoint = "ATH"
    boardingPass.DeplaningPoint = "LHR"
    boardingPass.OperatingCarrierPNR = ""
    boardingPass.FlightNumber = "1234"
    boardingPass.SequenceNumber = "1"

    departureDate = datetime.datetime.strptime(
        "10/9/2023", "%d/%m/%Y").timestamp()
    passenger = passenger_pb2.Passenger
    passenger.Forename = "Larry"
    passenger.Surname = "Loyalty"
    passenger.EmailAddress = ""

    boardingPass.Passenger = passenger
    boardingPass.DepartureDate = departureDate
    response = flightsStub.createBoardingPass(boardingPass)
    print(response)


create_boarding_pass()

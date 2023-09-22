import grpc
import io.flights.flight_pb2 as flight_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import datetime


def delete_flight():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Delete flight
    flight = flight_pb2.Flight()
    flight.CarrierCode = ""
    flight.FlightNumber = "1234"
    flight.BoardingPoint = "ATH"
    flight.DeplaningPoint = "TLV"

    departureDate = datetime.datetime.strptime(
        "10/9/2023", "%d/%m/%Y").timestamp()
    departureTime = datetime.time(13, 0, 0)
    flight.DepartureDate = departureDate
    flight.ScheduledDepartureTime = departureTime

    response = flightsStub.deleteFlight(flight)
    print(response)


delete_flight()

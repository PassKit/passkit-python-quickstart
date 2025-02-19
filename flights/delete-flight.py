import grpc
import passkit_io.flights.flight_pb2 as flight_pb2
import passkit_io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
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
    flight.carrierCode = ""
    flight.flightNumber = "1234"
    flight.boardingPoint = "ATH"
    flight.deplaningPoint = "TLV"

    departureDate = datetime.datetime.now(datetime.timezone.utc)
    departureTime = datetime.time(13, 0, 0)
    flight.departureDate = departureDate
    flight.scheduledDepartureTime = departureTime

    response = flightsStub.deleteFlight(flight)
    print(response)


delete_flight()

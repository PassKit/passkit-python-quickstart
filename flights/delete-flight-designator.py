import grpc
import io.flights.flight_designator_pb2 as flight_designator_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import datetime


def delete_flight_designator():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Delete flight designator
    flightDesignator = flight_designator_pb2.FlightDesignator()
    flightDesignator.CarrierCode = ""
    flightDesignator.FlightNumber = "1234"
    flightDesignator.Revision = 0

    response = flightsStub.deleteFlightDesignator(flightDesignator)
    print(response)


delete_flight_designator()

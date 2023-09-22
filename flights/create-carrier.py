import grpc
import io.flights.carrier_pb2 as carrier_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def create_carrier():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Create carrier
    carrier = carrier_pb2.Carrier()
    carrier.AirlineName = "ABC Airline"
    carrier.IataCarrierCode = ""  # Your IATA carrier code
    carrier.IcaoCarrierCode = ""  # Your ICAO carrier code
    carrier.PassTypeIdentifier = ""  # Insert your apple certificate id here
    response = flightsStub.createCarrier(carrier)
    print(response)


create_carrier()

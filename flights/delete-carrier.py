import grpc
import io.flights.carrier_pb2 as carrier_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def delete_carrier():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Delete carrier
    carrier = carrier_pb2.Carrier()
    carrier.CarrierCode = "YYY"
    response = flightsStub.deleteCarrier(carrier)
    print(response)


delete_carrier()

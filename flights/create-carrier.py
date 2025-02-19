import grpc
import passkit_io.flights.carrier_pb2 as carrier_pb2
import passkit_io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def create_carrier():
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

    # Create carrier
    carrier = carrier_pb2.Carrier()
    carrier.airlineName = "ABC Airline"
    carrier.iataCarrierCode = ""  # Your IATA carrier code
    carrier.icaoCarrierCode = ""  # Your ICAO carrier code
    carrier.passTypeIdentifier = ""  # Insert your apple certificate id here
    response = flightsStub.createCarrier(carrier)
    print(response)


create_carrier()

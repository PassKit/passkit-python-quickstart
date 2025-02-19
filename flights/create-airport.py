import grpc
import passkit_io.flights.airport_pb2 as airport_pb2
import passkit_io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def create_airport():
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

    # Create airport
    airport = airport_pb2.Port()
    airport.airportName = "ABC Airport"
    airport.cityName = "London"
    airport.iataAirportCode = ""  # Your airport IATA code
    airport.icaoAirportCode = ""  # Your airport ICAO code
    airport.countryCode = "IE"
    airport.timezone("Europe/London")

    response = flightsStub.createPort(airport)
    print(response)


create_airport()

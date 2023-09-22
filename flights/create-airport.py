import grpc
import io.flights.airport_pb2 as airport_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def create_airport():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Create airport
    airport = airport_pb2.Port()
    airport.AirportName = "ABC Airport"
    airport.CityName = "London"
    airport.IataAirportCode = ""  # Your airport IATA code
    airport.IcaoAirportCode = ""  # Your airport ICAO code
    airport.CountryCode = "IE"
    airport.Timezone("Europe/London")

    response = flightsStub.createPort(airport)
    print(response)


create_airport()

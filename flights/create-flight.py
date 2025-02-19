import grpc
import passkit_io.flights.flight_pb2 as flight_pb2
import passkit_io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import passkit_io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import passkit_io.common.template_pb2 as template_pb2
import google.protobuf.timestamp_pb2 as timestamp_pb2
import datetime


def create_flight():
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

    # Create templates stub
    templatesStub = a_rpc_templates_pb2_grpc.TemplatesStub(channel)

    # Create template
    templateRequest = template_pb2.DefaultTemplateRequest()
    templateRequest.protocol = "FLIGHT_PROTOCOL"
    templateRequest.revision = 1

    template = templatesStub.getDefaultTemplate(templateRequest)

    template.name = "ABC Flight Ticket"
    template.description = "Quickstart Flights"
    template.timezone = "Europe/London"

    # Make a note of the id for creating the flight designator
    try:
        response = templatesStub.createTemplate(template)
        print("Template " + response.id + " successfully created")
    except grpc.RpcError as e:
        print("Failed to create template", e.details())


    # Create flight
    flight = flight_pb2.Flight()
    flight.carrierCode = ""
    flight.flightNumber = "1234"
    flight.boardingPoint = "ATH"
    flight.deplaningPoint = "TLV"

    departureDate = datetime.datetime.now(datetime.timezone.utc)
    departureTime = datetime.time(13, 0, 0)
    flight.departureDate = departureDate
    flight.scheduledDepartureTime = departureTime
    flight.passTemplateId = response.id

    response = flightsStub.createFlight(flight)
    print(response)


create_flight()

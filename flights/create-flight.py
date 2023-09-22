import grpc
import io.flights.flight_pb2 as flight_pb2
import io.flights.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import io.common.template_pb2 as template_pb2
import google.protobuf.timestamp_pb2 as timestamp_pb2
import datetime


def create_flight():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    flightsStub = a_rpc_pb2_grpc.FlightsStub(channel)

    # Create templates stub
    templatesStub = a_rpc_templates_pb2_grpc.TemplatesStub(channel)

    # Create template
    templateRequest = template_pb2.DefaultTemplateRequest()
    templateRequest.Protocol = "FLIGHT_PROTOCOL"
    templateRequest.Revision = 1

    template = templatesStub.getDefaultTemplate(templateRequest)

    template.Name = "ABC Flight Ticket"
    template.Description = "Quickstart Flights"
    template.Timezone = "Europe/London"

    # Make a note of the id for creating the flight designator
    templateId = templatesStub.createTemplate(template)

    # Create flight
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
    flight.PassTemplateId = templateId.Id

    response = flightsStub.createFlight(flight)
    print(response)


create_flight()

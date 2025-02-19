import grpc
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import passkit_io.single_use_coupons.a_rpc_pb2_grpc as coupons_a_rpc_pb2_grpc
import passkit_io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import passkit_io.event_tickets.a_rpc_pb2_grpc as events_a_rpc_pb2_grpc
import passkit_io.flights.a_rpc_pb2_grpc as flights_a_rpc_pb2_grpc


def grpcConnection(): 
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

    # Membership Stub 
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Coupons Stub
    couponsStub = coupons_a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # Events Stub
    eventStub = events_a_rpc_pb2_grpc.EventTicketsStub(channel)

    # Flights Stub
    flightStub = flights_a_rpc_pb2_grpc.FlightsStub(channel)

    # Create templates stub
    templatesStub = a_rpc_templates_pb2_grpc.TemplatesStub(channel)

    grpcConnection()

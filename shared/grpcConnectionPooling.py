import grpc
import threading
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import passkit_io.single_use_coupons.a_rpc_pb2_grpc as coupons_a_rpc_pb2_grpc
import passkit_io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import passkit_io.event_tickets.a_rpc_pb2_grpc as events_a_rpc_pb2_grpc
import passkit_io.flights.a_rpc_pb2_grpc as flights_a_rpc_pb2_grpc

def grpcConnectionPooling():
        # Initialize the channel pool and current index correctly
    channel_pool = []
    current_index = 0  # Use an integer directly and control access with a lock
    lock = threading.Lock()

    def build_ssl_context():
        # Read the CA, certificate, and private key files
        with open('../certs/ca-chain.pem', 'rb') as ca_file:
            root_certificates = ca_file.read()
        with open('../certs/certificate.pem', 'rb') as cert_file:
            certificate_chain = cert_file.read()
        with open('../certs/key.pem', 'rb') as key_file:
            private_key = key_file.read()

        # Create SSL credentials for gRPC
        return grpc.ssl_channel_credentials(
            root_certificates=root_certificates,
            private_key=private_key,
            certificate_chain=certificate_chain
        )

    def initialize_channels(pool_size):
        host = "grpc.pub1.passkit.io"
        port = 443
        ssl_context = build_ssl_context()

        for _ in range(pool_size):
            channel = grpc.secure_channel(f"{host}:{port}", ssl_context)
            channel_pool.append(channel)

    def get_channel():
        nonlocal current_index
        with lock:
            channel = channel_pool[current_index]
            current_index = (current_index + 1) % len(channel_pool)
            return channel

    def shutdown_channels():
        for channel in channel_pool:
            channel.close()
        channel_pool.clear()

    pool_size = 5
    initialize_channels(pool_size)
    try:
        channel = get_channel()
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
    finally:
        shutdown_channels()
    grpcConnectionPooling()

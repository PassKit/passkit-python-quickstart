import grpc
import passkit_io.core.a_rpc_distribution_pb2_grpc as distribution_pb2_grpc
import passkit_io.common.distribution_pb2 as distribution_pb2


def resend_welcome_email():
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

    # Access the distributionStub from passkit_io.member
    distributionStub = distribution_pb2_grpc.DistributionStub(channel)

    emailRequest = distribution_pb2.EmailDistributionRequest()
    emailRequest.id = ""
    emailRequest.protocol = "MEMBERSHIP"

    try:
        response = distributionStub.sendWelcomeEmail(emailRequest)
        print("Resent welcome email" )
    except grpc.RpcError as e:
        print("Failed to resend welcome email", e.details())

resend_welcome_email()

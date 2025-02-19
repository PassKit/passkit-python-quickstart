import grpc
import passkit_io.member.member_pb2 as member_pb2
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def earn_points():
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

    # Access the MembersStub 
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Earn Points
    earnPointsRequest = member_pb2.EarnBurnPointsRequest()
    earnPointsRequest.id = "41Nq6AvJQzDNtMJgliwB4c"  # Id of member of points to earn points
    earnPointsRequest.points = 100
    earnPointsRequest.secondaryPoints = 0
    earnPointsRequest.tierPoints = 0
    try:
        response = membersStub.earnPoints(earnPointsRequest)
        print("Member " + response.id + " has earned " + str(earnPointsRequest.points))
    except grpc.RpcError as e:
        print("Failed to earn points", e.details())


earn_points()

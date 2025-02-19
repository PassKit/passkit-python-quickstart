import grpc
import passkit_io.member.member_pb2 as member_pb2
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def burn_points():
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

    # Burn Points
    burnPointsRequest = member_pb2.EarnBurnPointsRequest()
    burnPointsRequest.id = ""  # Id of member of points to burn
    burnPointsRequest.points = 100
    burnPointsRequest.secondaryPoints = 0
    burnPointsRequest.tierPoints = 0
    try:
        response = membersStub.burnPoints(burnPointsRequest)
        print("Member " + response.id + " has burned " + str(burnPointsRequest.points))
    except grpc.RpcError as e:
        print("Failed to burn points", e.details())



burn_points()

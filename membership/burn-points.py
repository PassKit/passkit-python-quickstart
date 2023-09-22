import grpc
import io.member.member_pb2 as member_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def burn_points():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Burn Points
    burnPointsRequest = member_pb2.EarnBurnPointsRequest()
    burnPointsRequest.Id = ""  # Id of member of points to burn
    burnPointsRequest.Points = 100
    burnPointsRequest.SecondaryPoints = 0
    burnPointsRequest.TierPoints = 0
    response = membersStub.burnPoints(burnPointsRequest)
    print(response)


burn_points()

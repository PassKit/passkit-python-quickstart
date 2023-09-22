import grpc
import io.member.member_pb2 as member_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def earn_points():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Earn Points
    earnPointsRequest = member_pb2.EarnBurnPointsRequest()
    earnPointsRequest.Id = ""  # Id of member of points to be increased
    earnPointsRequest.Points = 100
    earnPointsRequest.SecondaryPoints = 0
    earnPointsRequest.TierPoints = 0
    response = membersStub.earnPoints(earnPointsRequest)
    print(response)


earn_points()

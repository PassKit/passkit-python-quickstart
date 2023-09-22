import grpc
import io.member.member_pb2 as member_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def check_in():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Check in member
    checkInRequest = member_pb2.MemberCheckInOutRequest()
    checkInRequest.MemberId = ""  # Member Id tp check in
    checkInRequest.Lat = 0  # Latitude of check in location
    checkInRequest.Lon = 0  # Longitude of check in location
    checkInRequest.Address = ""  # Check in Address
    response = membersStub.checkInMember(checkInRequest)
    print(response)


check_in()

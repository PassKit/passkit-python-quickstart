import grpc
import io.member.member_pb2 as member_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def check_out():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Check out member
    checkOutRequest = member_pb2.MemberCheckInOutRequest()
    checkOutRequest.MemberId = ""  # Member Id tp check out
    checkOutRequest.Lat = 0  # Latitude of check out location
    checkOutRequest.Lon = 0  # Longitude of check out location
    checkOutRequest.Address = ""  # Check out Address
    response = membersStub.checkOutMember(checkOutRequest)
    print(response)


check_out()

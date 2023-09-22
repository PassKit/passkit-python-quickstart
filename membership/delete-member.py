import grpc
import io.member.member_pb2 as member_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def delete_member():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Delete member
    member = member_pb2.Member()
    member.Id = ""  # Id of member to delete
    response = membersStub.deleteMember(member)
    print(response)


delete_member()

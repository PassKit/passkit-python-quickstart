import grpc
import io.member.member_pb2 as member_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import io.common.personal_pb2 as personal_pb2


def update_member():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Update member
    # More fields can be updated see https://docs.passkit.io/protocols/member/#operation/Members_updateMember for more
    member = member_pb2.Member()
    member.Id = ""  # Id of member to update
    member.ProgramId = ""  # Get from dashboard or createProgram call
    member.TierId = ""  # Get from dashboard or createTier call

    person = personal_pb2.Person()
    person.DisplayName = "Loyal Larry"
    person.EmailAddress = ""

    member.Person = person
    response = membersStub.updateMember(member)
    print(response)


update_member()

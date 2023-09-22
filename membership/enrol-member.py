import grpc
import io.member.member_pb2 as member_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import io.common.personal_pb2 as personal_pb2


def enrol_member():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Create member
    member = member_pb2.Member()
    member.ProgramId = ""  # Get from dashboard or createProgram call
    member.TierId = ""  # Get from dashboard or createTier call

    person = personal_pb2.Person()
    person.DisplayName = "Loyal Larry"
    person.EmailAddress = ""

    member.Person = person
    response = membersStub.enrolMember(member)
    print(response)


enrol_member()

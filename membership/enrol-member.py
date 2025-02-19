import grpc
import passkit_io 
import passkit_io.member
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
from passkit_io.common.personal_pb2 import Person

def enrol_member():
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

    # Access the MembersStub from passkit_io.member
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Create and enrol a member
    member = passkit_io.member.get_member_pb2().Member()
    member.programId = ""  # Replace with valid program ID
    member.tierId = ""  # Replace with valid tier ID

    person = Person()
    person.displayName = "Percy PassKit"
    person.surname = "PassKit"
    person.forename = "Percy"
    person.emailAddress = ""

    member.person.CopyFrom(person)

    # Enrol the member
    try:
        response = membersStub.enrolMember(member)
        print("Member enrolled successfully: See their pass here:https://pub1.pskt.io/" + response.id)
    except grpc.RpcError as e:
        print("Failed to enrol member:", e.details())

# Call the function
enrol_member()

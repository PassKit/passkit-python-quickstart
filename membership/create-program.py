import grpc
import passkit_io.member
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
from passkit_io.common.project_pb2 import ProjectStatus 


def create_program():
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

    program = passkit_io.member.get_program_pb2().Program()
    program.name = "Quickstart Program"
    program.status.append("PROJECT_ACTIVE_FOR_OBJECT_CREATION") 
    program.status.append("PROJECT_DRAFT")


    try:
        response = membersStub.createProgram(program)
        print("Program " + response.id + " successfully created")
    except grpc.RpcError as e:
        print("Failed to create program", e.details())

create_program()

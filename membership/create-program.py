import grpc
import io.member.program_pb2 as program_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def create_program():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)
    program = program_pb2.Program()
    program.Name = "Quickstart Program"
    program.Status = [1, 4]
    response = membersStub.createProgram(program)
    print(response)


create_program()

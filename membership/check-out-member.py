import grpc
import passkit_io.member.member_pb2 as member_pb2
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def check_out():
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

    # Check out member

    # Check in member
    checkOutRequest = member_pb2.MemberCheckInOutRequest()
    checkOutRequest.memberId = ""  # Member Id tp check in
    checkOutRequest.lat = 0  # Latitude of check in location
    checkOutRequest.lon = 0  # Longitude of check in location
    checkOutRequest.address = ""  # Check in Address
    try:
        response = membersStub.checkOutMember(checkOutRequest)
        print("Member " + response.id + " successfully checked in")
    except grpc.RpcError as e:
        print("Failed to check in member", e.details())


check_out()

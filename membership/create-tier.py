import grpc
import passkit_io
import passkit_io.core.a_rpc_templates_pb2
import passkit_io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import passkit_io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import passkit_io.core 
import passkit_io.common.template_pb2 as template_pb2


def create_tier():
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
    # Create templates stub
    templatesStub = a_rpc_templates_pb2_grpc.TemplatesStub(channel)

    # Create template
    templateRequest = template_pb2.DefaultTemplateRequest()
    templateRequest.protocol = "MEMBERSHIP"
    templateRequest.revision = 1

    template = templatesStub.getDefaultTemplate(templateRequest)

    template.name = "Quickstart Base Tier"
    template.description = "Quickstart Base Tier Pass"
    template.timezone = "Europe/London"

    try:
        response = templatesStub.createTemplate(template)
        print("Template " + response.id + " successfully created")
    except grpc.RpcError as e:
        print("Failed to create template", e.details())

    # Create tier
    tier = passkit_io.member.get_tier_pb2().Tier()
    tier.id = "base"
    tier.tierIndex = 1
    tier.name = "Quickstart Base Tier"
    tier.passTemplateId = response.id
    tier.programId = ""   # Get from dashboard or createProgram call
    tier.timezone = "Europe/London"


    try:
        response = membersStub.createTier(tier)
        print("Tier " + response.id + " successfully created")
    except grpc.RpcError as e:
        print("Failed to create tier", e.details())

create_tier()

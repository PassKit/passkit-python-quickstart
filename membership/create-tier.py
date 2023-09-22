import grpc
import io.member.tier_pb2 as tier_pb2
import io.member.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import io.common.template_pb2 as template_pb2


def create_tier():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create members stub
    membersStub = a_rpc_pb2_grpc.MembersStub(channel)

    # Create templates stub
    templatesStub = a_rpc_templates_pb2_grpc.TemplatesStub(channel)

    # Create template
    templateRequest = template_pb2.DefaultTemplateRequest()
    templateRequest.Protocol = "MEMBERSHIP"
    templateRequest.Revision = 1

    template = templatesStub.getDefaultTemplate(templateRequest)

    template.Name = "Quickstart Base Tier"
    template.Description = "Quickstart Base Tier Pass"
    template.Timezone = "Europe/London"

    templateId = templatesStub.createTemplate(template)

    # Create tier
    tier = tier_pb2.Tier()
    tier.Id = "base"
    tier.Name = "Quickstart Base Tier"
    tier.PassTemplateId = templateId.Id
    tier.ProgramId = ""   # Get from dashboard or createProgram call
    tier.Timezone = "Europe/London"
    response = membersStub.createTier(tier)
    print(response)


create_tier()

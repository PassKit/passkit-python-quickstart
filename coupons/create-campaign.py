import grpc
import passkit_io.single_use_coupons.campaign_pb2 as campaign_pb2
import passkit_io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def create_campaign():
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

    # Create a stub
    couponsStub = a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # Create campaign
    campaign = campaign_pb2.CouponCampaign()
    campaign.name = "Quickstart Campaign"
    campaign.status.append("PROJECT_ACTIVE_FOR_OBJECT_CREATION") 
    campaign.status.append("PROJECT_DRAFT")
    response = couponsStub.createCouponCampaign(campaign)
    print(response)


create_campaign()

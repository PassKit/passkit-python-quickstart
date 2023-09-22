import grpc
import io.single_use_coupons.campaign_pb2 as campaign_pb2
import io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def create_campaign():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    couponsStub = a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # Create campaign
    campaign = campaign_pb2.CouponCampaign()
    campaign.Name = "Quickstart Campaign"
    campaign.Status = [1, 4]
    response = couponsStub.createCouponCampaign(campaign)
    print(response)


create_campaign()

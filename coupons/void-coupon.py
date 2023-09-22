import grpc
import io.single_use_coupons.coupon_pb2 as coupon_pb2
import io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def void_coupon():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    couponsStub = a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # Void coupon
    coupon = coupon_pb2.Coupon()
    coupon.Id = ""  # Id of coupon to void
    coupon.OfferId = ""  # Get offerId from createOffer call or dashboard
    coupon.CampaignId = ""  # Get campaignId from createCampaign call or dashboard

    response = couponsStub.update(coupon)
    print(response)


void_coupon()

import grpc
import io.single_use_coupons.coupon_pb2 as coupon_pb2
import io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def redeem_coupon():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    couponsStub = a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # Redeem coupon
    coupon = coupon_pb2.Coupon()
    coupon.Id = ""  # Id of coupon to void
    coupon.CampaignId = ""  # Get campaignId from createCampaign call or dashboard
    coupon.Status = 1

    response = couponsStub.redeemCoupon(coupon)
    print(response)


redeem_coupon()

import grpc
import io.single_use_coupons.coupon_pb2 as coupon_pb2
import io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def list_coupons():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    couponsStub = a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # List coupons by campaignId
    listCouponRequest = coupon_pb2.ListRequest()
    listCouponRequest.CouponCampaignId = ""  # Campaign Id of coupons to list

    response = couponsStub.listCouponsByCouponCampaign(listCouponRequest)
    print(response)


list_coupons()

import grpc
import io.single_use_coupons.coupon_pb2 as coupon_pb2
import io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import io.common.personal_pb2 as personal_pb2


def create_coupon():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    couponsStub = a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # Create coupon
    coupon = coupon_pb2.Coupon()
    coupon.OfferId = ""  # Get offerId from createOffer call or dashboard
    coupon.CampaignId = ""  # Get campaignId from createCampaign call or dashboard
    coupon.Sku = ""

    person = personal_pb2.Person()
    person.DisplayName = "Loyal Larry"
    person.EmailAddress = ""

    coupon.Person = person
    response = couponsStub.createCoupon(coupon)
    print(response)


create_coupon()

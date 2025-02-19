import grpc
import passkit_io.single_use_coupons.coupon_pb2 as coupon_pb2
import passkit_io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def void_coupon():
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

    # Void coupon
    coupon = coupon_pb2.Coupon()
    coupon.id = "2saS6qfTbuMpMZhHW71Sgz"  # Id of coupon to void
    coupon.offerId = "6Ju8CP1y05fBz6hwAUhw2Y"  # Get offerId from createOffer call or dashboard
    coupon.campaignId = "0S5FnxW9i2e0fBa8chRhBw"  # Get campaignId from createCampaign call or dashboard

    response = couponsStub.voidCoupon(coupon)
    print("Coupon Voided")


void_coupon()

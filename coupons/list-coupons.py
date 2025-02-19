import grpc
import passkit_io.single_use_coupons.coupon_pb2 as coupon_pb2
import passkit_io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc


def list_coupons():
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

    # List coupons by campaignId
    listCouponRequest = coupon_pb2.ListRequest()
    listCouponRequest.couponCampaignId = "0S5FnxW9i2e0fBa8chRhBw"  # Campaign Id of coupons to list

    try:
        couponsList = couponsStub.listCouponsByCouponCampaign(listCouponRequest, timeout=30)
        for data in couponsList:
            # This will print each member data received from the stream
            print("Received:", data)

        print("Stream ended successfully.")
    except grpc.RpcError as e:
        print(f"gRPC Error: {e.code()} - {e.details()}")
    except Exception as e:
        print(f"Error: {e}")


list_coupons()

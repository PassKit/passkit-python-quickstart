import grpc
import passkit_io.single_use_coupons.offer_pb2 as offer_pb2
import passkit_io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import passkit_io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import passkit_io.common.template_pb2 as template_pb2
import google.protobuf.timestamp_pb2 as timestamp_pb2
import datetime


def create_offer():
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

    # Create templates stub
    templatesStub = a_rpc_templates_pb2_grpc.TemplatesStub(channel)

    # Create template
    templateRequest = template_pb2.DefaultTemplateRequest()
    templateRequest.protocol = "SINGLE_USE_COUPON"
    templateRequest.revision = 1

    template = templatesStub.getDefaultTemplate(templateRequest)

    template.name = "Quickstart Base Offer"
    template.description = "Quickstart Base Offer Pass"
    template.timezone = "Europe/London"

    try:
        response = templatesStub.createTemplate(template)
        print("Template " + response.id + " successfully created")
    except grpc.RpcError as e:
        print("Failed to create template", e.details())

    # Create offer
    offer = offer_pb2.CouponOffer()
    offer.id = "Base Offer"
    offer.offerTitle = "Base Offer Title"
    offer.offerShortTitle = "Base Offer"
    offer.offerDetails = "Base Offer Details"
    offer.offerFinePrint = "Base Offer fine print"
    offer.beforeRedeemPassTemplateId = response.id

    # Get current UTC time as timezone-aware datetime
    issueStartDate = datetime.datetime.now(datetime.timezone.utc)
    issueEndDate = datetime.datetime.now(datetime.timezone.utc)
    redemptionStartDate = datetime.datetime.now(datetime.timezone.utc)
    redemptionEndDate = datetime.datetime.now(datetime.timezone.utc)

    # Convert the datetime objects to Timestamp
    redemptionSettings = offer_pb2.RedemptionSettings()
    redemptionSettings.redemptionStartDate = redemptionStartDate

    redemptionSettings.redemptionEndDate = redemptionEndDate

    couponExpirySettings = offer_pb2.CouponExpirySettings()
    couponExpirySettings.couponExpiryType = "AUTO_EXPIRE_REDEMPTION_END_DATE"

    offer.issueStartDate = issueStartDate

    offer.issueEndDate = issueEndDate

    # Assign settings
    offer.redemptionSettings.CopyFrom(redemptionSettings)
    offer.couponExpirySettings.CopyFrom(couponExpirySettings)
    offer.campaignId = ""  # Get from campaignId from createCampaign call or dashboard
    offer.ianaTimezone = "Europe/London"

    # Create coupon offer
    response = couponsStub.createCouponOffer(offer)
    print(response)


create_offer()

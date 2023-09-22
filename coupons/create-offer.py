import grpc
import io.single_use_coupons.offer_pb2 as offer_pb2
import io.single_use_coupons.a_rpc_pb2_grpc as a_rpc_pb2_grpc
import io.core.a_rpc_templates_pb2_grpc as a_rpc_templates_pb2_grpc
import io.common.template_pb2 as template_pb2
import google.protobuf.timestamp_pb2 as timestamp_pb2
import datetime


def create_offer():
    # Create channel credentials
    credentials = grpc.ssl_channel_credentials(
        root_certificates='certs/certificate.pem', private_key_file='certs/key.pem', certificate_chain_file='certs/ca-chain.pem')

    # Create a secure channel
    channel = grpc.secure_channel(
        'grpc.pub1.passkit.io' + ':' + '443', credentials)

    # Create a stub
    couponsStub = a_rpc_pb2_grpc.SingleUseCouponsStub(channel)

    # Create templates stub
    templatesStub = a_rpc_templates_pb2_grpc.TemplatesStub(channel)

    # Create template
    templateRequest = template_pb2.DefaultTemplateRequest()
    templateRequest.Protocol = "SINGLE_USE_COUPON"
    templateRequest.Revision = 1

    template = templatesStub.getDefaultTemplate(templateRequest)

    template.Name = "Quickstart Base Offer"
    template.Description = "Quickstart Base Offer Pass"
    template.Timezone = "Europe/London"

    templateId = templatesStub.createTemplate(template)

    # Create offer
    offer = offer_pb2.CouponOffer()
    offer.Id = "Base Offer"
    offer.OfferTitle = "Base Offer Title"
    offer.OfferShortTitle = "Base Offer"
    offer.OfferDetails = "Base Offer Details"
    offer.OfferFinePrint = "Base Offer fine print"
    offer.BeforeRedeemPassTemplateId(templateId.Id)

    issueStartDate = datetime.datetime.strptime(
        "10/9/2023", "%d/%m/%Y").timestamp()
    issueEndDate = datetime.datetime.strptime(
        "10/11/2023", "%d/%m/%Y").timestamp()
    redemptionStartDate = datetime.datetime.strptime(
        "10/9/2023", "%d/%m/%Y").timestamp()
    redemptionEndDate = datetime.datetime.strptime(
        "10/11/2023", "%d/%m/%Y").timestamp()

    redemptionSettings = offer_pb2.RedemptionSettings()
    redemptionSettings.RedemptionStartDate = timestamp_pb2.Timestamp(
        redemptionStartDate)
    redemptionSettings.RedemptionEndDate = timestamp_pb2.Timestamp(
        redemptionEndDate)

    couponExpirySettings = offer_pb2.CouponExpirySettings
    couponExpirySettings.CouponExpiryType = "AUTO_EXPIRE_REDEMPTION_END_DATE"

    offer.IssueStartDate = timestamp_pb2.Timestamp(issueStartDate)
    offer.IssueEndDate = timestamp_pb2.Timestamp(issueEndDate)
    offer.RedemptionSettings = redemptionSettings
    offer.CouponExpirySettings = couponExpirySettings
    offer.CampaignId = ""  # Get from campaignId from createCampaign call or dashboard
    offer.IanaTimezone = "Europe/London"
    response = couponsStub.createCouponOffer(offer)
    print(response)


create_offer()

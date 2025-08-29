# coupons/createOffer.py
import datetime
import grpc
from google.protobuf import timestamp_pb2
import constants

from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, offer_pb2
from passkit.io.core import a_rpc_templates_pb2_grpc as templates_grpc
from passkit.io.common import template_pb2


def _ts(dt: datetime.datetime) -> timestamp_pb2.Timestamp:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        dt = dt.astimezone(datetime.timezone.utc)
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(dt)
    return ts


def _set_coupon_protocol(req: template_pb2.DefaultTemplateRequest) -> None:
    """Set DefaultTemplateRequest.protocol enum by inspecting the field values."""
    field = req.DESCRIPTOR.fields_by_name.get("protocol")
    if field is None or field.enum_type is None:
        raise ValueError(
            "DefaultTemplateRequest.protocol is missing or not an enum")
    values = list(field.enum_type.values)
    choose = next((v for v in values if "COUPON" in v.name), None) or next(
        (v for v in values if v.number != 0), None
    )
    if choose is None:
        raise ValueError(
            f"Cannot choose protocol enum; available: {[v.name for v in values]}")
    setattr(req, "protocol", choose.number)


def run(
    channel: grpc.Channel,
    campaign_id: str,
    *,
    name: str = "Quickstart Base Offer",
    description: str = "Quickstart Base Offer Pass",
    timezone: str = constants.COUPON_TIMEZONE,
) -> str:
    if not campaign_id:
        raise ValueError("campaign_id is required")

    coupons = coupons_grpc.SingleUseCouponsStub(channel)
    templates = templates_grpc.TemplatesStub(channel)

    # 1) Create default COUPON template
    req = template_pb2.DefaultTemplateRequest()
    _set_coupon_protocol(req)
    req.revision = 1

    try:
        tpl = templates.GetDefaultTemplate(req)
    except AttributeError:
        tpl = templates.getDefaultTemplate(req)

    if hasattr(tpl, "name"):
        tpl.name = name
    if hasattr(tpl, "description"):
        tpl.description = description
    if hasattr(tpl, "timezone"):
        tpl.timezone = timezone

    try:
        created_tpl = templates.CreateTemplate(tpl)
    except AttributeError:
        created_tpl = templates.createTemplate(tpl)

    template_id = getattr(created_tpl, "id", "")
    if not template_id:
        raise RuntimeError("Template creation returned no id")

    # 2) Build offer with configurable windows
    now = datetime.datetime.now(datetime.timezone.utc)

    issue_start = now + \
        datetime.timedelta(minutes=constants.OFFER_ISSUE_START_OFFSET_MIN)
    issue_end = issue_start + \
        datetime.timedelta(days=constants.OFFER_ISSUE_DURATION_DAYS)

    red_start = now + \
        datetime.timedelta(minutes=constants.OFFER_REDEMPTION_START_OFFSET_MIN)
    red_end = red_start + \
        datetime.timedelta(days=constants.OFFER_REDEMPTION_DURATION_DAYS)

    offer = offer_pb2.CouponOffer()
    if hasattr(offer, "id"):
        offer.id = "Base Offer"
    if hasattr(offer, "offerTitle"):
        offer.offerTitle = "Base Offer Title"
    if hasattr(offer, "offerShortTitle"):
        offer.offerShortTitle = "Base Offer"
    if hasattr(offer, "offerDetails"):
        offer.offerDetails = "Base Offer Details"
    if hasattr(offer, "offerFinePrint"):
        offer.offerFinePrint = "Base Offer fine print"
    if hasattr(offer, "beforeRedeemPassTemplateId"):
        offer.beforeRedeemPassTemplateId = template_id

    if hasattr(offer, "issueStartDate"):
        offer.issueStartDate.CopyFrom(_ts(issue_start))
    if hasattr(offer, "issueEndDate"):
        offer.issueEndDate.CopyFrom(_ts(issue_end))

    red = offer_pb2.RedemptionSettings()
    if hasattr(red, "redemptionStartDate"):
        red.redemptionStartDate.CopyFrom(_ts(red_start))
    if hasattr(red, "redemptionEndDate"):
        red.redemptionEndDate.CopyFrom(_ts(red_end))
    offer.redemptionSettings.CopyFrom(red)

    exp = offer_pb2.CouponExpirySettings()
    # Choose an expiry type that mentions 'REDEMPTION_END_DATE' if available
    exp_field = exp.DESCRIPTOR.fields_by_name.get("couponExpiryType")
    if exp_field and exp_field.enum_type:
        vals = list(exp_field.enum_type.values)
        chosen = next((v for v in vals if "REDEMPTION_END_DATE" in v.name), None) or next(
            (v for v in vals if v.number != 0), None
        )
        if chosen:
            setattr(exp, "couponExpiryType", chosen.number)
    offer.couponExpirySettings.CopyFrom(exp)

    if hasattr(offer, "campaignId"):
        offer.campaignId = campaign_id
    if hasattr(offer, "ianaTimezone"):
        offer.ianaTimezone = timezone

    resp = coupons.createCouponOffer(offer)
    offer_id = getattr(resp, "id", "")
    print(f"Created coupon offer: {offer_id} (template {template_id})")
    return offer_id


if __name__ == "__main__":
    from shared.grpcConnectionPooling import ChannelPool
    pool = ChannelPool(size=1)
    try:
        ch = pool.get()
        # Set a real campaign_id to test
        run(ch, campaign_id="")
    finally:
        pool.close()

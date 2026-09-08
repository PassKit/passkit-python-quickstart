"""Reusable coupon examples collected behind one consistent interface."""

from passkit.io.common.common_objects_pb2 import Id
from passkit.io.common.filter_pb2 import Filters
from passkit.io.single_use_coupons.a_rpc_pb2_grpc import SingleUseCouponsStub
from passkit.io.single_use_coupons.campaign_pb2 import CampaignCopyRequest
from passkit.io.single_use_coupons.coupon_pb2 import ExternalIdRequest, ListRequest
from passkit.io.single_use_coupons.offer_pb2 import CouponOffersListRequest

from coupons.createCampaign import run as create_campaign
from coupons.createCoupon import run as create_coupon
from coupons.createOffer import run as create_offer
from coupons.deleteCampaign import run as delete_campaign
from coupons.listCoupons import run as list_coupons
from coupons.redeemCoupon import run as redeem_coupon
from coupons.updateCoupon import run as update_coupon
from coupons.voidCoupon import run as void_coupon


def _stub(channel):
    return channel if isinstance(channel, SingleUseCouponsStub) else SingleUseCouponsStub(channel)


def get_campaign(channel, campaign_id: str):
    return _stub(channel).getCouponCampaign(Id(id=campaign_id))


def update_campaign(channel, campaign):
    return _stub(channel).updateCouponCampaign(campaign)


def list_campaigns(channel):
    return list(_stub(channel).listCouponCampaigns(Filters(limit=-1)))


def copy_campaign(channel, campaign_id: str, name: str):
    return _stub(channel).copyCouponCampaign(CampaignCopyRequest(id=campaign_id, name=name))


def get_offer(channel, offer_id: str):
    return _stub(channel).getCouponOffer(Id(id=offer_id))


def update_offer(channel, offer):
    return _stub(channel).updateCouponOffer(offer)


def list_offers(channel, campaign_id: str):
    request = CouponOffersListRequest(campaignId=campaign_id, filters=Filters(limit=-1))
    return list(_stub(channel).listCouponOffers(request))


def delete_offer(channel, offer_id: str):
    return _stub(channel).deleteCouponOffer(Id(id=offer_id))


def get_coupon_by_id(channel, coupon_id: str):
    return _stub(channel).getCouponById(Id(id=coupon_id))


def get_coupon_by_external_id(channel, campaign_id: str, external_id: str):
    return _stub(channel).getCouponByExternalId(
        ExternalIdRequest(couponCampaignId=campaign_id, externalId=external_id)
    )


def count_coupons(channel, campaign_id: str):
    return _stub(channel).countCouponsByCouponCampaign(ListRequest(couponCampaignId=campaign_id))


__all__ = [
    "copy_campaign",
    "count_coupons",
    "create_campaign",
    "create_coupon",
    "create_offer",
    "delete_campaign",
    "delete_offer",
    "get_campaign",
    "get_coupon_by_external_id",
    "get_coupon_by_id",
    "get_offer",
    "list_campaigns",
    "list_coupons",
    "list_offers",
    "redeem_coupon",
    "update_campaign",
    "update_coupon",
    "update_offer",
    "void_coupon",
]

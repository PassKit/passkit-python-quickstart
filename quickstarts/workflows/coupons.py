"""Single-use coupon lifecycle example."""

from datetime import datetime, timedelta, timezone

from passkit.io.common.common_objects_pb2 import Id
from passkit.io.common.filter_pb2 import Filters
from passkit.io.common.personal_pb2 import Person
from passkit.io.common.project_pb2 import ProjectStatus
from passkit.io.common.protocols_pb2 import PassProtocol
from passkit.io.single_use_coupons.campaign_pb2 import CouponCampaign
from passkit.io.single_use_coupons.coupon_pb2 import Coupon, ListRequest
from passkit.io.single_use_coupons.offer_pb2 import (
    CouponExpirySettings,
    CouponExpiryType,
    CouponOffer,
    RedemptionSettings,
)

from quickstarts.workflow import Workflow, timestamp


class CouponsWorkflow(Workflow):
    protocol = PassProtocol.SINGLE_USE_COUPON

    def execute(self) -> dict[str, str]:
        print("Creating coupon images and templates")
        self.create_images()
        base_template = self.create_template("Python Quickstart Coupon")
        redeemed_template = self.create_template("Python Quickstart Redeemed Coupon", "#777777")

        print("Creating campaign and offers")
        campaign_id = (
            self.service("coupons")
            .createCouponCampaign(
                CouponCampaign(
                    name="Python Quickstart Coupon Campaign",
                    ianaTimezone="Europe/London",
                    status=[
                        ProjectStatus.PROJECT_DRAFT,
                        ProjectStatus.PROJECT_ACTIVE_FOR_OBJECT_CREATION,
                    ],
                )
            )
            .id
        )
        self.remember(
            "coupon campaign",
            lambda: self.service("coupons").deleteCouponCampaign(Id(id=campaign_id)),
        )
        now = datetime.now(timezone.utc)

        def create_offer(title: str, short_title: str) -> str:
            return (
                self.service("coupons")
                .createCouponOffer(
                    CouponOffer(
                        offerTitle=title,
                        offerShortTitle=short_title,
                        offerDetails="Save 10% with this Python quickstart coupon.",
                        offerFinePrint="Quickstart demonstration only.",
                        beforeRedeemPassTemplateId=base_template,
                        afterRedeemPassTemplateId=redeemed_template,
                        campaignId=campaign_id,
                        ianaTimezone="Europe/London",
                        issueStartDate=timestamp(now - timedelta(minutes=1)),
                        issueEndDate=timestamp(now + timedelta(days=30)),
                        couponExpirySettings=CouponExpirySettings(
                            couponExpiryType=CouponExpiryType.AUTO_EXPIRE_REDEMPTION_END_DATE
                        ),
                        redemptionSettings=RedemptionSettings(
                            redemptionStartDate=timestamp(now - timedelta(minutes=1)),
                            redemptionEndDate=timestamp(now + timedelta(days=30)),
                        ),
                    )
                )
                .id
            )

        base_offer = create_offer("Python Quickstart Offer", "Offer")
        vip_offer = create_offer("Python Quickstart VIP Offer", "VIP Offer")

        print("Issuing and updating coupons")
        email = self.config.recipient_email or "python.coupon@dummy.passkit.com"

        def issue(offer_id: str, external_id: str, name: str) -> tuple[str, Coupon]:
            coupon = Coupon(
                externalId=external_id,
                campaignId=campaign_id,
                offerId=offer_id,
                person=Person(displayName=name, emailAddress=email),
            )
            return self.service("coupons").createCoupon(coupon).id, coupon

        base_id, base_coupon = issue(base_offer, "python-coupon-base", "Coupon Holder")
        vip_id, _ = issue(vip_offer, "python-coupon-vip", "VIP Coupon Holder")
        base_coupon.id = base_id
        base_coupon.person.displayName = "Updated Coupon Holder"
        self.service("coupons").updateCoupon(base_coupon)

        print("Reading, listing, counting, redeeming, and voiding coupons")
        self.service("coupons").getCouponById(Id(id=base_id))
        list(
            self.service("coupons").listCouponsByCouponCampaign(
                ListRequest(couponCampaignId=campaign_id, filters=Filters(limit=-1))
            )
        )
        self.service("coupons").countCouponsByCouponCampaign(
            ListRequest(couponCampaignId=campaign_id, filters=Filters(limit=-1))
        )
        self.service("coupons").redeemCoupon(
            Coupon(id=base_id, campaignId=campaign_id, offerId=base_offer)
        )
        self.service("coupons").voidCoupon(
            Coupon(id=vip_id, campaignId=campaign_id, offerId=vip_offer)
        )

        print(f"Created coupons: {base_id}, {vip_id}")
        return {"baseCouponId": base_id, "vipCouponId": vip_id}

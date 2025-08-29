import grpc
from passkit.io.single_use_coupons import a_rpc_pb2_grpc as coupons_grpc, coupon_pb2


def _find_req_message(*name_hints: str):
    for msg in coupon_pb2.DESCRIPTOR.message_types_by_name.values():
        name = msg.name.lower()
        if all(h.lower() in name for h in name_hints):
            return getattr(coupon_pb2, msg.name)
    return None


def _call_method(stub, base_names: list[str], request):
    for base in base_names:
        for method in (base, base[:1].lower() + base[1:]):
            fn = getattr(stub, method, None)
            if fn:
                return fn(request)
    raise RuntimeError(f"No RPC found on stub for {base_names}")


def run(channel: grpc.Channel, campaign_id: str, offer_id: str, coupon_id: str) -> None:
    """
    Void a coupon. Tries several request+RPC combos to survive proto name changes.
    """
    if not coupon_id:
        raise ValueError("coupon_id is required")

    stub = coupons_grpc.SingleUseCouponsStub(channel)

    # Preferred: a dedicated VoidCouponRequest
    Req = _find_req_message("Void", "Coupon")
    if Req:
        req = Req()
        # Populate common fields if present
        if hasattr(req, "couponId"):
            req.couponId = coupon_id
        if hasattr(req, "id") and not hasattr(req, "couponId"):
            req.id = coupon_id
        if hasattr(req, "campaignId") and campaign_id:
            req.campaignId = campaign_id
        if hasattr(req, "offerId") and offer_id:
            req.offerId = offer_id

        _call_method(stub, ["VoidCoupon"], req)
        print("Voided coupon:", coupon_id)
        return

    # Fallback: some APIs accept the Coupon message directly
    if hasattr(stub, "VoidCoupon") or hasattr(stub, "voidCoupon"):
        c = coupon_pb2.Coupon()
        if hasattr(c, "id"):
            c.id = coupon_id
        elif hasattr(c, "couponId"):
            c.couponId = coupon_id
        if campaign_id and hasattr(c, "campaignId"):
            c.campaignId = campaign_id
        if offer_id and hasattr(c, "offerId"):
            c.offerId = offer_id

        _call_method(stub, ["VoidCoupon"], c)
        print("Voided coupon:", coupon_id)
        return

    raise RuntimeError("Could not find a way to call VoidCoupon on this build")

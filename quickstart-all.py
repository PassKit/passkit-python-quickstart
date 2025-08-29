# quickstart_all.py
from membership.deleteProgram import run as run_delete_program
from membership.deleteMember import run as run_delete_member
from membership.checkOutMember import run as run_check_out
from membership.checkInMember import run as run_check_in
from membership.burnPoints import run as run_burn_points
from membership.earnPoints import run as run_earn_points
from membership.updateMember import run as run_update_member
from membership.enrolMember import run as run_enrol_member
from membership.createTier import run as run_create_tier
from membership.createProgram import run as run_create_program

from coupons.createCampaign import run as run_create_campaign
from coupons.createOffer import run as run_create_offer
from coupons.createCoupon import run as run_create_coupon
from coupons.listCoupons import run as run_list_coupons
from coupons.updateCoupon import run as run_update_coupon
from coupons.redeemCoupon import run as run_redeem_coupon
from coupons.voidCoupon import run as run_void_coupon
from coupons.deleteCampaign import run as run_delete_campaign

from flights.createAirport import run as run_create_airport
from flights.deleteAirport import run as run_delete_airport
from flights.createCarrier import run as run_create_carrier
from flights.deleteCarrier import run as run_delete_carrier
from flights.createFlightDesignator import run as run_create_flight_designator
from flights.deleteFlightDesignator import run as run_delete_flight_designator
from flights.createFlight import run as run_create_flight
from flights.deleteFlight import run as run_delete_flight
from flights.createBoardingPass import run as run_create_boarding_pass


from shared.grpcConnectionPooling import ChannelPool
from shared.resendWelcomeEmail import run as run_resend_welcome_email

import sys
from pathlib import Path
import grpc
import constants


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


DEFAULT_MEMBER_EMAIL = "percy@example.com"  # change as needed

if __name__ == "__main__":
    pool = ChannelPool(size=constants.POOL_SIZE)

    program_id = None
    tier_id = None
    member_id = None
    campaign_id = None
    offer_id = None
    coupon_id = None
    flight_template_id = None
    carrier_code = None
    origin_airport = None
    dest_airport = None
    flight_number = None
    service_date = None
    flight_designator_id = None
    boarding_pass_id = None
    origin_port_id = None
    arrival_port_id = None
    origin_existed = False
    arrival_existed = False
    carrier_id = None
    carrier_existed = False
    flight_designator_id = None
    flight_designator_existed = False

    try:
        # Membership Methods
        # 1) Create Program
        program_id = run_create_program(pool.get())

        # 2) Create Tier
        tier_id = run_create_tier(pool.get(), program_id)

        # 3) Enrol Member
        member_id = run_enrol_member(
            pool.get(), program_id, tier_id, constants.DEFAULT_MEMBER_EMAIL)

        # 4) Update Member
        run_update_member(pool.get(), program_id, tier_id, member_id,
                          display_name="Loyal Larry",
                          email="loyal.larry@example.com")

        # 5) Earn & Burn Points
        run_earn_points(pool.get(), member_id, points=100)
        run_burn_points(pool.get(), member_id, points=50)

        # 6) Check In / Out
        run_check_in(pool.get(), member_id,
                     lat=constants.DEFAULT_CHECKIN_LAT,
                     lon=constants.DEFAULT_CHECKIN_LON,
                     address=constants.DEFAULT_CHECKIN_ADDRESS)
        run_check_out(pool.get(), member_id, lat=constants.DEFAULT_CHECKOUT_LAT,
                      lon=constants.DEFAULT_CHECKOUT_LON,
                      address=constants.DEFAULT_CHECKOUT_ADDRESS)

        # 7) Resend welcome email
       # run_resend_welcome_email(pool.get(), "MEMBERSHIP", member_id=member_id)

        # Coupon Methods
        # 1) Create Campaign
        campaign_id = run_create_campaign(pool.get())

        # 2) Create Offer
        offer_id = run_create_offer(pool.get(), campaign_id)

        # 3) Create coupon
        coupon_id = run_create_coupon(
            pool.get(),
            campaign_id,
            offer_id,
            constants.DEFAULT_COUPON_EMAIL,
            display_name=constants.DEFAULT_COUPON_DISPLAY_NAME,  # optional
            forename=constants.DEFAULT_COUPON_FORENAME,          # optional
            surname=constants.DEFAULT_COUPON_SURNAME,            # optional
        )

        # 4) List coupons
        _ = run_list_coupons(pool.get(), campaign_id)

        # 5) Update coupon
        run_update_coupon(
            pool.get(),
            campaign_id,
            coupon_id,
            display_name=constants.DEFAULT_COUPON_DISPLAY_NAME,
            forename=constants.DEFAULT_COUPON_FORENAME,
            surname=constants.DEFAULT_COUPON_SURNAME,
            email=constants.DEFAULT_COUPON_EMAIL,
        )

        # 6) Redeem coupon
        run_redeem_coupon(pool.get(), campaign_id, coupon_id)

        # 7) Resend welcome email
        run_resend_welcome_email(
            pool.get(),
            "SINGLE_USE_COUPON",
            coupon_id=coupon_id,
        )

        # 1) Create origin and arrival airports
        origin_port_id, origin_existed = run_create_airport(
            pool.get(),
            iata=constants.ORIGIN_AIRPORT_IATA,
            icao=constants.ORIGIN_AIRPORT_ICAO,
            name=constants.ORIGIN_AIRPORT_NAME,
            city=constants.ORIGIN_AIRPORT_CITY,
            country_code=constants.ORIGIN_AIRPORT_COUNTRY,
            timezone=constants.ORIGIN_AIRPORT_TZ,
        )

        arrival_port_id, arrival_existed = run_create_airport(
            pool.get(),
            iata=constants.ARRIVAL_AIRPORT_IATA,
            icao=constants.ARRIVAL_AIRPORT_ICAO,
            name=constants.ARRIVAL_AIRPORT_NAME,
            city=constants.ARRIVAL_AIRPORT_CITY,
            country_code=constants.ARRIVAL_AIRPORT_COUNTRY,
            timezone=constants.ARRIVAL_AIRPORT_TZ,
        )

        # 2) Create Carrier
        carrier_id, carrier_existed = run_create_carrier(
            pool.get(),
            iata=constants.CARRIER_IATA,
            icao=constants.CARRIER_ICAO,
            name=constants.CARRIER_NAME,
            pass_type_identifier=constants.CARRIER_PASS_TYPE_ID,
        )

        # 3) Create flight
        flight_id, flight_existed = run_create_flight(
            pool.get(),
            carrier_code=constants.CARRIER_IATA,
            flight_number=constants.FLIGHT_NUMBER,
            origin_iata=constants.ORIGIN_AIRPORT_IATA,
            destination_iata=constants.ARRIVAL_AIRPORT_IATA,
            pass_template_id=constants.FLIGHT_TEMPLATE_ID or None,
            departure_iso=constants.FLIGHT_DEPARTURE_ISO,
        )

        # 4) Create flight designator
        flight_designator_id, flight_designator_existed = run_create_flight_designator(
            pool.get(),
            carrier_code=constants.CARRIER_IATA,
            flight_number=constants.FLIGHT_NUMBER,
            pass_template_id=(
                flight_template_id or constants.FLIGHT_TEMPLATE_ID or ""),
            origin=constants.ORIGIN_AIRPORT_IATA,
            destination=constants.ARRIVAL_AIRPORT_IATA,
            revision=constants.FLIGHT_DESIGNATOR_REVISION,
        )

        # 5) Create boarding pass
        boarding_pass_id, bp_existed = run_create_boarding_pass(
            pool.get(),
            carrier_code=constants.CARRIER_IATA,
            flight_number=constants.FLIGHT_NUMBER,
            origin_iata=constants.ORIGIN_AIRPORT_IATA,
            destination_iata=constants.ARRIVAL_AIRPORT_IATA,
            departure_iso=constants.FLIGHT_DEPARTURE_ISO,
            pnr=getattr(constants, "BP_PNR", ""),
            sequence_number=constants.BP_SEQUENCE_NUMBER,
            pax_forename=constants.BP_PAX_FORENAME,
            pax_surname=constants.BP_PAX_SURNAME,
            pax_email=constants.BP_EMAIL,
        )

    finally:
       # Cleanup — delete member then program if they exist
        if member_id:
            try:
                run_delete_member(pool.get(), member_id)
            except grpc.RpcError as e:
                print("Failed to delete member during cleanup:", e.details())
        if program_id:
            try:
                run_delete_program(pool.get(), program_id)
            except grpc.RpcError as e:
                print("Failed to delete program during cleanup:", e.details())
        if coupon_id:
            try:
                run_void_coupon(pool.get(), campaign_id, offer_id, coupon_id)
            except grpc.RpcError as e:
                print("Failed to delete coupon during cleanup:", e.details())
        if campaign_id:
            try:
                run_delete_campaign(pool.get(), campaign_id)
            except grpc.RpcError as e:
                print("Failed to delete campaign during cleanup:", e.details())
        if origin_port_id and not origin_existed:
            try:
                run_delete_airport(pool.get(), port_id=origin_port_id)
            except grpc.RpcError as e:
                print("Cleanup: failed to delete origin airport:", e.details())

        if arrival_port_id and not arrival_existed:
            try:
                run_delete_airport(pool.get(), port_id=arrival_port_id)
            except grpc.RpcError as e:
                print("Cleanup: failed to delete arrival airport:", e.details())

        if carrier_id and not carrier_existed:
            try:
                run_delete_carrier(pool.get(), carrier_id=carrier_id)
            except grpc.RpcError as e:
                print("Cleanup: failed to delete carrier:", e.details())

        if (not flight_designator_existed) and constants.CARRIER_IATA and constants.FLIGHT_NUMBER:
            try:
                run_delete_flight_designator(
                    pool.get(),
                    carrier_code=constants.CARRIER_IATA,
                    flight_number=constants.FLIGHT_NUMBER,
                    revision=constants.FLIGHT_DESIGNATOR_REVISION,  # match the create step
                )
            except grpc.RpcError as e:
                print("Cleanup: failed to delete flight designator:", e.details())

        if not flight_existed and flight_id:
            try:
                run_delete_flight(
                    pool.get(),
                    carrier_code=constants.CARRIER_IATA,
                    flight_number=constants.FLIGHT_NUMBER,
                    origin_iata=constants.ORIGIN_AIRPORT_IATA,
                    destination_iata=constants.ARRIVAL_AIRPORT_IATA,
                    departure_iso=constants.FLIGHT_DEPARTURE_ISO,
                )
            except grpc.RpcError as e:
                print("Cleanup: failed to delete flight :", e.details())

        pool.close()

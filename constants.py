"""
Shared constants for quickstart scripts.
Edit these values to configure your environment and defaults.
"""

from pathlib import Path

# ----------------------------------------------------------------------
# gRPC settings
# ----------------------------------------------------------------------
GRPC_HOST = "grpc.pub1.passkit.io:443"  # default production endpoint
POOL_SIZE = 5                           # how many channels in the pool

# ----------------------------------------------------------------------
# Certificates (mTLS)
# ----------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
CERTS_DIR = ROOT / "certs"

CA_FILE = CERTS_DIR / "ca-chain.pem"
CERT_FILE = CERTS_DIR / "certificate.pem"
KEY_FILE = CERTS_DIR / "key.pem"

# ----------------------------------------------------------------------
# Default test data for membership methods
# ----------------------------------------------------------------------
DEFAULT_MEMBER_EMAIL = "percy@passkit.com"
DEFAULT_MEMBER_DISPLAY_NAME = "Percy PassKit"
DEFAULT_MEMBER_FORENAME = "Percy"
DEFAULT_MEMBER_SURNAME = "PassKit"

UPDATE_MEMBER_DISPLAY_NAME = "Loyal Larry"
UPDATE_MEMBER_EMAIL = "loyal.larry@passki.com"

DEFAULT_CHECKIN_LAT = 51.5074
DEFAULT_CHECKIN_LON = -0.1278
DEFAULT_CHECKIN_ADDRESS = "London, UK"

DEFAULT_CHECKOUT_LAT = 51.5074
DEFAULT_CHECKOUT_LON = -0.1278
DEFAULT_CHECKOUT_ADDRESS = "London, UK"

# Points config
DEFAULT_EARN_POINTS = 100
DEFAULT_BURN_POINTS = 50

# ----------------------------------------------------------------------
# Default test data for coupon methods
# ----------------------------------------------------------------------

DEFAULT_COUPON_EMAIL = "cassandra.coupon@passkit.com"
DEFAULT_COUPON_NAME = "Quickstart Coupon"
DEFAULT_COUPON_DESCRIPTION = "10% off – Quickstart"
DEFAULT_COUPON_DISPLAY_NAME = "Cassandra Coupon"
DEFAULT_COUPON_FORENAME = "Cassandra"
DEFAULT_COUPON_SURNAME = "Coupon"

# minutes from "now" to start issuing
OFFER_ISSUE_START_OFFSET_MIN = -1
OFFER_ISSUE_DURATION_DAYS = 30           # issue window length

# minutes from "now" to start redemption
OFFER_REDEMPTION_START_OFFSET_MIN = -1
OFFER_REDEMPTION_DURATION_DAYS = 30      # redemption window length

# used for template/offer where applicable
COUPON_TIMEZONE = "Europe/London"

# ----------------------------------------------------------------------
# Flights defaults
# ----------------------------------------------------------------------
ORIGIN_AIRPORT_IATA = "LHR"
ORIGIN_AIRPORT_ICAO = "EGLL"
ORIGIN_AIRPORT_NAME = "London Heathrow"
ORIGIN_AIRPORT_CITY = "London"
ORIGIN_AIRPORT_COUNTRY = "GB"
ORIGIN_AIRPORT_TZ = "Europe/London"

ARRIVAL_AIRPORT_IATA = "DUB"
ARRIVAL_AIRPORT_ICAO = "EIDW"
ARRIVAL_AIRPORT_NAME = "Dublin Airport"
ARRIVAL_AIRPORT_CITY = "Dublin"
ARRIVAL_AIRPORT_COUNTRY = "IE"
ARRIVAL_AIRPORT_TZ = "Europe/Dublin"


CARRIER_IATA = "YY"
CARRIER_ICAO = "YYY"
CARRIER_NAME = "PassKit Air"
# your Apple passTypeIdentifier if applicable
CARRIER_PASS_TYPE_ID = "pass.com.passkit.claudia"

FLIGHT_NUMBER = "1234"
FLIGHT_TEMPLATE_ID = ""

FLIGHT_TIMES_MODE = "OFFSETS"  # or "CLOCK"

# OFFSETS mode: calculate boarding/arrival/gate-close from one departure datetime
# Example (BST): "2025-09-15T14:00:00+01:00"
FLIGHT_DEPARTURE_ISO = "2025-09-15T14:00:00+01:00"
BOARDING_MIN_BEFORE_DEP = 60     # boarding starts 60 min before departure
ARRIVAL_MIN_AFTER_DEP = 60       # arrival scheduled 60 min after departure
GATE_CLOSE_MIN_BEFORE_DEP = 30   # gate closes 30 min before departure

# CLOCK mode: set explicit clock times (24h "HH:MM")
FLIGHT_BOARDING_CLOCK = "13:00"
FLIGHT_DEPARTURE_CLOCK = "14:00"
FLIGHT_ARRIVAL_CLOCK = "15:00"
FLIGHT_GATECLOSE_CLOCK = "13:30"

FLIGHT_DESIGNATOR_REVISION = 3  # must be > 0

BP_SEAT_NUMBER = ""      # e.g. "12A"
BP_BOARDING_ZONE = ""    # e.g. "B"
BP_CABIN_CLASS = ""      # e.g. "ECONOMY"
BP_EMAIL = ""
BP_PAX_FORENAME = "Larry"
BP_PAX_SURNAME = "Loyalty"
BP_SEQUENCE_NUMBER = 1

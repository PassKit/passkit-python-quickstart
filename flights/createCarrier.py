# flights/createCarrier.py
import grpc
from typing import Optional, Tuple
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc, carrier_pb2


def run(
    channel: grpc.Channel,
    *,
    iata: str,
    icao: str,
    name: str,
    pass_type_identifier: str = "",
) -> Tuple[Optional[str], bool]:
    """
    Create an airline carrier. Returns (carrier_id, existed).
      - carrier_id: ID of created carrier (None if it already existed and we skipped create)
      - existed: True if a record with this IATA/ICAO already existed
    """
    if not iata and not icao:
        raise ValueError("At least one of iata or icao must be provided")

    stub = flights_grpc.FlightsStub(channel)

    carrier = carrier_pb2.Carrier()
    if hasattr(carrier, "airlineName"):
        carrier.airlineName = name
    if hasattr(carrier, "iataCarrierCode"):
        carrier.iataCarrierCode = iata or ""
    if hasattr(carrier, "icaoCarrierCode"):
        carrier.icaoCarrierCode = icao or ""
    if hasattr(carrier, "passTypeIdentifier"):
        carrier.passTypeIdentifier = pass_type_identifier

    try:
        try:
            resp = stub.createCarrier(carrier)
        except AttributeError:
            resp = stub.CreateCarrier(carrier)
        carrier_id = getattr(resp, "id", "") or getattr(resp, "carrierId", "")
        print(f"Created carrier: {carrier_id} ({iata or icao} - {name})")
        return carrier_id or None, False
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            print(f"Carrier already exists, skipping create: {iata or icao}")
            return None, True
        raise

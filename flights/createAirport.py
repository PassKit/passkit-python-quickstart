# flights/createAirport.py
import grpc
from typing import Optional, Tuple
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc, airport_pb2


def run(
    channel: grpc.Channel,
    *,
    iata: str,
    icao: str,
    name: str,
    city: str,
    country_code: str,
    timezone: str,
) -> Tuple[Optional[str], bool]:
    """
    Create an airport/port. Returns (port_id, existed).
      - port_id: ID of created port (None if we didn't create one)
      - existed: True if the airport already existed and we skipped creation
    """
    if not iata and not icao:
        raise ValueError("At least one of iata or icao must be provided")

    stub = flights_grpc.FlightsStub(channel)

    port = airport_pb2.Port()
    if hasattr(port, "airportName"):
        port.airportName = name
    if hasattr(port, "cityName"):
        port.cityName = city
    if hasattr(port, "iataAirportCode"):
        port.iataAirportCode = iata or ""
    if hasattr(port, "icaoAirportCode"):
        port.icaoAirportCode = icao or ""
    if hasattr(port, "countryCode"):
        port.countryCode = country_code
    if hasattr(port, "timezone"):
        port.timezone = timezone

    try:
        resp = stub.createPort(port)
        port_id = getattr(resp, "id", "") or getattr(resp, "portId", "")
        print(f"Created airport/port: {port_id} ({iata or icao} - {name})")
        return port_id or None, False
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.ALREADY_EXISTS:
            print(f"Airport already exists, skipping create: {iata or icao}")
            return None, True
        raise

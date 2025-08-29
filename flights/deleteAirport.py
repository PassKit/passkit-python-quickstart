# flights/deleteAirport.py
import grpc
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc, airport_pb2


def run(
    channel: grpc.Channel,
    *,
    port_id: str | None = None,
    iata: str | None = None,
    icao: str | None = None,
    airport_code: str | None = None,  # some builds use a generic code
) -> None:
    """
    Delete an airport (Port). Provide ONE of: port_id, iata, icao, airport_code.
    """
    if not any([port_id, iata, icao, airport_code]):
        raise ValueError("Provide one of: port_id, iata, icao, airport_code")

    stub = flights_grpc.FlightsStub(channel)

    port = airport_pb2.Port()
    # Populate the identifier your build supports
    if port_id and hasattr(port, "id"):
        port.id = port_id
    elif iata and hasattr(port, "iataAirportCode"):
        port.iataAirportCode = iata
    elif icao and hasattr(port, "icaoAirportCode"):
        port.icaoAirportCode = icao
    elif airport_code and hasattr(port, "airportCode"):
        port.airportCode = airport_code
    else:
        # Last resort: try a generic 'code' if it exists
        if hasattr(port, "code") and (iata or icao or airport_code):
            port.code = iata or icao or airport_code
        else:
            raise RuntimeError(
                "Could not map provided identifier to Port fields for this build")

    stub.deletePort(port)

    ident = port_id or iata or icao or airport_code
    print(f"Deleted airport/port: {ident}")

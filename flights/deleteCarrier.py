# flights/deleteCarrier.py
import grpc
from passkit.io.flights import a_rpc_pb2_grpc as flights_grpc, carrier_pb2


def run(
    channel: grpc.Channel,
    *,
    carrier_id: str | None = None,
    iata: str | None = None,
    icao: str | None = None,
    carrier_code: str | None = None,  # some builds expose a generic 'carrierCode'
) -> None:
    """
    Delete a carrier. Provide ONE of: carrier_id, iata, icao, carrier_code.
    """
    if not any([carrier_id, iata, icao, carrier_code]):
        raise ValueError(
            "Provide one of: carrier_id, iata, icao, carrier_code")

    stub = flights_grpc.FlightsStub(channel)

    carrier = carrier_pb2.Carrier()
    # Map the identifier to whatever your build supports
    if carrier_id and hasattr(carrier, "id"):
        carrier.id = carrier_id
    elif iata and hasattr(carrier, "iataCarrierCode"):
        carrier.iataCarrierCode = iata
    elif icao and hasattr(carrier, "icaoCarrierCode"):
        carrier.icaoCarrierCode = icao
    elif carrier_code and hasattr(carrier, "carrierCode"):
        carrier.carrierCode = carrier_code
    else:
        # Last-resort: try a generic field if present
        if hasattr(carrier, "code") and (carrier_code or iata or icao):
            carrier.code = carrier_code or iata or icao
        else:
            raise RuntimeError(
                "Could not map provided identifier to Carrier fields for this build")

    stub.deleteCarrier(carrier)

    ident = carrier_id or iata or icao or carrier_code
    print(f"Deleted carrier: {ident}")

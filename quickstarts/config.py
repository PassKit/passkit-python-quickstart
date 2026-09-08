"""Environment-based quickstart configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


def _path(value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


@dataclass(frozen=True)
class Config:
    address: str
    root_certificate: Path
    private_key: Path
    certificate: Path
    passphrase: str | None
    connection_mode: str
    pool_size: int
    keep_assets: bool
    recipient_email: str | None
    apple_certificate: str | None
    carrier_code: str
    origin: str
    destination: str

    @classmethod
    def load(cls) -> Config:
        load_dotenv(ROOT / ".env", override=False)
        host = os.getenv("PASSKIT_ADDRESS", "grpc.pub1.passkit.io")
        port = os.getenv("PASSKIT_PORT", "443")
        return cls(
            address=f"{host}:{port}",
            root_certificate=_path(os.getenv("PASSKIT_ROOT_CERT", "certs/ca-chain.pem")),
            private_key=_path(os.getenv("PASSKIT_PRIVATE_KEY", "certs/key.pem")),
            certificate=_path(os.getenv("PASSKIT_CERTIFICATE", "certs/certificate.pem")),
            passphrase=os.getenv("PASSKIT_PASSPHRASE") or None,
            connection_mode=os.getenv("PASSKIT_CONNECTION_MODE", "pool").lower(),
            pool_size=int(os.getenv("PASSKIT_POOL_SIZE", "5")),
            keep_assets=os.getenv("PASSKIT_KEEP_ASSETS", "false").lower() == "true",
            recipient_email=os.getenv("PASSKIT_RECIPIENT_EMAIL") or None,
            apple_certificate=os.getenv("PASSKIT_APPLE_CERTIFICATE") or None,
            carrier_code=os.getenv("PASSKIT_FLIGHT_CARRIER", "YY").upper(),
            origin=os.getenv("PASSKIT_FLIGHT_ORIGIN", "YY4").upper(),
            destination=os.getenv("PASSKIT_FLIGHT_DESTINATION", "ADP").upper(),
        )

    def validate(self, *, require_flights: bool = False, check_files: bool = True) -> None:
        errors: list[str] = []
        if self.connection_mode not in {"single", "pool"}:
            errors.append('PASSKIT_CONNECTION_MODE must be "single" or "pool"')
        if self.pool_size < 1:
            errors.append("PASSKIT_POOL_SIZE must be a positive integer")
        if require_flights and not self.apple_certificate:
            errors.append("PASSKIT_APPLE_CERTIFICATE is required for flights")
        if len(self.carrier_code) != 2:
            errors.append("PASSKIT_FLIGHT_CARRIER must be a two-character IATA code")
        if check_files:
            for path in (self.root_certificate, self.private_key, self.certificate):
                if not path.is_file():
                    errors.append(f"Credential file not found: {path}")
        if errors:
            raise ValueError("Invalid PassKit configuration:\n- " + "\n- ".join(errors))

import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from quickstarts.config import Config


class ConfigTests(unittest.TestCase):
    def test_defaults_are_developer_friendly(self):
        with patch.dict(os.environ, {}, clear=True):
            config = Config.load()
        self.assertEqual(config.address, "grpc.pub1.passkit.io:443")
        self.assertEqual(config.connection_mode, "pool")
        self.assertEqual(config.pool_size, 5)
        self.assertFalse(config.keep_assets)

    def test_validation_reports_all_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.pem"
            config = Config(
                address="grpc.pub1.passkit.io:443",
                root_certificate=missing,
                private_key=missing,
                certificate=missing,
                passphrase=None,
                connection_mode="pool",
                pool_size=5,
                keep_assets=False,
                recipient_email=None,
                apple_certificate=None,
                carrier_code="YY",
                origin="YY4",
                destination="ADP",
            )
            with self.assertRaisesRegex(ValueError, "Credential file not found"):
                config.validate()

    def test_flights_require_apple_certificate(self):
        config = replace(Config.load(), apple_certificate=None)
        with self.assertRaisesRegex(ValueError, "PASSKIT_APPLE_CERTIFICATE"):
            config.validate(require_flights=True, check_files=False)

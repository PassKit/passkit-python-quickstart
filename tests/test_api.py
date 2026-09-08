import unittest

from quickstarts.api import DESTRUCTIVE_METHODS, PassKitApi, Service


class FakePool:
    def service(self, _name):
        return type("Stub", (), {"safe": lambda self, request: request})()


class ApiTests(unittest.TestCase):
    def test_operations_exposes_every_service(self):
        operations = PassKitApi.operations()
        self.assertGreaterEqual(len(operations), 14)
        self.assertIn("createProgram", operations["members"])
        self.assertIn("issueTicket", operations["event_tickets"])
        self.assertIn("createBoardingPass", operations["flights"])
        self.assertGreater(sum(map(len, operations.values())), 200)

    def test_sensitive_methods_are_blocked_by_default(self):
        service = Service(FakePool(), "members", False)
        method = next(iter(DESTRUCTIVE_METHODS))
        with self.assertRaises(PermissionError):
            getattr(service, method)(object())

    def test_safe_method_is_forwarded(self):
        marker = object()
        self.assertIs(Service(FakePool(), "members", False).safe(marker), marker)

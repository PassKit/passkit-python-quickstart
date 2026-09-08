"""Complete, low-level access to the generated PassKit SDK service methods."""

from __future__ import annotations

from quickstarts.client import STUB_CLASSES

DESTRUCTIVE_METHODS = {
    "addAppleCertificate",
    "bulkDeleteMembers",
    "bulkDeleteTickets",
    "bulkVoidCoupons",
    "changeOwnPassword",
    "changePassword",
    "deleteAccount",
    "deleteMembersBySegment",
    "refreshApiSecret",
    "resetPassword",
    "revokeLegacyCredentials",
    "sendNFCSigningCredentials",
    "updateMembersBySegment",
}


class Service:
    def __init__(self, pool, name: str, allow_destructive: bool):
        self._pool = pool
        self._name = name
        self._allow_destructive = allow_destructive

    def __getattr__(self, method: str):
        if method in DESTRUCTIVE_METHODS and not self._allow_destructive:

            def blocked(*_args, **_kwargs):
                raise PermissionError(
                    f"{method} is a sensitive operation; construct PassKitApi with "
                    "allow_destructive=True to enable it"
                )

            return blocked
        candidate = getattr(self._pool.service(self._name), method, None)
        if candidate is None:
            raise AttributeError(f"Unknown {self._name} SDK method: {method}")
        return candidate

    def collect(self, method: str, request, **kwargs) -> list:
        return list(getattr(self, method)(request, **kwargs))


class PassKitApi:
    def __init__(self, pool, *, allow_destructive: bool = False):
        self._pool = pool
        self._allow_destructive = allow_destructive

    def __getattr__(self, service: str) -> Service:
        if service not in STUB_CLASSES:
            raise AttributeError(f"Unknown PassKit service: {service}")
        return Service(self._pool, service, self._allow_destructive)

    @staticmethod
    def operations() -> dict[str, list[str]]:
        operations: dict[str, list[str]] = {}
        for service, stub_class in STUB_CLASSES.items():
            method_names = []
            # Generated stubs attach RPC callables in __init__, so use the paired
            # service descriptor embedded in the module's imported pb2 module.
            pb2 = __import__(stub_class.__module__.removesuffix("_grpc"), fromlist=["DESCRIPTOR"])
            for definition in pb2.DESCRIPTOR.services_by_name.values():
                if definition.name == stub_class.__name__.removesuffix("Stub"):
                    method_names = [method.name for method in definition.methods]
                    break
            operations[service] = method_names
        return operations

"""Shared helpers used by all four quickstart workflows."""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
from passkit.io.common.common_objects_pb2 import Id
from passkit.io.common.protocols_pb2 import PassProtocol
from passkit.io.common.template_pb2 import DefaultTemplateRequest
from passkit.io.image.image_pb2 import CreateImageInput, ImageData, ImageIds

ROOT = Path(__file__).resolve().parents[1]


def timestamp(value: datetime) -> Timestamp:
    result = Timestamp()
    result.FromDatetime(value.astimezone(timezone.utc))
    return result


def image_string(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


class Workflow:
    protocol: int = PassProtocol.PASS_PROTOCOL_DO_NOT_USE

    def __init__(self, pool, config):
        self.pool = pool
        self.config = config
        self.cleanup_actions: list[tuple[str, Callable[[], object]]] = []
        self.image_ids = ImageIds()

    def service(self, name: str):
        return self.pool.service(name)

    def remember(self, label: str, callback) -> None:
        self.cleanup_actions.append((label, callback))

    def create_images(self) -> ImageIds:
        icon = image_string(ROOT / "assets/shared/icon.png")
        logo = image_string(ROOT / "assets/shared/logo.png")
        hero = image_string(ROOT / "assets/pass/hero.png")
        strip = image_string(ROOT / "assets/pass/strip.png")
        data = ImageData(
            icon=icon,
            logo=logo,
            appleLogo=logo,
            hero=hero,
            eventStrip=strip,
            strip=strip,
        )
        self.image_ids = self.service("images").createImages(
            CreateImageInput(name="Python quickstart images", imageData=data)
        )
        for field in self.image_ids.DESCRIPTOR.fields:
            image_id = getattr(self.image_ids, field.name)
            if image_id:
                self.remember(
                    f"{field.name} image",
                    lambda value=image_id: self.service("images").deleteImage(Id(id=value)),
                )
        return self.image_ids

    def create_template(self, name: str, color: str = "#1F4E79") -> str:
        template = self.service("templates").getDefaultTemplate(
            DefaultTemplateRequest(protocol=self.protocol, revision=1)
        )
        template.name = name
        template.description = f"{name} pass"
        template.timezone = "Europe/London"
        template.imageIds.CopyFrom(self.image_ids)
        template.ClearField("images")
        template.colors.backgroundColor = color
        result = self.service("templates").createTemplate(template)
        self.remember(
            f"{name} template",
            lambda: self.service("templates").deleteTemplate(Id(id=result.id)),
        )
        return result.id

    def cleanup(self) -> None:
        if self.config.keep_assets:
            print("PASSKIT_KEEP_ASSETS=true; generated resources were not deleted.")
            return
        print("Cleaning up generated resources...")
        for label, callback in reversed(self.cleanup_actions):
            try:
                callback()
                print(f"Deleted {label}.")
            except grpc.RpcError as error:
                if error.code() == grpc.StatusCode.NOT_FOUND:
                    continue
                print(f"Could not delete {label}: {error.details()}")

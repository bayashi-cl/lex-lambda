from pydantic import BaseModel
from typing import Any


class Slot(BaseModel):
    name: str


class Intent(BaseModel):
    name: str
    slots: list[Slot]


class Bot(BaseModel):
    name: str
    intents: list[Intent]

    def to_cfn(self) -> dict[str, Any]:
        raise NotImplementedError

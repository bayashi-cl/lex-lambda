import json
from pathlib import Path
from typing import Any

import pytest
from lambda_app.handler import handler


@pytest.mark.parametrize(
    "event",
    json.loads(Path(__file__).with_name("events.json").read_text()),
)
def test_event(event: dict[str, Any]) -> None:
    resp = handler(event, ...)
    assert resp["sessionState"]["dialogAction"]["type"] == "Delegate"

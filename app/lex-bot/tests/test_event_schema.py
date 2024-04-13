import json
from pathlib import Path
from typing import Any

import lex_bot
import pytest


@pytest.mark.parametrize(
    "event",
    json.loads(Path(__file__).with_name("events.json").read_text()),
)
def test_event(event: dict[str, Any]) -> None:
    lex_bot.LexEvent.model_validate(event)

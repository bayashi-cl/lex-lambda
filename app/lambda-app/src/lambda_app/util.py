from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence

from aws_lambda_powertools.middleware_factory import lambda_handler_decorator
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel

JsonType = Mapping[str, "JsonType"] | Sequence["JsonType"] | str | int | float | bool | None


@lambda_handler_decorator
def dump_response(handler: Callable[..., BaseModel], event: JsonType, context: LambdaContext) -> JsonType:
    return handler(event, context).model_dump(by_alias=True)

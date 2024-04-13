import logging
from typing import Any

from aws_lambda_powertools.utilities import parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from lex_bot import DialogAction, LexEvent, LexResponse, SessionState


def delegate(
    session_state: SessionState, request_attributes: dict[str, str]
) -> LexResponse:
    session_state.dialog_action = DialogAction.default()
    return LexResponse(
        session_state=session_state, request_attributes=request_attributes
    )


def pass_through(event: LexEvent) -> LexResponse:
    return delegate(event.session_state, request_attributes=event.request_attributes)


@parser.event_parser
def handler(event: LexEvent, context: LambdaContext) -> dict[str, Any]:  # noqa: ARG001
    logging.info(event.model_dump_json(by_alias=True))
    return pass_through(event).model_dump(by_alias=True)

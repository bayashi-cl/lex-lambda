import logging

from aws_lambda_powertools.utilities import parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from lex_bot import LexEvent, LexResponse, LexSession

from .bot import bot
from .util import dump_response


@dump_response
@parser.event_parser
def handler(
    event: LexEvent,
    context: LambdaContext,  # noqa: ARG001
) -> LexResponse:
    logging.info(event.model_dump_json(by_alias=True))
    session = LexSession(event, bot)

    return session.delegate()

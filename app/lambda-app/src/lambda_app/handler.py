import logging

from aws_lambda_powertools.utilities import parser
from aws_lambda_powertools.utilities.typing import LambdaContext
from lex_bot import Bot, LexEvent, LexResponse, LexSession

from .util import dump_response

bot = Bot(name="TestBot", intents=[])


@dump_response
@parser.event_parser
def handler(
    event: LexEvent,
    context: LambdaContext,  # noqa: ARG001
) -> LexResponse:
    logging.info(event.model_dump_json(by_alias=True))
    session = LexSession(event, bot)

    return session.delegate()

from typing import Any

import common_utils
from aws_lambda_powertools.utilities.typing import LambdaContext


def handler(event: dict[str, Any], context: LambdaContext) -> dict[str, str]:
    return {"statusCode": "200"}

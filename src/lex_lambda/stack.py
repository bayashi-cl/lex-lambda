from aws_cdk import (
    Arn,
    ArnComponents,
    BundlingOptions,
    DockerImage,
    RemovalPolicy,
    Stack,
    aws_iam,
    aws_lambda,
    aws_lex,
    aws_logs,
)
from constructs import Construct
from lambda_app.bot import bot as bot_def

from .bot_def import bot_as_cfn

LOCALE_JP = "ja_JP"
BUNDLE_COMMAND_TEMPLATE = r"""\
pip wheel --wheel-dir /tmp/wheelhouse --no-deps --requirement <(grep -E '^\-e' requirements.lock | sed 's/-e //g')
pip install --find-links /tmp/wheelhouse --no-index --no-warn-conflicts --target /asset-output {}
"""


class LexLambdaStack(Stack):
    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)
        runtime = aws_lambda.Runtime.PYTHON_3_12

        app = aws_lambda.Function(
            self,
            "LexFunction",
            code=aws_lambda.Code.from_asset(
                ".",
                bundling=BundlingOptions(
                    image=DockerImage.from_build(
                        ".",
                        build_args={"IMAGE": runtime.bundling_image.image},
                        file="docker/lambda.Dockerfile",
                    ),
                    command=["bash", "-eux", "-c", BUNDLE_COMMAND_TEMPLATE.format("lambda_app")],
                    user="root",
                ),
            ),
            handler="lambda_app.handler",
            runtime=runtime,
            logging_format=aws_lambda.LoggingFormat.JSON,
            application_log_level="INFO",
        )
        aws_logs.LogGroup(
            self,
            "App2LogGroup",
            log_group_name=f"/aws/lambda/{app.function_name}",
            removal_policy=RemovalPolicy.DESTROY,
        )

        bot_role = aws_iam.Role(self, "BotRole", assumed_by=aws_iam.ServicePrincipal("lexv2.amazonaws.com"))

        bot = aws_lex.CfnBot(
            self,
            "Bot",
            data_privacy={"ChildDirected": False},
            idle_session_ttl_in_seconds=60,
            name="TestBot",
            role_arn=bot_role.role_arn,
            auto_build_bot_locales=True,
            bot_locales=[bot_as_cfn(bot_def)],
            test_bot_alias_settings=aws_lex.CfnBot.TestBotAliasSettingsProperty(
                bot_alias_locale_settings=[
                    aws_lex.CfnBot.BotAliasLocaleSettingsItemProperty(
                        bot_alias_locale_setting=aws_lex.CfnBot.BotAliasLocaleSettingsProperty(
                            enabled=True,
                            code_hook_specification=aws_lex.CfnBot.CodeHookSpecificationProperty(
                                lambda_code_hook=aws_lex.CfnBot.LambdaCodeHookProperty(
                                    code_hook_interface_version="1.0",
                                    lambda_arn=app.function_arn,
                                ),
                            ),
                        ),
                        locale_id=LOCALE_JP,
                    ),
                ],
            ),
        )
        app.add_permission(
            "BotPermission",
            action="lambda:InvokeFunction",
            principal=aws_iam.ServicePrincipal("lex.amazonaws.com"),
            source_arn=Arn.format(
                ArnComponents(
                    service="lex",
                    resource="bot-alias",
                    resource_name=f"{bot.attr_id}/*",
                ),
                stack=self,
            ),
        )

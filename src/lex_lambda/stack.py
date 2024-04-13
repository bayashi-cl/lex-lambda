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
            bot_locales=[
                aws_lex.CfnBot.BotLocaleProperty(
                    locale_id=LOCALE_JP,
                    nlu_confidence_threshold=0.5,
                    intents=[
                        aws_lex.CfnBot.IntentProperty(
                            name="FallbackIntent",
                            parent_intent_signature="AMAZON.FallbackIntent",
                            dialog_code_hook=aws_lex.CfnBot.DialogCodeHookSettingProperty(enabled=True),
                        ),
                        aws_lex.CfnBot.IntentProperty(
                            name="TestIntent",
                            sample_utterances=[aws_lex.CfnBot.SampleUtteranceProperty(utterance="test intent")],
                            slots=[
                                aws_lex.CfnBot.SlotProperty(
                                    name="slot1",
                                    slot_type_name="AMAZON.FreeFormInput",
                                    value_elicitation_setting=aws_lex.CfnBot.SlotValueElicitationSettingProperty(
                                        slot_constraint="Required",
                                        slot_capture_setting=aws_lex.CfnBot.SlotCaptureSettingProperty(
                                            elicitation_code_hook=aws_lex.CfnBot.ElicitationCodeHookInvocationSettingProperty(
                                                enable_code_hook_invocation=True,
                                                invocation_label="TestIntent-slot1",
                                            )
                                        ),
                                        prompt_specification=aws_lex.CfnBot.PromptSpecificationProperty(
                                            max_retries=1,
                                            message_groups_list=[
                                                aws_lex.CfnBot.MessageGroupProperty(
                                                    message=aws_lex.CfnBot.MessageProperty(
                                                        plain_text_message=aws_lex.CfnBot.PlainTextMessageProperty(
                                                            value="slot1-message",
                                                        ),
                                                    ),
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                                aws_lex.CfnBot.SlotProperty(
                                    name="slot2",
                                    slot_type_name="AMAZON.FreeFormInput",
                                    value_elicitation_setting=aws_lex.CfnBot.SlotValueElicitationSettingProperty(
                                        slot_constraint="Required",
                                        slot_capture_setting=aws_lex.CfnBot.SlotCaptureSettingProperty(
                                            elicitation_code_hook=aws_lex.CfnBot.ElicitationCodeHookInvocationSettingProperty(
                                                enable_code_hook_invocation=True,
                                                invocation_label="TestIntent-slot2",
                                            )
                                        ),
                                        prompt_specification=aws_lex.CfnBot.PromptSpecificationProperty(
                                            max_retries=1,
                                            message_groups_list=[
                                                aws_lex.CfnBot.MessageGroupProperty(
                                                    message=aws_lex.CfnBot.MessageProperty(
                                                        plain_text_message=aws_lex.CfnBot.PlainTextMessageProperty(
                                                            value="slot2-message",
                                                        ),
                                                    ),
                                                ),
                                            ],
                                        ),
                                    ),
                                ),
                            ],
                            slot_priorities=[
                                aws_lex.CfnBot.SlotPriorityProperty(priority=1, slot_name="slot1"),
                                aws_lex.CfnBot.SlotPriorityProperty(priority=2, slot_name="slot2"),
                            ],
                            dialog_code_hook=aws_lex.CfnBot.DialogCodeHookSettingProperty(enabled=True),
                        ),
                    ],
                ),
            ],
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

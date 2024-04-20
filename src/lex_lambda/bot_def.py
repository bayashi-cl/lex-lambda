"""Lex Bot SDK to AWS CDK

Lambdaにaws-cdk-libを乗せるわけには行かないので
"""

from aws_cdk import aws_lex
from lex_bot.bot import Bot, BuiltInIntent, Intent, Slot


def slot_as_cfn(slot: Slot) -> aws_lex.CfnBot.SlotProperty:
    return aws_lex.CfnBot.SlotProperty(
        name=slot.name,
        slot_type_name=slot.slot_type_name,
        value_elicitation_setting=aws_lex.CfnBot.SlotValueElicitationSettingProperty(
            slot_constraint="Required" if slot.required else "Optional",
            slot_capture_setting=aws_lex.CfnBot.SlotCaptureSettingProperty(
                elicitation_code_hook=aws_lex.CfnBot.ElicitationCodeHookInvocationSettingProperty(
                    enable_code_hook_invocation=slot.code_hook_invocation,
                    invocation_label=slot.invocation_label,
                )
            ),
            prompt_specification=aws_lex.CfnBot.PromptSpecificationProperty(
                max_retries=slot.max_retries,
                message_groups_list=[
                    aws_lex.CfnBot.MessageGroupProperty(
                        message=aws_lex.CfnBot.MessageProperty(
                            plain_text_message=aws_lex.CfnBot.PlainTextMessageProperty(
                                value=slot.message,
                            ),
                        ),
                    ),
                ],
            ),
        ),
    )


def intent_as_cfn(intent: Intent | BuiltInIntent) -> aws_lex.CfnBot.IntentProperty:
    match intent:
        case Intent():
            return aws_lex.CfnBot.IntentProperty(
                name=intent.name,
                sample_utterances=[
                    aws_lex.CfnBot.SampleUtteranceProperty(utterance=utterance)
                    for utterance in intent.sample_utterances
                ],
                slots=[slot_as_cfn(slot) for slot in intent.slots],
                slot_priorities=[
                    aws_lex.CfnBot.SlotPriorityProperty(priority=i, slot_name=slot.name)
                    for i, slot in enumerate(intent.slots, start=1)
                ],
                dialog_code_hook=aws_lex.CfnBot.DialogCodeHookSettingProperty(enabled=intent.dialog_code_hook),
                fulfillment_code_hook=aws_lex.CfnBot.FulfillmentCodeHookSettingProperty(
                    enabled=intent.fulfillment_code_hook,
                ),
            )
        case BuiltInIntent():
            return aws_lex.CfnBot.IntentProperty(
                name=intent.name,
                parent_intent_signature=intent.parent_intent_signature,
                dialog_code_hook=aws_lex.CfnBot.DialogCodeHookSettingProperty(enabled=intent.dialog_code_hook),
                fulfillment_code_hook=aws_lex.CfnBot.FulfillmentCodeHookSettingProperty(
                    enabled=intent.fulfillment_code_hook,
                ),
            )


def bot_as_cfn(bot: Bot) -> aws_lex.CfnBot.BotLocaleProperty:
    return aws_lex.CfnBot.BotLocaleProperty(
        locale_id=bot.locale_id,
        nlu_confidence_threshold=bot.nlu_confidence_threshold,
        intents=[intent_as_cfn(intent) for intent in bot.intents],
    )

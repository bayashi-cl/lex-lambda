from lex_bot.bot import Bot, BuiltInIntent, Intent, Slot

slot1 = Slot(
    name="Slot1",
    slot_type="AMAZON.FreeFormInput",
    required=True,
    max_retries=1,
    message="slot1 message",
    code_hook_invocation=True,
)

slot2 = Slot(
    name="Slot2",
    slot_type="AMAZON.FreeFormInput",
    required=True,
    max_retries=1,
    message="slot2 message",
    code_hook_invocation=True,
)

fallback_intent = BuiltInIntent(
    name="FallbackIntent",
    parent_intent_signature="AMAZON.FallbackIntent",
    dialog_code_hook=True,
)

main_intent = Intent(
    name="MainIntent",
    sample_utterances=["main"],
    slots=[slot1, slot2],
    dialog_code_hook=True,
)

bot = Bot(
    name="Bot",
    intents=[fallback_intent, main_intent],
    locale_id="ja_JP",
    nlu_confidence_threshold=0.5,
)

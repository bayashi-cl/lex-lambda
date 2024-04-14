from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

# TODO
KendraResponse = Any
ActiveContext = Any
RuntimeHints = Any
Interpretation = Any
ProposedNextState = Any
Transcription = Any
ImageResponseCard = Any


class CommonBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=lambda s: to_camel(s).removesuffix("_"),
        populate_by_name=True,
    )


class DialogAction(CommonBaseModel):
    slot_elicitation_style: Literal["Default", "SpellByLetter", "SpellByWord"] = "Default"
    slot_to_elicit: str | None = None
    type_: Literal["Close", "ConfirmIntent", "Delegate", "ElicitIntent", "ElicitSlot"]


class SlotValue(CommonBaseModel):
    original_value: str
    interpreted_value: str
    resolved_values: list[str]


class Slot(CommonBaseModel):
    shape: Literal["Scalar", "List"]
    value: SlotValue
    values: list[SlotValue] | None = None


class Intent(CommonBaseModel):
    confirmation_state: Literal["Confirmed", "Denied", "None"]
    name: str
    slots: dict[str, Slot | None]
    state: Literal["Failed", "Fulfilled", "FulfillmentInProgress", "InProgress", "ReadyForFulfillment", "Waiting"]
    kendra_response: KendraResponse | None = None


class SessionState(CommonBaseModel):
    session_attributes: dict[str, str] = Field(default_factory=dict)
    active_contexts: list[ActiveContext] | None = None
    runtime_hints: RuntimeHints | None = None
    dialog_action: DialogAction = DialogAction(type_="Delegate")
    intent: Intent
    originating_request_id: str


class Bot(CommonBaseModel):
    id_: str
    name: str
    locale_id: str
    version: str
    alias_id: str
    alias_name: str


class LexEvent(CommonBaseModel):
    message_version: Literal["1.0"]
    invocation_source: Literal["DialogCodeHook", "FulfillmentCodeHook"]
    input_mode: Literal["DTMF", "Speech", "Text"]
    response_content_type: Literal["audio/mpeg", "audio/ogg", "audio/pcm", "text/plain; charset=utf-8"]
    session_id: str
    input_transcript: str
    invocation_label: str | None = None
    bot: Bot
    interpretations: list[Interpretation]
    proposed_next_state: ProposedNextState | None = None
    request_attributes: dict[str, str] = Field(default_factory=dict)
    session_state: SessionState
    transcriptions: list[Transcription] | None = None


class Message(CommonBaseModel):
    content_type: Literal["CustomPayload", "ImageResponseCard", "PlainText", "SSML"]
    content: str
    image_response_card: ImageResponseCard | None = None


class LexResponse(CommonBaseModel):
    session_state: SessionState
    messages: list[Message] | None = None
    request_attributes: dict[str, str] = Field(default_factory=dict)

from pydantic import BaseModel, Field


class SlotType(BaseModel):
    name: str


class Slot(BaseModel):
    name: str
    slot_type: str | SlotType
    required: bool
    code_hook_invocation: bool
    max_retries: int
    message: str

    @property
    def slot_type_name(self) -> str:
        match self.slot_type:
            case str():
                return self.slot_type
            case SlotType():
                return self.slot_type.name

    @property
    def invocation_label(self) -> str:
        return self.name


class Intent(BaseModel):
    name: str
    sample_utterances: list[str]
    slots: list[Slot]
    dialog_code_hook: bool = False
    fulfillment_code_hook: bool = False


class BuiltInIntent(BaseModel):
    name: str
    parent_intent_signature: str  # TODO: Literal?
    dialog_code_hook: bool = False
    fulfillment_code_hook: bool = False


class Bot(BaseModel):
    name: str
    intents: list[Intent | BuiltInIntent]
    slot_types: list[SlotType] = Field(default=[])
    locale_id: str
    nlu_confidence_threshold: float

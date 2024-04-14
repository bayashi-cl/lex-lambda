from lex_bot.bot import Bot, Slot
from lex_bot.event import DialogAction, LexEvent, LexResponse, SlotValue
from lex_bot.event import Slot as EventSlot


class LexSession:
    def __init__(self, event: LexEvent, bot: Bot) -> None:
        self._event = event
        self._bot = bot

    def delegate(self) -> LexResponse:
        self._event.session_state.dialog_action = DialogAction(type_="Delegate")
        return LexResponse(session_state=self._event.session_state, request_attributes=self._event.request_attributes)

    def elicit_slot(self, slot: str | Slot) -> LexResponse:
        self._event.session_state.dialog_action = DialogAction(
            type_="ElicitSlot",
            slot_to_elicit=self.__slot_name(slot),
        )
        return LexResponse(
            session_state=self._event.session_state,
            request_attributes=self._event.request_attributes,
        )

    def transfer_intent(self) -> LexResponse:
        raise NotImplementedError

    @staticmethod
    def __slot_name(slot: str | Slot) -> str:
        match slot:
            case str():
                return slot
            case Slot():
                return slot.name

    def set_slot_value(self, slot: str | Slot, value: str) -> None:
        self._event.session_state.intent.slots[self.__slot_name(slot)] = EventSlot(
            shape="Scalar",
            value=SlotValue(original_value=value, interpreted_value=value, resolved_values=[]),
        )

    def has_slot_value(self, slot: str | Slot) -> bool:
        slot_data = self._event.session_state.intent.slots[self.__slot_name(slot)]
        return slot_data is not None

    def get_slot_value(self, slot: str | Slot) -> str | None:
        slot_data = self._event.session_state.intent.slots[self.__slot_name(slot)]
        if slot_data is None:
            return None

        return slot_data.value.interpreted_value

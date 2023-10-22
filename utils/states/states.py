from aiogram.dispatcher.filters.state import State, StatesGroup


class States(StatesGroup):
    change_custom_lore = State()


class AdminStates(StatesGroup):
    send_message = State()
    send_message_link = State()

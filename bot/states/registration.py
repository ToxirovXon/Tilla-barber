"""Ro'yxatdan o'tish bosqichlari (FSM)."""
from aiogram.fsm.state import State, StatesGroup


class Registration(StatesGroup):
    full_name = State()
    phone = State()
    birthday = State()

from aiogram.fsm.state import State, StatesGroup

class Form(StatesGroup):
    weight = State()
    height = State()
    age = State()
    activity = State()
    city = State()

class Food(StatesGroup):
    calories_per_100g = State()
    food_weight = State()

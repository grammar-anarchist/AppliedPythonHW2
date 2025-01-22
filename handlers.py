import yaml
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db_handler import db
from states import Form, Food
from api_requests import calories_goal_func, water_goal_func, product_calories

router = Router()

with open("constants.yaml", "r") as f:
    constants = yaml.safe_load(f)

@router.message(Command("start"))
async def start(message: Message):
    await message.reply(constants['START'])

@router.message(Command("help"))
async def help(message: Message):
    await message.reply(constants['HELP'])

@router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    await message.reply(constants['ASK_WEIGHT'])
    await state.set_state(Form.weight)

async def proccess_int_input(message: Message, state: FSMContext, key: str, next_state, reply_message: str):
    try:
        answer = int(message.text)
    except:
        await message.reply(constants['ASK_ERROR'])
        return

    await state.update_data({key: answer})
    await message.reply(reply_message)
    await state.set_state(next_state)

@router.message(Form.weight)
async def process_weight(message: Message, state: FSMContext):
    await proccess_int_input(message, state, 'weight', Form.height, constants['ASK_HEIGHT'])

@router.message(Form.height)
async def process_height(message: Message, state: FSMContext):
    await proccess_int_input(message, state, 'height', Form.age, constants['ASK_AGE'])

@router.message(Form.age)
async def process_age(message: Message, state: FSMContext):
    await proccess_int_input(message, state, 'age', Form.activity, constants['ASK_ACTIVITY'])

@router.message(Form.activity)
async def process_activity(message: Message, state: FSMContext):
    await proccess_int_input(message, state, 'activity', Form.city, constants['ASK_CITY'])

@router.message(Form.city)
async def process_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    data = await state.get_data()
    calories_goal = await calories_goal_func(data['weight'], data['height'], data['age'])
    water_goal = await water_goal_func(data['weight'], data['city'])
    db.add_user(message.from_user.id, **data, water_goal=water_goal, calories_goal=calories_goal)
    await state.clear()
    await message.reply(constants['REGISTRATION_SUCCESS'].format(calories=calories_goal, water=water_goal))

@router.message(Command("log_water"))
async def log_water(message: Message):
    try:
        args = message.text.split(maxsplit=1)
        assert len(args) == 2
        water = int(args[1])
    except:
        await message.reply(constants['LOG_WATER_ERROR'])
        return

    try:
        remaining = db.add_water(message.from_user.id, water)
    except:
        await message.reply(constants['DATABASE_ERROR'])
        return

    await message.reply(constants['WATER_LOGGED'].format(amount=water, remaining=remaining))
    
@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext):
    try:
        args = message.text.split(maxsplit=1)
        assert len(args) == 2
    except:
        await message.reply(constants['LOG_FOOD_ERROR'])
        return

    try:
        calories = await product_calories(args[1])
    except:
        await message.reply(constants['OPENFOOD_API_ERROR'])
        return

    await state.set_state(Food.calories_per_100g)
    await state.update_data(calories_per_100g=calories)
    await state.set_state(Food.food_weight)
    
    await message.reply(constants['ASK_FOOD_WEIGHT'])

@router.message(Food.food_weight)
async def process_calories_per_100g(message: Message, state: FSMContext):
    try:
        weight = int(message.text)
    except:
        await message.reply(constants['ASK_FOOD_ERROR'])
        return

    data = await state.get_data()
    calories = int(data['calories_per_100g'] * weight / 100)
    await state.clear()

    try:
        remaining = db.add_calories(message.from_user.id, calories)
    except:
        await message.reply(constants['DATABASE_ERROR'])
        return

    await message.reply(constants['FOOD_LOGGED'].format(amount=calories, remaining=remaining))

@router.message(Command("/log_workout"))
async def log_workout(message: Message):
    try:
        args = message.text.split(maxsplit=1)
        assert len(args) == 3
        time_spent = int(args[2])
    except:
        await message.reply(constants['LOG_WORKOUT_ERROR'])
        return
    
    equivalent = time_spent // 30
    calories_spent = 300 * equivalent
    water_increase = 200 * equivalent

    try:
        db.log_training(message.from_user.id, water_increase, calories_spent)
    except:
        await message.reply(constants['DATABASE_ERROR'])
        return

    await message.reply(constants['WORKOUT_LOGGED'].format(calories=calories_spent, water=water_increase))

@router.message(Command("/check_progress"))
async def check_progress(message: Message):
    try:
        calories_goal, calories_consumed, calories_burnt, water_goal, water_consumed = \
            db.get_progress(message.from_user.id)
    except:
        await message.reply(constants['DATABASE_ERROR'])
        return

    await message.reply(constants['PROGRESS'].format(
        calories_goal=calories_goal,
        calories_consumed=calories_consumed,
        calories_burnt=calories_burnt,
        calories_left=calories_goal - calories_consumed + calories_burnt,
        water_goal=water_goal,
        water_consumed=water_consumed,
        water_left=water_goal - water_consumed
    ))

def setup_handlers(dp):
    dp.include_router(router)

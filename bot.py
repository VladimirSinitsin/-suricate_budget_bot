from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from tools import AccessMiddleware

import db.dbms as db
from bot_config import TOKEN, SELECTED_USERS


# Инициализация бота.
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
# dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(AccessMiddleware(SELECTED_USERS))


@dp.message_handler(commands=['start'])
async def send_welcome(message):
    # содание клавиатуры с кнопками
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("/total")
    item2 = KeyboardButton("/help")
    markup.add(item1, item2)
    await message.answer('Привет! Я бот для отслеживания долгов друг другу.\n'
                         'Просто отправь фото с QR-кодом на чеке или запиши расход,\n'
                         'например: такси - 160.\n\n', reply_markup=markup)


@dp.message_handler(commands=['help'])
async def send_help(message):
    await message.answer('Если тебе нужна помощь, то обратись к разработчику: @VSinitsin\n'
                         'Ниже приведён список доступных команд:\n'
                         '/last_costs - последние 5 расходов\n'
                         '/all_costs - все расходы\n'
                         '/all_payers - все сурикаты\n'
                         '/add_payer - добавить суриката\n\n'
                         '/clear_costs - очистить все расходы\n'
                         '/clear_db - очистить всю базу данных')


@dp.message_handler(commands=['total'])
async def total(message):
    await message.answer(db.total_credit())


async def send_costs(message, costs):
    if not costs:
        await message.answer("Список пуст.")
    else:
        answer = ''
        for cost in costs:
            answer += cost + f" для удаления нажмите /del{cost.split(')')[0]}\n\n"
        await message.answer(answer)


@dp.message_handler(commands=['last_costs'])
async def last_costs(message):
    costs = db.all_costs()[-5:]
    await send_costs(message, costs)


@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_cost(message):
    row_id = int(message.text[4:])
    db.delete_cost(row_id)
    answer_message = "Расход удалён"
    await message.answer(answer_message)


@dp.message_handler(commands=['all_costs'])
async def all_costs(message):
    costs = db.all_costs()
    await send_costs(message, costs)


@dp.message_handler(commands=['all_payers'])
async def all_payers(message):
    answer = 'Сурикаты:\n\n'
    for payer in db.all_payers():
        answer += payer + '\n'
    await message.answer(answer)


@dp.message_handler(commands=['add_payer'])
async def add_payer(message):
    pass


@dp.message_handler(commands=['clear_costs'])
async def clear_all_costs(message):
    db.delete_all_costs()
    await message.answer("Все расходы удалены!")


@dp.message_handler(commands=['clear_db'])
async def clear_db(message):
    db.delete_db()
    await message.answer("База данных полностью очищена!")


if __name__ == '__main__':
    executor.start_polling(dp)

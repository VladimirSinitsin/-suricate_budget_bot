from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import db.dbms as db
from bot_config import TOKEN


# Инициализация бота.
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


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
    await message.answer('Если тебе нужна помощь, то обратись к разработчику: @VladimirSinitsin.\n'
                         'Ниже приведён список доступных команд:\n'
                         '/last_costs - последние 5 расходов\n'
                         '/all_costs - все расходы\n'
                         '/all_payers - все сурикаты\n'
                         '/add_payer - добавить суриката\n\n'
                         '/delete_costs - очистить все расходы\n'
                         '/delete_db - очистить всю базу данных')


@dp.message_handler(commands=['total'])
async def total(message):
    await message.answer(db.total_credit())


if __name__ == '__main__':
    executor.start_polling(dp)

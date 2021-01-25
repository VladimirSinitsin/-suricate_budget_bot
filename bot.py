from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import db.dbms as db
from bot_config import TOKEN, SELECTED_USERS
from tools import AccessMiddleware, parse_custom_cost_message


# Состояния для приёма ответов-сообщений от пользователя.
class Statements(StatesGroup):
    adding_payer = State()


custom_cost = {'дата': None,
               'плательщик': None,
               'сумма': None,
               'магазин': None}


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
    """
    Функция для вывода списка расходов.
    :param message:
    :param costs: выводимый список расходов.
    :return:
    """
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


# Обработка команд для удаления расхода по его id.
@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_cost(message):
    row_id = int(message.text[4:])
    db.delete_cost(row_id)
    answer_message = "❌ Расход удалён ❌"
    await message.answer(answer_message)


@dp.message_handler(commands=['all_costs'])
async def all_costs(message):
    costs = db.all_costs()
    await send_costs(message, costs)


@dp.message_handler(commands=['all_payers'])
async def all_payers(message):
    payers = db.all_payers()
    if not payers:
        await message.answer("Сурикаты не найдены 😢")
    else:
        answer = 'Сурикаты:\n\n'
        for payer in payers:
            answer += payer + '\n'
        await message.answer(answer)


@dp.message_handler(commands=['add_payer'])
async def add_payer(message):
    await Statements.adding_payer.set()
    await message.answer("Введите имя плательщика")


# Приём имени плательщика.
@dp.message_handler(state=Statements.adding_payer)
async def process_message(message, state):
    async with state.proxy() as data:
        data['text'] = message.text
        name = data['text']
        try:
            db.add_payer(name)
        except Exception as e:
            print('Возникла ошибка: ', e)
            await message.answer(f"🆘 Что-то пошло не так: {e}")
        else:
            await message.answer(f"✅ {name} добавлен(-а) в список сурикатов!")
            if len(db.all_payers()) < 2:
                await message.answer("Сурикату одиноко 😢\nДобавьте ему пару через /add_payer")
            else:
                await message.answer("💃 Ого! Да у нас тут целая сурикачья семья.\nМожем приступать к ведению бюджета!")
    await state.finish()


@dp.message_handler(commands=['clear_costs'])
async def clear_all_costs(message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    confirmation = InlineKeyboardButton("🚫 Очистить расходы 🚫", callback_data="Очистить расходы")
    keyboard.add(confirmation)

    await message.answer("❗️ Вы точно хотите очистить все расходы? ❗️\n"
                         "‼️ Это действие невозможно отменить. ‼️\n\n"
                         "(если Вы ошиблись, то просто продолжайте пользоваться ботом, не нажимая кнопку ниже)",
                         reply_markup=keyboard)


# Удаление расходов, подтверждённое пользователем.
@dp.callback_query_handler(lambda c: c.data == "Очистить расходы")
async def confirmed_clear_costs(callback_query):
    db.delete_all_costs()
    await bot.send_message(callback_query.message.chat.id, "✅ Все расходы удалены!")


@dp.message_handler(commands=['clear_db'])
async def clear_db(message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    confirmation = InlineKeyboardButton("🚫 Очистить БД 🚫", callback_data="Очистить БД")
    keyboard.add(confirmation)

    await message.answer("❗️ Удаление базы данных (БД) полностью очистит списки расходов и плательщиков. ❗️\n"
                         "‼ Это действие невозможно отменить. Вы точно хотите очистить БД? ‼\n\n"
                         "(если Вы ошиблись, то просто продолжайте пользоваться ботом, не нажимая кнопку ниже)",
                         reply_markup=keyboard)


# Удаление БД, подтверждённое пользователем.
@dp.callback_query_handler(lambda c: c.data == "Очистить БД")
async def confirmed_clear_db(callback_query):
    db.delete_db()
    await bot.send_message(callback_query.message.chat.id, "✅ База данных полностью очищена!")


async def get_keyboard_payers(alias):
    """
    Возвращает клавиатуру с плательщиками.
    :alias: псевдоним, добавяемый перед callback_data у кнопок.
    :return: клавиатура с плательщиками.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    for payer in db.all_payers():
        button = InlineKeyboardButton(payer, callback_data=str(alias+payer))
        keyboard.add(button)
    return keyboard


@dp.message_handler(content_types=["text"])
async def add_custom_cost(message):
    global custom_cost

    if len(db.all_payers()) < 2:
        await message.answer("⚠️ Сурикатов должно быть двое. ⚠️\n"
                             "Добавьте их через команду /add_payer")
    else:
        try:
            custom_cost = parse_custom_cost_message(message.text)
        except Exception as e:
            print('Возникла ошибка: ', e)
            await message.answer("🆘 Что-то пошло не так...\n"
                                 "⚠ Вводите расходы в виде МАГАЗИН - СТОИМОСТЬ. ⚠")
        else:
            await message.answer("Кто оплатил покупку? 🧐", reply_markup=await get_keyboard_payers(alias='custom_'))


@dp.callback_query_handler(lambda c: c.data[:6] == 'custom')
async def select_payer(callback_query):
    global custom_cost

    custom_cost['плательщик'] = callback_query.data[7:]
    db.add_cost(custom_cost)

    await bot.send_message(callback_query.message.chat.id,
                           f"✅ Покупка от {custom_cost['дата']} в {custom_cost['магазин']} "
                           f"на сумму {custom_cost['сумма']} рублей добавлена в расходы, "
                           f"которые оплатил(-а) {custom_cost['плательщик']}.")


if __name__ == '__main__':
    executor.start_polling(dp)

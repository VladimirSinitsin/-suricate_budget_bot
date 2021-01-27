import numpy as np
import PIL.Image as Image
from typing import Dict, List
from aiogram import Bot
from aiogram import types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.contrib.middlewares.logging import LoggingMiddleware

import db.dbms as db
from bot_config import TOKEN, SELECTED_USERS
from tools import AccessMiddleware, parse_custom_cost_message, scan_qr_image


# Состояния для приёма ответов-сообщений от пользователя.
class Statements(StatesGroup):
    adding_payer = State()


cost = {'дата': '',
        'плательщик': '',
        'сумма': 0.0,
        'магазин': ''}
products = []
individual_products = []


# Инициализация бота.
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(AccessMiddleware(SELECTED_USERS))
# dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # содание клавиатуры с кнопками
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = KeyboardButton("/total")
    item2 = KeyboardButton("/help")
    markup.add(item1, item2)
    await message.answer('Привет! Я бот для отслеживания долгов друг другу.\n'
                         'Просто отправь фото с QR-кодом на чеке или запиши расход,\n'
                         'например: такси - 160.\n\n', reply_markup=markup)


@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    await message.answer('Если тебе нужна помощь, то обратись к разработчику: @VSinitsin\n'
                         'Ниже приведён список доступных команд:\n'
                         '/last_costs - последние 5 расходов\n'
                         '/all_costs - все расходы\n'
                         '/all_payers - все сурикаты\n'
                         '/add_payer - добавить суриката\n\n'
                         '/clear_costs - очистить все расходы\n'
                         '/clear_db - очистить всю базу данных')


@dp.message_handler(commands=['total'])
async def total(message: types.Message):
    await message.answer(db.total_credit())


async def send_costs(message: types.Message, costs: List):
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


# Обработка команд для удаления расхода по его id.
@dp.message_handler(lambda message: message.text.startswith('/del'))
async def del_cost(message: types.Message):
    row_id = int(message.text[4:])
    db.delete_cost(row_id)
    answer_message = "❌ Расход удалён ❌"
    await message.answer(answer_message)
    # После удаления выводим все расходы.
    await send_costs(message, db.all_costs())


@dp.message_handler(commands=['last_costs'])
async def last_costs(message: types.Message):
    costs = db.all_costs()[-5:]
    await send_costs(message, costs)


@dp.message_handler(commands=['all_costs'])
async def all_costs(message: types.Message):
    costs = db.all_costs()
    await send_costs(message, costs)


@dp.message_handler(commands=['all_payers'])
async def all_payers(message: types.Message):
    payers = db.all_payers()
    if not payers:
        await message.answer("Сурикаты не найдены 😢")
    else:
        answer = '🌿 Сурикаты:\n\n'
        for payer in payers:
            answer += payer + '\n'
        await message.answer(answer)


@dp.message_handler(commands=['add_payer'])
async def add_payer(message: types.Message):
    await Statements.adding_payer.set()
    await message.answer("Введите имя плательщика")


# Приём имени плательщика.
@dp.message_handler(state=Statements.adding_payer)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        name = data['text']
        try:
            db.add_payer(name)
        except Exception as e:
            print('Возникла ошибка: ', e)
            await message.answer(f"🆘 Что-то пошло не так:\n{e}")
        else:
            await message.answer(f"✅ {name} добавлен(-а) в список сурикатов!")
            if len(db.all_payers()) < 2:
                await message.answer("Сурикату одиноко 😢\nДобавьте ему пару через /add_payer")
            else:
                await message.answer("💃 Ого! Да у нас тут целая сурикачья семья.\nМожем приступать к ведению бюджета!")
    await state.finish()


@dp.message_handler(commands=['clear_costs'])
async def clear_all_costs(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    confirmation = InlineKeyboardButton("🚫 Очистить расходы 🚫", callback_data="Очистить расходы")
    keyboard.add(confirmation)

    await message.answer("❗️ Вы точно хотите очистить все расходы? ❗️\n"
                         "‼️ Это действие невозможно отменить. ‼️\n\n"
                         "(если Вы ошиблись, то просто продолжайте пользоваться ботом, не нажимая кнопку ниже)",
                         reply_markup=keyboard)


# Удаление расходов, подтверждённое пользователем.
@dp.callback_query_handler(lambda c: c.data == "Очистить расходы")
async def confirmed_clear_costs(callback_query: types.CallbackQuery):
    db.delete_all_costs()
    # Удаляем кнопку подтверждения.
    await callback_query.message.delete_reply_markup()
    await bot.send_message(callback_query.message.chat.id, "✅ Все расходы удалены!")


@dp.message_handler(commands=['clear_db'])
async def clear_db(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=1)
    confirmation = InlineKeyboardButton("🚫 Очистить БД 🚫", callback_data="Очистить БД")
    keyboard.add(confirmation)

    await message.answer("❗️ Удаление базы данных (БД) полностью очистит списки расходов и плательщиков. ❗️\n"
                         "‼ Это действие невозможно отменить. Вы точно хотите очистить БД? ‼\n\n"
                         "(если Вы ошиблись, то просто продолжайте пользоваться ботом, не нажимая кнопку ниже)",
                         reply_markup=keyboard)


# Удаление БД, подтверждённое пользователем.
@dp.callback_query_handler(lambda c: c.data == "Очистить БД")
async def confirmed_clear_db(callback_query: types.CallbackQuery):
    db.delete_db()
    # Удаляем кнопку подтверждения.
    await callback_query.message.delete_reply_markup()
    await bot.send_message(callback_query.message.chat.id, "✅ База данных полностью очищена!")


async def get_keyboard_payers(alias: str) -> InlineKeyboardMarkup:
    """
    Возвращает клавиатуру с плательщиками.
    :alias: псевдоним, добавяемый перед callback_data у кнопок.
    :return: клавиатура с плательщиками.
    """
    keyboard = InlineKeyboardMarkup(row_width=2)
    for payer in db.all_payers():
        button = InlineKeyboardButton(payer, callback_data=str(alias+payer))
        keyboard.insert(button)
    return keyboard


# Отлавливает плательщика у простого расхода.
@dp.callback_query_handler(lambda c: c.data[:6] == 'simple')
async def select_payer_simple(callback_query: types.CallbackQuery):
    global cost

    cost['плательщик'] = callback_query.data[7:]
    db.add_cost(cost)

    # Удаляем кнопки выбора.
    await callback_query.message.delete_reply_markup()
    await bot.send_message(callback_query.message.chat.id,
                           f"✅ Покупка от {cost['дата']} в {cost['магазин']} "
                           f"на сумму {cost['сумма']} рублей добавлена в расходы, "
                           f"которые оплатил(-а) {cost['плательщик']}.")


# Расход, записанный вручную. Например, "такси - 160".
@dp.message_handler(content_types=["text"])
async def add_custom_cost(message: types.Message):
    global cost

    if len(db.all_payers()) < 2:
        await message.answer("⚠️ Сурикатов должно быть двое. ⚠️\n"
                             "Добавьте их через команду /add_payer")
    else:
        try:
            cost = parse_custom_cost_message(message.text)
        except Exception as e:
            print('Возникла ошибка: ', e)
            await message.answer("🆘 Что-то пошло не так...\n"
                                 "⚠ Вводите расходы в виде МАГАЗИН - СТОИМОСТЬ. ⚠")
        else:
            await message.answer("Кто оплатил покупку? 🧐", reply_markup=await get_keyboard_payers(alias='simple_'))


# Обработка фото чека с qr-кодом.
@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    global cost
    global products

    # Получаем изображение в виде экземпляра io.BytesIO.
    bytes_of_photo = await bot.download_file_by_id(message.photo[-1].file_id)

    # Приводим к numpy массиву.
    img = Image.open(bytes_of_photo)
    img = np.array(img)

    try:
        # Получаем данные из qr-кода на изображении и обрабатываем их (основной расход глобальный).
        ticket_data = await scan_qr_image(img)
        is_simple, products = await parse_ticket(ticket_data)
    except Exception as e:
        print('Возникла ошибка: ', e)
        await message.answer(f"🆘 Что-то пошло не так:\n{e}")
        return

    # Если чек простой (нельзя считать каждый продукт отдельно), то обрабатываем его как кастомный расход.
    if is_simple:
        await message.answer("Мне не удалось детально просканировать чек 🥺\n\n"
                             f"Чек из {cost['магазин']} на сумму {cost['сумма']}.\n\n"
                             "Но я могу добавить сумму в нём как общий расход (пополам).\n"
                             "Выберите, кто оплатил покупку.", reply_markup=await get_keyboard_payers(alias='simple_'))
    else:
        keyboard = InlineKeyboardMarkup(row_width=2)
        button1 = InlineKeyboardButton("❇️ Пополам", callback_data="Пополам")
        button2 = InlineKeyboardButton("🆚 Уточнить", callback_data="Уточнить")
        keyboard.add(button1, button2)
        await message.answer("💙 Отлично! Мне удалось полностью обработать чек.\n\n"
                             f"Чек из {cost['магазин']} на сумму {cost['сумма']}.\n\n"
                             "Если Вы уверены, что все товары общие, то можно делить сумму чека на двоих пополам ❇️\n"
                             "Иначе, Вы можете уточнить плательщика для каждого товара 🆚", reply_markup=keyboard)


async def parse_ticket(data: Dict) -> (bool, List):
    """
    Обрабатывает данные из чека. Сохраняет их в глобальный расход.
    :param data: данные, полученные из qr-кода чека.
    :return: являяется ли чек "простым"; список продуктов.
    """
    global cost

    if not data:
        raise Exception("Не удалось считать qr-код, чек пустой.")
    if len(db.all_payers()) < 2:
        raise Exception("⚠️ Сурикатов должно быть двое. ⚠️\n"
                        "Добавьте их через команду /add_payer")

    date = data['operation']['date']
    day, time = date.split('T')
    y, m, d = day.split('-')
    cost['дата'] = f"{d}/{m} {time}"

    cost['сумма'] = int(data['operation']['sum'])/100

    if 'ticket' not in data:
        is_simple = True
        cost['магазин'] = "_неизвестном магазине_"
        products = []
        return is_simple, products

    is_simple = False
    # В старых чеках нет поля retailPlace, поэтому название берём из ['seller']['name'].
    if 'retailPlace' not in data['ticket']['document']['receipt']:
        cost['магазин'] = data['seller']['name']
    else:
        cost['магазин'] = data['ticket']['document']['receipt']['retailPlace']
    products = await parse_items(data['ticket']['document']['receipt']['items'])
    return is_simple, products


async def parse_items(items: List) -> List:
    """
    Обрабатывает товары.
    :param items: список товаров-словарей.
    :return: список товаров-списов (0 - название, 1 - сумма).
    """
    products = []
    for item in items:
        products.append([item['name'], int(item['sum'])/100])
    return products


# Если в отсканированном чеке не было индивидуальных покупок.
@dp.callback_query_handler(lambda c: c.data == "Пополам")
async def half_ticket(callback_query: types.CallbackQuery):
    global cost

    cost['сумма'] = cost['сумма'] / 2
    await bot.send_message(callback_query.message.chat.id, "Кто оплатил покупку? 🧐",
                           reply_markup=await get_keyboard_payers(alias='simple_'))


# Если в отсканированном чеке были индивидуальные покупки.
@dp.callback_query_handler(lambda c: c.data == "Уточнить")
async def individual_ticket(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.message.chat.id, "Кто оплатил покупку? 🧐",
                           reply_markup=await get_keyboard_payers(alias='ticket_'))


# После того, как узнали плательщика.
@dp.callback_query_handler(lambda c: c.data[:6] == 'ticket')
async def select_payer_simple(callback_query: types.CallbackQuery):
    global cost
    global individual_products

    individual_products = []

    await callback_query.message.delete_reply_markup()

    cost['плательщик'] = callback_query.data[7:]

    await bot.send_message(callback_query.message.chat.id, "🆚 Для каждого товара выберите покупателя.\n"
                                                           "💤 Если товар общий, то ничего не нажимайте.\n"
                                                           "Когда закончите, то нажмите кнопку в самом конце списка ✅")

    # Выводим все товары отдельно с кнопками выбора плательщика.
    # В callback_data делаем префикс с номером товара.
    for index, product in enumerate(products):
        name, sum = product
        await bot.send_message(callback_query.message.chat.id, f"{sum} - {name}",
                               reply_markup=await get_keyboard_payers(alias=f'{index}_'))

    ending_keyboard = InlineKeyboardMarkup(row_width=1)
    button = InlineKeyboardButton('✅ Заврешить уточнение', callback_data='Заврешить уточнение')
    ending_keyboard.add(button)
    await bot.send_message(callback_query.message.chat.id, "Если все товары определены, то нажмите кнопку ниже",
                           reply_markup=ending_keyboard)


# Обработка каждого товара.
@dp.callback_query_handler(lambda c: c.data.split('_')[0].isdigit())
async def select_payer_product(callback_query: types.CallbackQuery):
    product_index = int(callback_query.data.split('_')[0])
    current_product = products[product_index]
    product_name, sum = current_product
    payer = callback_query.data.split('_')[1]

    # Если индивидуальный товар плательщика, то просто вычитаем из общей суммы.
    # Иначе запоминаем, чтобы потом прибавить отдельно.
    cost['сумма'] -= sum
    if payer != cost['плательщик']:
        individual_products.append(current_product)

    await callback_query.message.delete()


@dp.callback_query_handler(lambda c: c.data == "Заврешить уточнение")
async def ending_ticket(callback_query: types.CallbackQuery):
    global cost
    global individual_products

    # Делим общую (без индивидуальных товаров) сумму пополам.
    cost['сумма'] = cost['сумма'] / 2
    # И прибывляем сумму каждого индивидуального товара того, кто не платил.
    for product in individual_products:
        _, sum = product
        cost['сумма'] += sum

    db.add_cost(cost)

    await callback_query.message.delete_reply_markup()
    await bot.send_message(callback_query.message.chat.id,
                           f"✅ Покупка от {cost['дата']} в {cost['магазин']} "
                           f"на сумму {cost['сумма']} рублей добавлена в расходы, "
                           f"которые оплатил(-а) {cost['плательщик']}.")


if __name__ == '__main__':
    executor.start_polling(dp)

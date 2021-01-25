import json
import cv2
import datetime
import pytz
import re
from pyzbar import pyzbar
from typing import Dict, List
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

import db.dbms as db
from nalog_python import NalogRuPython


TIME_ZONE = 'Europe/Moscow'


class AccessMiddleware(BaseMiddleware):
    def __init__(self, users_id: List):
        self.users_id = users_id
        super().__init__()

    async def on_process_message(self, message, _):
        if int(message.from_user.id) not in self.users_id:
            await message.answer("Отказано в доступе!\nДля уточнения обратись к разработчику @VSinitsin")
            raise CancelHandler()



def get_now_formatted() -> str:
    return _get_now_datetime().strftime("%d/%m %H:%M")


def _get_now_datetime() -> datetime.datetime:
    tz = pytz.timezone(TIME_ZONE)
    now = datetime.datetime.now(tz)
    return now


def parse_custom_cost_message(raw_message: str) -> Dict:
    """
    Обрабатывает сообщения с расходом в виде текста.
    :param raw_message: расход (форма: МАГАЗИН - СУММА)
    :return: словарь-расход.
    """
    try:
        # Разбиваем на две части, и убираем пробел, если есть в конце названия.
        shop, price = raw_message.split('-')
        if shop[-1] == " ":
            shop = shop[:-1]
        # Находим число-цену.
        price = re.findall(r"[-+]?\d*\.\d+|\d+", price)[0]
        price = float(price) / 2
    except Exception as e:
        raise e
    return {'магазин': shop, 'сумма': price, 'дата': get_now_formatted()}


def scan_qr_image(filename: str) -> str:
    """
    Обрабатывает qr-код чека на снимке.
    :param filename:
    :return: данные по чеку в виде json дампа.
    """
    image = cv2.imread(filename)
    # Находим qr-коды на изображении и обрабатываем их.
    qr_codes = [barcode for barcode in pyzbar.decode(image) if barcode.type == 'QRCODE']

    if len(qr_codes) > 1:
        raise Exception("Ошибка! Распознано больше одного qr-кода.")

    qr_data = qr_codes[0].data.decode("utf-8")
    # Обрабатываем текст из qr-кода чека.
    client = NalogRuPython()
    ticket = client.get_ticket(qr_data)
    result = json.dumps(ticket, indent=4, ensure_ascii=False)
    return result

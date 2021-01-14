import json
import cv2
import datetime
import pytz
from pyzbar import pyzbar

import db.dbms as db
from nalog_python import NalogRuPython


TIME_ZONE = 'Europe/Moscow'


def get_now_formatted() -> str:
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    tz = pytz.timezone(TIME_ZONE)
    now = datetime.datetime.now(tz)
    return now


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

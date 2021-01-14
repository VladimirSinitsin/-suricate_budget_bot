import json
import cv2
from pyzbar import pyzbar

from nalog_python import NalogRuPython


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

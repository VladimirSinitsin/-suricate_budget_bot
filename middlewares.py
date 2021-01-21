"""Аутентификация — пропускаем сообщения только от избранных Telegram аккаунтов"""
from typing import List
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware


class AccessMiddleware(BaseMiddleware):
    def __init__(self, users_id: List):
        self.users_id = users_id
        super().__init__()

    async def on_process_message(self, message, _):
        if int(message.from_user.id) not in self.users_id:
            await message.answer("Отказано в доступе!\nДля уточнения обратись к разработчику @VSinitsin")
            raise CancelHandler()

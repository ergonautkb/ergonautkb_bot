import logging
from datetime import timedelta

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils.callback_data import CallbackData

from db import ChatUser, Session
from messages import (
    get_full_welcome_message,
    get_returning_welcome_message,
    get_welcome_message,
)
from settings import API_TOKEN, CHAT_ID

logging.basicConfig(level=logging.INFO)

MUTED_PERMISSIONS = types.ChatPermissions(
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
    False,
)
DEFAULT_PERMISSIONS = types.ChatPermissions(
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
    True,
)

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()

dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

rules_cb = CallbackData("rules", "user_id", "action")


def get_rules_button(user_id: int) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "I've read the rules!",
            callback_data=rules_cb.new(user_id=user_id, action="agree"),
        )
    )
    return markup


def get_chat_user(chat_id: int, user_id: int) -> ChatUser | None:
    with Session() as s:
        return s.get(ChatUser, (chat_id, user_id))


def create_chat_user(chat_id: int, user_id: int) -> None:
    with Session() as s:
        user = ChatUser(chat_id=chat_id, user_id=user_id)
        s.add(user)
        s.commit()


def update_chat_user(
    chat_id: int, user_id: int, agreed_with_rules: bool = True
) -> None:
    with Session() as s:
        user = s.get(ChatUser, (chat_id, user_id))
        user.agreed_with_rules = agreed_with_rules
        s.add(user)
        s.commit()


@dp.message_handler(content_types=types.ContentType.NEW_CHAT_MEMBERS, chat_id=CHAT_ID)
async def send_welcome_message(message: types.Message):
    for user in message.new_chat_members:
        name = user.full_name
        if user.username:
            name = "@" + user.username

        db_user = get_chat_user(message.chat.id, user.id)
        if db_user is not None and db_user.agreed_with_rules:
            await message.reply(
                get_returning_welcome_message(user.id, name),
                parse_mode=types.ParseMode.HTML,
            )
            return

        create_chat_user(message.chat.id, user.id)

        await message.chat.restrict(
            user.id, until_date=timedelta(days=3000), permissions=MUTED_PERMISSIONS
        )
        await message.reply(
            get_welcome_message(user.id, name),
            parse_mode=types.ParseMode.HTML,
            reply_markup=get_rules_button(user_id=user.id),
        )


@dp.callback_query_handler(rules_cb.filter(action="agree"), chat_id=CHAT_ID)
async def rules_agree(query: types.CallbackQuery, callback_data: dict[str, str]):
    user_id = int(callback_data.get("user_id", 0))
    if query.from_user.id != user_id:
        return

    name = query.from_user.full_name
    if query.from_user.username:
        name = "@" + query.from_user.username

    if get_chat_user(query.message.chat.id, user_id) is None:
        create_chat_user(query.message.chat.id, user_id)

    await query.message.chat.restrict(user_id, permissions=DEFAULT_PERMISSIONS)

    update_chat_user(query.message.chat.id, user_id)

    await query.message.edit_text(
        get_full_welcome_message(query.from_user.id, name),
        parse_mode=types.ParseMode.HTML,
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

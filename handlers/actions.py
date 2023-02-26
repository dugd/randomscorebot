import random
from datetime import datetime, timedelta

from pytz import timezone
from aiogram import types
from dispatcher import dp, bot
from bot import db_bot
from config import TIMEZONE


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    chat = message.chat
    if chat.type in [types.ChatType.GROUP, types.ChatType.SUPERGROUP]:
        if not await db_bot.check_chat_id(chat.id):
            message = (
                "Thanks for adding me to the group!\n"
                "I'm a bot that randomly adds (or subtracts) the score every day.")
            await bot.send_message(chat.id, message)
            await db_bot.insert_chat_id(chat.id)
    else:
        me = await bot.me
        await message.answer(f'Add me to the group and write a command <b>/start@{me.username}</b>')


@dp.message_handler(commands=['score'])
async def cmd_score(message: types.Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if not await db_bot.check_chat_id(chat_id):
        await message.answer("Add me to a group or use a command <b>/start@{me.username}</b>")
        return

    mention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.full_name}</a>'
    user = list(await db_bot.get_user_info(chat_id, user_id))
    tz = timezone(TIMEZONE)
    date = (datetime.now(tz) + timedelta(hours=3)).date()
    message_text = ""

    if user and user[1] == date:
        message_text += f'{mention}, you played today!\n'
    else:
        new_points = random.randint(-5, 10)
        if user:
            user[0] += new_points
            user[1] = date
            await db_bot.update_user_info(chat_id, user_id, *user)
        else:
            user = [new_points, date]
            await db_bot.insert_user_info(chat_id, user_id, *user)

        if new_points >= 0:
            message_text += f'{mention}, you get <b>{new_points}</b> score!\n'
        elif new_points < 0:
            message_text += f'{mention}, you loose <b>{-new_points}</b> score!\n'

    message_text += f"You have <b>{user[0]}</b> score."
    await message.answer(message_text)


async def top(chat_id, anti=False):
    top_users = await db_bot.get_sort_user_info(chat_id, anti)
    message_text = f'top 10 players{" from end" if anti else ""}:\n'
    for i, (user_id, points) in enumerate(top_users):
        user = await bot.get_chat_member(chat_id, user_id)
        message_text += f'<b>{i + 1}. {user.user.full_name[:10]}</b> — <b>{points}</b> points\n'
    return message_text


@dp.message_handler(commands=['top'])
async def cmd_top(message: types.Message):
    chat_id = message.chat.id

    if not await db_bot.check_chat_id(chat_id):
        await message.answer("Add me to a group or use a command <b>/start@{me.username}</b>")
        return

    await message.answer(await top(chat_id, anti=False))


@dp.message_handler(commands=['antitop'])
async def cmd_antitop(message: types.Message):
    chat_id = message.chat.id

    if not await db_bot.check_chat_id(chat_id):
        await message.answer("Add me to a group or use a command <b>/start@{me.username}</b>")
        return

    await message.answer(await top(chat_id, anti=True))


@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    message_text = (
        'Commands:\n'
        '<b>/score</b> - Add randomly to score from -5 to 10. Can be used once a day.\n'
        '<b>/top</b> - Show top 10 players.\n'
        '<b>/help</b> - Commands.'
    )
    await message.answer(message_text)
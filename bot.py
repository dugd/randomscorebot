from aiogram import executor
import handlers
from dispatcher import dp
from db import BotDB

db_bot = BotDB()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

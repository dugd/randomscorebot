from config import DB_CONFIG
import aiomysql
import datetime


class BotDB:
    def __init__(self, config=DB_CONFIG):
        self.config = config
        self.conn = None

    async def connect(self):
        self.conn = await aiomysql.connect(**self.config)

    @staticmethod
    def _check_connect(func):
        async def wrapper(*args, **kwargs):
            self = args[0]
            if not (self.conn and not self.conn.closed):
                await self.connect()
            return await func(*args, **kwargs)

        return wrapper

    @_check_connect
    async def check_chat_id(self, chat_id):
        async with self.conn.cursor() as cursor:
            await cursor.execute("""SELECT id FROM chat_ids WHERE id = %s""", (chat_id, ))
            res = True if await cursor.fetchone() else False
            return res

    @_check_connect
    async def insert_chat_id(self, chat_id):
        async with self.conn.cursor() as cursor:
            await cursor.execute("""INSERT INTO chat_ids (id) VALUES (%s)""", (chat_id, ))
            await self.conn.commit()

    @_check_connect
    async def get_user_info(self, chat_id, user_id):
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
            SELECT points, last_use_date FROM group_scores WHERE chat_id = %s AND user_id = %s""", (chat_id, user_id, ))
            res = await cursor.fetchone()
            return res if res else set()

    @_check_connect
    async def insert_user_info(self, chat_id, user_id, points, date):
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
            INSERT INTO group_scores (chat_id, user_id, points, last_use_date) 
            VALUES (%s, %s, %s, %s)""", (chat_id, user_id, points, date, ))
            await self.conn.commit()

    @_check_connect
    async def update_user_info(self, chat_id, user_id, points, date):
        async with self.conn.cursor() as cursor:
            await cursor.execute("""
            UPDATE group_scores SET points = %s, last_use_date = %s
            WHERE chat_id = %s AND user_id = %s""", (points, date, chat_id, user_id, ))
            await self.conn.commit()

    @_check_connect
    async def get_sort_user_info(self, chat_id, anti=False):
        async with self.conn.cursor() as cursor:
            await cursor.execute(f"""
            SELECT user_id, points FROM group_scores WHERE chat_id = %s 
            ORDER BY points {"" if anti else "DESC"} limit 10""", (chat_id, ))
            res = await cursor.fetchall()
            return res if res else set()

    async def close(self):
        await self.conn.close()


if __name__ == '__main__':
    db = BotDB()
    try:
        pass
    finally:
        db.close()
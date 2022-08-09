from aiogram.types import ContentType, Message
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
import sqlite3 as sq
import os
from aiogram.contrib.fsm_storage.memory import MemoryStorage
storage = MemoryStorage()
bot = Bot(token='5463577812:AAEeYWZMkwYjRxf3Gm_cEsGZvYxG__ohMY0')

dp = Dispatcher(bot, storage=storage)
@dp.message_handler(commands="start")
async def start(message: types.Message):
    id_user = message.from_id
    print(id_user)
    await message.answer(f'Привет {message.from_user.full_name} \n\n' '<i>Выбери кнопку в меню.</i>',
                          parse_mode=types.ParseMode.HTML)
    try:
        sql_request(f'ALTER TABLE words ADD COLUMN  "{id_user}" INTEGER ')
    except:
        pass

#___________________________Чистка_слов________________________
def clear_text(a):
   a = str(a)
   a = a.split("'")
   a = ''.join(a)
   a = a.split(")")
   a = ''.join(a)
   a = a.split("(")
   a = ''.join(a)
   a = a.split(",")
   a = '|'.join(a)
   a = a.split("]")
   a = ''.join(a)
   a = a.split("[")
   a = ''.join(a)
   return a
# __________________________ Создание_базы _____________________

def sql_request(reqwest):
    global base, cur
    base = sq.connect('words.db')
    cur = base.cursor()
    if base:
        print('База подключена')
    cur.execute(reqwest)
    base.commit()

def sql_words (reqwest):
    global base, cur
    base = sq.connect('words.db')
    cur = base.cursor()
    cur.execute(reqwest).fetchall()
    base.commit()
    return cur.execute(reqwest).fetchall()
@dp.message_handler(commands="words")
async def load_qwes(message: types.Message):
    id_user = message.from_id
    bodymessage = sql_words(f'SELECT Infinitive, Past_Simple, Participle, Перевод FROM words WHERE '
                            f'[{id_user}]  IS NULL LIMIT 1')
    await message.reply(f'новые слова \n{clear_text(bodymessage)}')






executor.start_polling(dp)

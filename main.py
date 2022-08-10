from aiogram.types import ContentType, Message
from aiogram import Bot, Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
import sqlite3 as sq
import os
import asyncio
import aioschedule
from aiogram.contrib.fsm_storage.memory import MemoryStorage
storage = MemoryStorage()
bot = Bot(token='5463577812:AAEeYWZMkwYjRxf3Gm_cEsGZvYxG__ohMY0')

dp = Dispatcher(bot, storage=storage)
@dp.message_handler(commands="start")
async def start(message: types.Message):
    global id_user
    id_user = message.from_id
    print(id_user)
    number_question = 1
    await message.answer(f'Привет {message.from_user.full_name} \n\n' '<i>Выбери кнопку в меню.</i>',
                          parse_mode=types.ParseMode.HTML)
    sql_add_user_base('CREATE TABLE IF NOT EXISTS users (id PRIMARY KEY,number_question)')
    try:
        sql_save_id('INSERT  INTO users VALUES (?,?)', id_user, number_question)
        # sql_request(f'ALTER TABLE words ADD COLUMN  "{id_user}" INTEGER ')
    except:
        pass

@dp.message_handler(commands="test")
async def get_test(message: types.Message):
    user = message.from_id
    bodymessage = sql_words(f'SELECT Infinitive, Past_Simple, Participle FROM words WHERE '
                            f'[{user}]  IS NULL LIMIT 1')
    await message.answer(f'Введи перевод \n{clear_text(bodymessage)}')
    await message.answer('dasda')


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

def clear_user(a):
   a = str(a)
   a = a.split("'")
   a = ''.join(a)
   a = a.split(")")
   a = ''.join(a)
   a = a.split("(")
   a = ''.join(a)
   a = a.split(",")
   a = ''.join(a)
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
    if cur:
        print('Запрос прошел')
    cur.execute(reqwest)
    base.commit()

def sql_save_id(reqwest,user,number_question):
    global base, cur
    base = sq.connect('words.db')
    cur = base.cursor()
    if cur:
        print('Запрос прошел')
    cur.execute(reqwest, (user,number_question))
    base.commit()

def sql_add_user_base(reqwest):
    global base, cur
    base = sq.connect('words.db')
    cur = base.cursor()
    if base:
        print('База подключена')
    base.execute(reqwest)
    base.commit()

def sql_words (reqwest):
    global base, cur
    base = sq.connect('words.db')
    cur = base.cursor()
    cur.execute(reqwest).fetchall()
    base.commit()
    return cur.execute(reqwest).fetchall()




@dp.message_handler()
async def load_qwes():
    users = sql_words(f'SELECT*FROM users')
    for user in users:
        print(type(user[1]))
        bodymessage = sql_words(f'SELECT Infinitive, Past_Simple, Participle, Перевод FROM words WHERE id_number = {str(user[1])}')
        await bot.send_message(chat_id=648226895,text= f'новые слова \n{clear_text(bodymessage)}')


async def scheduler():
    times = '02:13','21:19','21:20'
    for time in times:
        aioschedule.every().day.at(time_str=time).do(load_qwes)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)




async def on_startup(dp):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp,on_startup=on_startup)

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
from aiogram.utils.exceptions import (MessageToEditNotFound, MessageCantBeEdited, MessageCantBeDeleted,
                              MessageToDeleteNotFound)
from contextlib import suppress

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

# ______________________________________проверка перевода__________________________________________________
class FSMtest(StatesGroup): #сохранение запрашиваемого перевода в машину состояния
    request = State()
    id = State()
@dp.message_handler(commands="test", state=None)
async def get_name(message: types.Message):

    await FSMtest.request.set()
    user = message.from_id
    print(user)
    number_question = sql_words(f'SELECT * FROM users WHERE id IS {str(user)}')
    number_question = (number_question[0])[1]
    bodymessage = sql_words(
    f'SELECT Infinitive, Past_Simple, Participle FROM words WHERE id_number = {str(number_question)}')
    await message.answer(f'Введи перевод \n{clear_text(bodymessage)}')


#
@dp.message_handler(state=FSMtest.request)
async def load_request(message: types.Message, state: FSMContext):
    if message.text == '/test':
        await message.answer(f'<i>Нужно было ввести перевод на русском языке.</i>\n\n'
                             f' <i>Можешь заново нажать кнопку и</i>\n\n'
                             f' <i>ввести перевод на русском языке</i>',parse_mode=types.ParseMode.HTML)
        await state.finish()
    else:
        async with state.proxy() as data:
            data['id'] = message.from_id
            data['request'] = message.text

        await get_request(state)  # тут нужно записать в базу+1
        await state.finish()


async def get_request(state): # вставка перевода в запрос sql
    global base, cur
    base = sq.connect('words.db')
    cur = base.cursor()
    async with state.proxy() as data:
        translate = list(data.values())
        translate_word =str.lower(translate[1])
        iduser=str(translate[0])
        print(iduser)
        print(translate_word)
        number_question = cur.execute(f'SELECT * FROM users WHERE id IS {str(iduser)}').fetchall()
        number_question = (number_question[0])[1]
        reqwest = f"SELECT Перевод FROM words WHERE id_number = {number_question} AND Перевод  LIKE '%{translate_word}%'"
        bodyreqwest = None
        bodyreqwest = cur.execute(reqwest).fetchall()
        print(bodyreqwest)
    if not bodyreqwest:
        await bot.send_message(iduser,text='Не правильно!!! Учи дальше!!!')
    else:
        await bot.send_message(iduser,text='Правильно! Ты молодец!')
        new_question = number_question + 1
        print(new_question)
        cur.execute(f'UPDATE USERS SET number_question={new_question} WHERE id IS {str(iduser)} ')
        base.commit()
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


def sql_restore_number_question(reqwest):
    global base, cur
    base = sq.connect('words.db')
    cur = base.cursor()
    if cur:
        print('Запрос прошел')
    cur.execute(reqwest)
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
        print(user)
        bodymessage = sql_words(f'SELECT Infinitive, Past_Simple, Participle, Перевод FROM words WHERE id_number = {str(user[1])}')
        await bot.send_message(chat_id=user[0],text= f'новые слова \n{clear_text(bodymessage)}')


async def scheduler():
    times = '15:07','14:59','14:53'
    for time in times:
        aioschedule.every().day.at(time_str=time).do(load_qwes)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)




async def on_startup(dp):
    asyncio.create_task(scheduler())


if __name__ == '__main__':
    executor.start_polling(dp,on_startup=on_startup)

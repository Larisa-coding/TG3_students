import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import TOKEN
import sqlite3
import logging

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    with sqlite3.connect('school_data.db') as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                grade TEXT NOT NULL)
        ''')
        conn.commit()

init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Пожалуйста, введите правильный возраст числом.")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Какой у тебя класс?")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    data = await state.get_data()
    try:
        with sqlite3.connect('school_data.db') as conn:
            cur = conn.cursor()
            cur.execute('''
                INSERT INTO users (name, age, grade) VALUES (?, ?, ?)''',
                (data['name'], data['age'], data['grade']))
            conn.commit()
        await message.answer(f"Тебя зовут {data['name']}. Тебе {data['age']} лет. Твой класс - {data['grade']}.")
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя: {e}")
        await message.answer("Произошла ошибка при сохранении данных. Пожалуйста, попробуйте еще раз.")
    finally:
        await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

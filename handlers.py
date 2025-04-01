from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import kb
import text
from misc import dp
from db import check_inn_in_db

# Переменная для хранения текущего типа организации
type_of_org = {}


@dp.message(Command("start"))
async def start_handler(msg: Message):
    """Обработчик команды /start"""
    user_id = msg.from_user.id
    type_of_org.pop(user_id, None)  # Сброс выбранного типа
    print(f"✅ Обработчик /start сработал для {user_id}")
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@dp.message()
async def message_handler(msg: Message):
    """Обработчик ввода ИНН"""
    user_id = msg.from_user.id
    inn = msg.text.strip()

    if user_id in type_of_org:
        table = "Dilers" if type_of_org[user_id] == "diler" else "LPU"
        res = await check_inn_in_db(inn, table)
        if res:
            await msg.answer(text.text_yes, reply_markup=kb.menu)
        else:
            await msg.answer(text.text_no, reply_markup=kb.menu)

        type_of_org.pop(user_id, None)  # Сброс после проверки
    else:
        # Пользователь ввёл ИНН без выбора типа
        await msg.answer(text.missing_type, reply_markup=kb.menu)


@dp.message(F.text == "Меню")
async def menu_handler(msg: Message):
    """Обработчик кнопки Меню"""
    await msg.answer(text.menu, reply_markup=kb.menu)


@dp.callback_query(F.data == "diler")
async def select_diler(callback: CallbackQuery):
    """Обработчик выбора 'Дилер'"""
    user_id = callback.from_user.id
    type_of_org[user_id] = "diler"
    await callback.message.answer(text.gen_text, reply_markup=kb.menu)


@dp.callback_query(F.data == "lpu")
async def select_lpu(callback: CallbackQuery):
    """Обработчик выбора 'ЛПУ'"""
    user_id = callback.from_user.id
    type_of_org[user_id] = "lpu"
    await callback.message.answer(text.gen_text, reply_markup=kb.menu)

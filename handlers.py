from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import kb
import text
from misc import dp
from db import check_inn_in_db

# Глобальная переменная для хранения типа организации
type_of_org = []


@dp.message(Command("start"))
async def start_handler(msg: Message):
    """Обработчик команды /start"""
    print(f"✅ Обработчик /start сработал для {msg.from_user.id}")
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@dp.message()
async def message_handler(msg: Message):
    """Обработчик ввода ИНН"""
    if type_of_org:
        table = "Dilers" if type_of_org[0] == "diler" else "LPU"
        res = await check_inn_in_db(msg.text, table)
        if res:
            await msg.answer(text.text_yes, reply_markup=kb.menu)
        else:
            await msg.answer(text.text_no, reply_markup=kb.menu)

        type_of_org.clear()
    else:
        type_of_org.clear()


@dp.message(F.text.in_(["Меню", "Выйти в меню", "◀️ Выйти в меню"]))
async def menu(msg: Message):
    """Обработчик кнопки меню"""
    await msg.answer(text.menu, reply_markup=kb.menu)


@dp.callback_query(F.data == "diler")
async def send_msg_inn_dealer(callback: CallbackQuery):
    """Выбор дилера"""
    await callback.message.answer(text.gen_text)
    await callback.message.answer(text.gen_exit, reply_markup=kb.exit_kb)
    type_of_org.append("diler")


@dp.callback_query(F.data == "lpu")
async def send_msg_inn_lpu(callback: CallbackQuery):
    """Выбор ЛПУ"""
    await callback.message.answer(text.gen_text)
    await callback.message.answer(text.gen_exit, reply_markup=kb.exit_kb)
    type_of_org.append("lpu")


from misc import dp

__all__ = ["dp"]

from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import kb
import text
from misc import dp
from db import check_inn_in_db  # Импортируем новую функцию проверки

type_of_org = []


@dp.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@dp.message()
async def message_handler(msg: Message):
    if len(type_of_org):
        table = "Dilers" if type_of_org[0] == "dealer" else "LPU"
        res = await check_inn_in_db(msg.text, table)
        if res:
            await msg.answer(text.text_yes, reply_markup=kb.menu)
        else:
            await msg.answer(text.text_no, reply_markup=kb.menu)

        type_of_org.clear()
    else:
        type_of_org.clear()


@dp.message(F.text == "Меню")
@dp.message(F.text == "Выйти в меню")
@dp.message(F.text == "◀️ Выйти в меню")
async def menu(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)


@dp.callback_query(F.data == "dealer")
async def send_msg_inn_dealer(callback: CallbackQuery):
    await callback.message.answer(text.gen_text)
    await callback.message.answer(text.gen_exit, reply_markup=kb.exit_kb)
    type_of_org.append("dealer")


@dp.callback_query(F.data == "lpu")
async def send_msg_inn_lpu(callback: CallbackQuery):
    await callback.message.answer(text.gen_text)
    await callback.message.answer(text.gen_exit, reply_markup=kb.exit_kb)
    type_of_org.append("lpu")

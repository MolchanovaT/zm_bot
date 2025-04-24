from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import kb
import text
from misc import dp
from db import check_inn_in_db

type_of_org = {}


@dp.message(Command("start"))
async def start_handler(msg: Message):
    user_id = msg.from_user.id
    type_of_org.pop(user_id, None)
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@dp.message()
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    inn = msg.text.strip()

    if user_id not in type_of_org:
        await msg.answer(text.missing_type, reply_markup=kb.menu)
        return

    table = "Dilers" if type_of_org[user_id] == "diler" else "LPU"
    result = await check_inn_in_db(inn, table)

    if result == "approved":
        await msg.answer(text.text_yes, reply_markup=kb.menu)
    elif result == "denied":
        await msg.answer("❌ Отгрузка запрещена", reply_markup=kb.menu)
    elif result.startswith("denied_date:"):
        date = result.split(":", 1)[1]
        await msg.answer(f"❌ Отгрузка запрещена, дата запрета: {date}", reply_markup=kb.menu)
    elif result.startswith("pending:"):
        date = result.split(":", 1)[1]
        await msg.answer(f"⌛ На рассмотрении, подано: {date}", reply_markup=kb.menu)
    else:
        await msg.answer(text.text_no, reply_markup=kb.menu)

    type_of_org.pop(user_id, None)


@dp.message(F.text == "Меню")
async def menu_handler(msg: Message):
    await msg.answer(text.menu, reply_markup=kb.menu)


@dp.callback_query(F.data == "diler")
async def select_diler(callback: CallbackQuery):
    user_id = callback.from_user.id
    type_of_org[user_id] = "diler"
    await callback.message.answer(text.gen_text, reply_markup=kb.menu)


@dp.callback_query(F.data == "lpu")
async def select_lpu(callback: CallbackQuery):
    user_id = callback.from_user.id
    type_of_org[user_id] = "lpu"
    await callback.message.answer(text.gen_text, reply_markup=kb.menu)

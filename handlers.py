from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import kb
import text
# from misc import dp, db_pool
from misc import dp

type_of_org = []


# async def check_inn_in_db(inn: str):
#     async with db_pool.acquire() as conn:
#         row = await conn.fetchrow("SELECT name FROM Dilers WHERE inn = $inn AND allowed = TRUE", inn)
#         if row is None:
#             return False
#         else:
#             return True


@dp.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(text.greet.format(name=msg.from_user.full_name), reply_markup=kb.menu)


@dp.message()
async def message_handler(msg: Message):
    if len(type_of_org):
        # здесь должен быть поиск в БД по ИНН
        # если type_of_org = дилер, тогда в таблице дилеров
        # если type_of_org = лпу, тогда в таблице лпу
        # res = await check_inn_in_db(msg.text)
        # if res:
        #     await msg.answer(text.text_yes, reply_markup=kb.menu)
        # else:
        #     await msg.answer(text.text_no, reply_markup=kb.menu)

        await msg.answer(text.text_yes, reply_markup=kb.menu)
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
    type_of_org.append(callback.data)


@dp.callback_query(F.data == "lpu")
async def send_msg_inn_lpu(callback: CallbackQuery):
    await callback.message.answer(text.gen_text)
    await callback.message.answer(text.gen_exit, reply_markup=kb.exit_kb)
    type_of_org.append(callback.data)
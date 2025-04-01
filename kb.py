from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

# Главное меню: выбор типа контрагента
menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Дилер", callback_data="diler"),
     InlineKeyboardButton(text="ЛПУ", callback_data="lpu")],
])

# Кнопка "Меню" (обычная кнопка — ReplyKeyboard)
menu_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Меню")]],
    resize_keyboard=True
)

from aiogram.types import (
    ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
)


MAIN_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
MAIN_MARKUP.add('Оставить заявку').add('Купить товар').add('Мой баланс')


ADMIN_MARKUP = ReplyKeyboardMarkup(resize_keyboard=True)
ADMIN_MARKUP.add('Оставить заявку').add(
    'Купить товар').add('Мой баланс').add('Отправить сообщение пользователям')


REQUEST_MARKUP = InlineKeyboardMarkup(row_width=2)
REQUEST_MARKUP.add(
    InlineKeyboardButton(text='Продажа', callback_data='sells'),
    InlineKeyboardButton(text='Производство', callback_data='production'),
    InlineKeyboardButton(text='Оказание услуг', callback_data='services'),
)

PLATFORM_MARKUP = InlineKeyboardMarkup(row_width=1)
PLATFORM_MARKUP.add(
    InlineKeyboardButton(text='Telegram', callback_data='Telegram'),
    InlineKeyboardButton(text='WhatsApp', callback_data='WhatsApp'),
    InlineKeyboardButton(text='Viber', callback_data='Viber'),
)

PAYMENT_MARKUP = InlineKeyboardMarkup(row_width=2)
PAYMENT_MARKUP.add(
    InlineKeyboardButton('Купить 1', callback_data='1 item'),
    InlineKeyboardButton('Купить 2', callback_data='2 item'),
)

ERROR_MESSAGE = 'Если честно.. я не знаю о чем ты... Попробуй /start'

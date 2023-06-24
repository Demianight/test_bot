from aiogram import Dispatcher, Bot, executor
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from app.markups import (
    MAIN_MARKUP, REQUEST_MARKUP, PLATFORM_MARKUP, PAYMENT_MARKUP, ADMIN_MARKUP,
    ERROR_MESSAGE
)
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.models import Base
from app.database import SessionLocal, engine
from app.crud import (
    get_or_create_user, get_users, create_request, get_requests,
    increment_balance, get_balance
)


# .env stuff required, but to lazy to add it
YOO_TOKEN = '381764678:TEST:59907'
TG_TOKEN = '5993078785:AAFDE8xERTgjYsgK5_k2EO2_ab4aOxYX8gQ'
ADMIN_ID = [1650629059, ]


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


db = get_db()


storage = MemoryStorage()
bot = Bot(TG_TOKEN)
dp = Dispatcher(bot, storage=storage)


# Commands


@dp.message_handler(commands=['start'])
async def greet(message: Message):
    get_or_create_user(db, message.from_user.id)

    markup = ADMIN_MARKUP if message.from_user.id in ADMIN_ID else MAIN_MARKUP
    await message.answer(
        'Рад тебя видеть!',
        reply_markup=markup
    )


@dp.message_handler(commands=['cancel'], state='*')
async def cancel(message: Message, state: FSMContext):
    await state.finish()
    await message.answer(
        'Заявка отменена(( ждем вас снова', reply_markup=MAIN_MARKUP
    )


@dp.message_handler(commands=['users'])
async def send_users_info(message: Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer(
            ERROR_MESSAGE
        )
        return
    await message.answer(get_users(db))


@dp.message_handler(commands=['requests'])
async def send_requests_info(message: Message):
    if message.from_user.id not in ADMIN_ID:
        await message.answer(
            ERROR_MESSAGE
        )
        return
    await message.answer(get_requests(db))

# Payment


@dp.message_handler(text='Купить товар')
async def handle_payment(message: Message):
    await message.answer(
        'Выберите количество единиц ниже.', reply_markup=PAYMENT_MARKUP
    )


@dp.callback_query_handler()
async def handle_callback(callback: CallbackQuery):
    if callback.data not in ['1 item', '2 item']:
        return

    amount = int(callback.data[0])
    await bot.delete_message(
        callback.from_user.id, callback.message.message_id
    )

    await bot.send_invoice(
        callback.from_user.id,
        f'Покупка {amount} единиц',
        f'Покупка {amount} единиц',
        f'{amount} item',
        YOO_TOKEN,
        'RUB',
        [{'amount': 20000 * amount, 'label': f'{amount} единиц'}],
        start_parameter='test'
    )


@dp.pre_checkout_query_handler()
async def process_pre_checkout(pre_checkout:  PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def finish_payment(message: Message):
    if message.successful_payment.invoice_payload in ['1 item', '2 item']:
        increment_balance(
            db,
            message.from_user.id,
            int(message.successful_payment.invoice_payload[0])
        )
        await message.answer('Покупка успешно совершна! Баланс пополнен.')


# Balance check
@dp.message_handler(text='Мой баланс')
async def send_balance(message: Message):
    await message.answer(get_balance(db, message.from_user.id))


# Request sending


class NewOrder(StatesGroup):
    type = State()
    platform = State()
    budget = State()
    phone = State()


@dp.message_handler(text='Оставить заявку')
async def handle_request(message: Message):
    await NewOrder.type.set()
    await message.answer(
        'Сейчас вы пройдете процедуру отправки заявки. Если по какой то '
        'причине вы решили отменить ее заполнение, просто напишите /cancel'
    )
    await message.reply(
        'Какое направление вашего бизнеса.', reply_markup=REQUEST_MARKUP
    )


@dp.callback_query_handler(state=NewOrder.type)
async def add_request_type(callback: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        callback.from_user.id, callback.message.message_id
    )

    async with state.proxy() as data:
        data['type'] = callback.data
    await callback.message.answer(
        'Выберите платформу на которой хотите запустить чат бота',
        reply_markup=PLATFORM_MARKUP
    )
    await NewOrder.next()


@dp.callback_query_handler(state=NewOrder.platform)
async def add_request_platform(callback: CallbackQuery, state: FSMContext):
    await bot.delete_message(
        callback.from_user.id, callback.message.message_id
    )
    async with state.proxy() as data:
        data['platform'] = callback.data
    await callback.message.answer(
        'Опишите ваш бюджет двумя числами,'
        ' первое число - от, второе - до. Например: 100 4000',
    )
    await NewOrder.next()


@dp.message_handler(state=NewOrder.budget)
async def add_request_budget(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['budget'] = list(map(int, message.text.split()))
    await message.answer(
        'И наконец введите свой номер телефона в формате: +7**********',
    )
    await NewOrder.next()


@dp.message_handler(state=NewOrder.phone)
async def add_request_phone(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    await message.answer(
        'Ваша заявка отправлена. Удачи!',
        reply_markup=MAIN_MARKUP
    )
    db_data = await state.get_data()
    request = create_request(db, db_data, message.from_user.id)
    await bot.send_message(ADMIN_ID[-1], request)

    await state.finish()


# Admin


class MessageSend(StatesGroup):
    message = State()


@dp.message_handler(
    lambda message: message.from_user.id in ADMIN_ID,
    text='Отправить сообщение пользователям'
)
async def message_spam_prep(message: Message):
    await message.answer('Отправь мне сообщение которое надо всем разослать')
    await MessageSend.message.set()


@dp.message_handler(state=MessageSend.message)
async def message_spam(message: Message, state: FSMContext):
    users = get_users(db)
    text = message.text
    for user in users:
        await bot.send_message(user.tg_id, text)

    await message.answer('Все сообщения успешно разосланы')
    await state.finish()


# Error handling


@dp.message_handler()
async def bad_request(message: Message):
    await message.reply(ERROR_MESSAGE)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

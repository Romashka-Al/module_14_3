from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Инфо')
button2 = KeyboardButton(text='Рассчитать')
button3 = KeyboardButton(text='Купить')
kb.add(button)
kb.add(button2)
kb.add(button3)

inline_keyboard = InlineKeyboardMarkup()
inline_keyboard.add(
    InlineKeyboardButton("Рассчитать норму калорий", callback_data="calories"),
    InlineKeyboardButton("Формулы расчета", callback_data="formulas")
)

catalog_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Счастье', callback_data='product_buying')],
        [InlineKeyboardButton(text='Уют', callback_data='product_buying')],
        [InlineKeyboardButton(text='Любовь', callback_data='product_buying')],
        [InlineKeyboardButton(text='Радость', callback_data='product_buying')]
    ]
)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(commands=['start'])
async def start(sms):
    await sms.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=kb)


@dp.message_handler(text=['Инфо'])
async def info(sms):
    await sms.answer('Жми "Расчёт" для индивидуального подсчёта калорий')


@dp.message_handler(text=['Рассчитать'])
async def starter(sms):
    await sms.answer("Выберите опцию", reply_markup=inline_keyboard)


@dp.message_handler(text=['Купить'])
async def get_buying_list(sms):
    with open('1.jpg', 'rb') as img:
        await sms.answer_photo(img, 'Название: Продукт 1 - Счастье | Описание: ❤ | Цена: 100')
    with open('2.jpg', 'rb') as img:
        await sms.answer_photo(img, 'Название: Продукт 2 - Уют| Описание: ❤❤ | Цена: 200')
    with open('3.jpg', 'rb') as img:
        await sms.answer_photo(img, 'Название: Продукт 3 - Любовь| Описание: ❤❤❤ | Цена: 300')
    with open('4.jpg', 'rb') as img:
        await sms.answer_photo(img, 'Название: Продукт 4 - Радость| Описание: ❤❤❤❤ | Цена: 400')
    await sms.answer("Выберите продукт для покупки:", reply_markup=catalog_kb)


@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_sms(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.callback_query_handler(text=['formulas'])
async def get_formulas(call):
    await call.message.answer("10 * вес + 6.25 * рост - 4.92 * возраст + 5")
    await call.answer()


@dp.message_handler(text=['Инфо'])
async def info(sms):
    await sms.answer('Жми "Расчёт" для индивидуального подсчёта калорий')


@dp.callback_query_handler(text=['calories'])
async def set_age(call):
    await UserState.age.set()
    await call.message.answer("Введите свой возраст:")


@dp.message_handler(state=UserState.age)
async def set_growth(sms, state):
    try:
        await state.update_data(age=float(sms.text))
    except ValueError:
        await sms.answer('Введено не число, введите ещё раз')
        await UserState.age.set()
    finally:
        await sms.answer('Введите свой рост:')
        await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(sms, state):
    try:
        await state.update_data(growth=float(sms.text))
    except ValueError:
        await sms.answer('Введено не число, введите ещё раз')
        await UserState.growth.set()
    finally:
        await sms.answer('Введите свой вес:')
        await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(sms, state):
    try:
        await state.update_data(weight=float(sms.text))
    except ValueError:
        await sms.answer('Введено не число, введите ещё раз')
        await UserState.weight.set()
    finally:
        data = await state.get_data()
        await sms.answer(f'Норма калорий: {10 * data["weight"] + 6.25 * data["growth"] - 4.92 * data["age"] + 5}')
        await state.finish()


@dp.message_handler()
async def start(sms):
    await sms.answer("Введите команду /start, чтобы начать")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

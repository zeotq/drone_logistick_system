import asyncio
import user_data_save
#import tgz_user
#import aiogram.utils.markdown as md
from manual_data_base_interaction import data_base
from aiogram import Bot, Dispatcher, executor, types#, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext


with open("token.yoda", "r") as f:
    TOKEN = f.readline()
    bot = Bot(TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)


class Form(StatesGroup):
    adress = State()
    time = State()

kb_1 = [
        [
            types.KeyboardButton(text="/drone"),
            types.KeyboardButton(text="/help"),
            types.KeyboardButton(text="/close")
        ],
]
keyboard_start = types.ReplyKeyboardMarkup(
    keyboard=kb_1,
    resize_keyboard=True,
)
kb_2 = [
        [
            types.KeyboardButton(text="/place"),
            types.KeyboardButton(text="/orders"),
            types.KeyboardButton(text="/cancel")
        ],
        [
            types.KeyboardButton(text="/close")
        ],
]
keyboard_dronedb = types.ReplyKeyboardMarkup(
    keyboard=kb_2,
    resize_keyboard=True,
)
help_info = "Функционал для пользователя:\n/drone:\n  /place - сделать заказ\n  /orders - список заказов пользователя\n  /cancel - отменить заказ\n\nФункционал для модераторов:\n  /show_drone_db - показать список дронов и их статусы\n  /reset_drone_db - сбросить статусы дронов"

async def on_startup():
    ...

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer('<b>Добро пожаловать!</b>', parse_mode="HTML", reply_markup = keyboard_start, allow_sending_without_reply=True)
    user_data_save.data_writer(dict(message.from_user))
    await message.delete()  

@dp.message_handler(commands=['menu'])
async def menu_command(message: types.Message):
    await message.reply(text = "/drone - для работы с дронами\n/help - получить помощь\n/close - закрыть меню", reply_markup = keyboard_start, allow_sending_without_reply=True)
    await message.delete()

@dp.message_handler(commands=['drone'])
async def getstatus_command(message: types.Message):
    await message.answer('/place - оформить заказ\n/orders - ваши заказы\n/cancel - отменить заказ\n/close - закрыть меню', reply_markup = keyboard_dronedb, allow_sending_without_reply=True)

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.reply(text=help_info)
    await message.delete()  
    
@dp.message_handler(state='*', commands=['close'])
async def close_menu_command(message: types.Message):
    msg = await message.reply(text='Открыть меню снова - /menu', reply_markup=types.ReplyKeyboardRemove())
    await message.delete()
    await asyncio.sleep(delay = 5)
    await msg.delete()

@dp.message_handler(commands=['place'])
async def palce_oreder(message: types.Message):
    await Form.adress.set()
    await bot.send_message(message.from_user.id, text='Введите ваш адрес:',  reply_markup=types.ReplyKeyboardRemove())

@dp.message_handler(commands=['show_drone_db'])
async def show_drone_db(message: types.Message):
    await message.reply(text= f'{data_base(1)}')
    await message.delete()

@dp.message_handler(commands=['reset_drone_db'])
async def reset_drone_db(message: types.Message):
    msg = await message.reply(text= f'{data_base(2)}')
    await message.delete()
    await asyncio.sleep(delay = 2)
    await msg.delete()

@dp.message_handler(state=Form.adress)
async def adress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['adress'] = message.text
    await bot.send_message(message.from_user.id, text='Введите время:')
    await Form.next()

@dp.message_handler(state=Form.time)
async def adress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    await bot.send_message(message.from_user.id, text = f"Оформлен заказ на адрес: {data['adress']}, по номеру телефона {data['phone']}", reply_markup = keyboard_dronedb)
    #   В этом месте будет вызываться функция добавляющая заказ в базу данных. 
    await state.finish()


#   Любые некомандные сообщение в случае, когда state не обособлен будет отпраляться напрямую в личные сообщения модератора для анализа
@dp.message_handler()
async def backcall(message: types.Message):
        if message.from_user.id == 802558859:
            await message.answer(text = 'Admin_Profile')
        else:
            await message.answer(text = message.text.capitalize())
            await bot.send_message(802558859, f"{message.from_user.full_name} \ {message.from_user.id}: {message.text}")

#   Функция отправки сообщений пользователю непосредственно через userID
@dp.message_handler(state='*', commands=['send'])
async def send(message: types.Message):
    try:
        service_data = message.text.split(" ")
        format_message = message.text.replace(service_data[0]+" ", "").replace(service_data[1]+" ", "")
        await bot.send_message(service_data[1], f"{message.from_user.full_name} \ {message.from_user.id}: {format_message}")
    except:
        await message.answer(text = 'Ошибка отправки сообщения')

if __name__ == '__main__':
    executor.start_polling(dp)
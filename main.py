import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from app.keyboards import *
import app.database as database
from dotenv import load_dotenv
from app.albumHandler import AlbumMiddleware
from typing import List, Union

import os

storage = MemoryStorage()
load_dotenv()

# loading .env variables
GENERAL_GROUP_ID = os.getenv('GENERAL_GROUP_ID')
GROUP_ID = os.getenv('GROUP_ID')
ADMIN_ID = os.getenv('MAIN_ADMIN_ID')
WHATSAPP_NUMBER = os.getenv('WHATSAPP_NUMBER')
TELEGRAM_LINK_CONTACT = os.getenv('TELEGRAM_LINK_CONTACT')
SOCIAL_VK = os.getenv('SOCIAL_VK')
# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)


async def on_startup(_):
    await database.db_start()
    print('Bot is launched')


class NewOrder(StatesGroup):
    teleID = State()
    teleNick = State()
    gettingName = State()
    gettingNumber = State()
    gettingDescription = State()
    gettingPhoto = State()


class CallMe(StatesGroup):
    gettingNumber = State()
    teleName = State()
    teleID = State()
    teleNick = State()


class NewService(StatesGroup):
    gettingFIO = State()
    gettingName = State()
    gettingPhone = State()
    gettingAddress = State()
    gettingPhotoRoom = State()
    gettingPhotoBuilding = State()
    gettingPhotoEquipment = State()
    gettingDescription = State()


# def generate_clickable_number(number):
#     return f'<a href="tel:{number}">{number}</a>'


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await database.cmd_start_db(message.from_user.id, message.from_user.username)
    if message.from_user.id == int(ADMIN_ID):
        await message.answer(f'Здравствуйте, {message.from_user.first_name}! Вы авторизовались как администратор',
                             reply_markup=main_admin_keyboard)
    else:
        await message.answer(f'''Рады вам, {message.from_user.first_name}, в нашем автоматизированном пункте приёма-выдачи "PC_Donetsk service"!

❗Убедительно просим перед звонком всё же оставить заявку здесь, это поможет нам быстрее заняться ремонтом именно вашего оборудования!

Внимание, сейчас обслуживание клиентов производится по адресу:
👉 Россия, г. Москва, Пятницкое шоссе 18
     "ТК Митинский радиорынок" пав. 560 на 3 этаже''', reply_markup=main_keyboard)


@dp.message_handler(text='Ввести быстрый код 🔐🔢')
async def fastCode(message: types.Message):
    await message.answer('Введите быстрый код')


@dp.message_handler(text='Наши сервисные центры 🛠(Как добраться, контакты)')
async def serviceCentresAddresses(message: types.Message):
    await message.answer(f'''Сейчас обслуживание клиентов производится по адресу:
👉 Россия, г. Москва, Пятницкое шоссе 18
     "ТК Митинский радиорынок" пав. 560 на 3 этаже
     
     
Контакты:
    WhatsApp номер: {WHATSAPP_NUMBER}
    Телеграмм: {TELEGRAM_LINK_CONTACT}''')


@dp.message_handler(text='Не могу разобраться, позвоните мне ☎️')
async def callMe(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tele_id'] = message.from_user.id
        data['tele_nick'] = message.from_user.username
    await CallMe.gettingNumber.set()
    await message.answer('Пожалуйста, напишите свой номер')


@dp.message_handler(state=CallMe.gettingNumber)
async def callMe(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
    await database.call_later_db(state)
    await message.answer("Спасибо за обращение! Скоро с вами свяжемся")
    await bot.send_message(GENERAL_GROUP_ID, f'''⚠️ Клиент просил связаться с ним!
        Ник: @{data['tele_nick']}
        Номер: {data['number']}
    ''', parse_mode='HTML')
    await bot.send_message(GROUP_ID, f'''⚠️ Клиент просил связаться с ним!

    Ник: @{data['tele_nick']}
    Номер: {data['number']}
    ''', parse_mode='HTML')
    await state.finish()


@dp.message_handler(text='Сдать в ремонт')
async def placeOrder(message: types.Message):
    await NewOrder.gettingName.set()
    await message.answer('Пожалуйста, напишите своё имя')


@dp.message_handler(state=NewOrder.gettingName)
async def getName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['tele_id'] = message.from_user.id
        data['tele_nick'] = message.from_user.username
        data['name'] = message.text
    await message.answer('Пожалуйста, напишите свой номер')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.gettingNumber)
async def getName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
    await message.answer('Пожалуйста, опишите проблему')
    await NewOrder.next()


@dp.message_handler(state=NewOrder.gettingDescription)
async def getName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['problem'] = message.text
    await message.answer(
        'Пожалуйста, пришлите фотографию, если не хотите добавить фото, нажмите на кнопку "Не хочу отправлять"',
        reply_markup=photo_keyboard)
    await NewOrder.next()


@dp.message_handler(lambda message: not message.photo, state=NewOrder.gettingPhoto)
async def add_item_photo_check(message: types.Message):
    await message.answer('Это не фотография!\n Если не хотите добавить фото, нажмите на кнопку "Не хочу отправлять"',
                         reply_markup=photo_keyboard)


@dp.callback_query_handler(lambda query: query.data == "dont_send", state=NewOrder.gettingPhoto)
async def handle_dont_send_query(query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = ""
    await bot.edit_message_reply_markup(
        chat_id=query.from_user.id,
        message_id=query.message.message_id,
        reply_markup=None
    )
    await database.add_order_db(state)
    await query.message.answer("Ваш заказ принят! Скоро с вами свяжемся")
    await bot.send_message(GENERAL_GROUP_ID, f"""⚠️ Новый заказ!\n
        Имя: {data['name']}\n
        Ник: @{data['tele_nick']}\n
        Номер: {data['number']}\n
        Описание: {data['problem']}
                """)
    await bot.send_message(GROUP_ID, f"""⚠️ Новый заказ!\n
    Имя: {data['name']}\n
    Ник: @{data['tele_nick']}\n
    Номер: {data['number']}\n
    Описание: {data['problem']}
            """)

    await state.finish()


@dp.message_handler(content_types=['photo'], state=NewOrder.gettingPhoto)
async def add_item_photo(message: types.Message, state: FSMContext, album: List[types.Message]):
    media_group = []
    async with state.proxy() as data:
        message_text = f"""⚠️❗Новый заказ от @pcservicebot\n
        {data['number']} {data['name']}\n
        {data['problem']}\n
        Россия > Москва\n
        Никнейм клиента в Telegram: @{data['tele_nick']}"""
        data['photo'] = ''
        for obj in album:
            if obj.photo:
                photo = obj.photo[-1]
                data['photo'] += photo.file_id
                media_group.append(types.InputMediaPhoto(photo.file_id))
                print(types.InputMediaPhoto(photo.file_id))
            else:
                return await message.answer("Invalid album format. Only photos are supported.")

    await message.answer_media_group(media_group)

    await database.add_order_db(state)
    await message.answer("Ваш заказ принят! Скоро с вами свяжемся")

    await bot.send_media_group(GENERAL_GROUP_ID, media=media_group)
    await bot.send_message(GENERAL_GROUP_ID, message_text)
    await bot.send_media_group(GROUP_ID, media=media_group)
    await bot.send_message(GROUP_ID, message_text)

    await state.finish()


@dp.message_handler(text='Наши соц. сети 📲')
async def ourSocialNetworks(message: types.Message):
    await message.answer(f'ВКонтакте: {SOCIAL_VK}\nInstagram: pc_donetsk_service')


@dp.message_handler(text='Франшиза💰')
async def franchise(message: types.Message):
    await message.answer(f'Крутяк! Напишите мне {TELEGRAM_LINK_CONTACT}')


@dp.message_handler(text='Админ-панель')
async def adminPanel(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        await message.answer('Вы вошли в Админ-панель', reply_markup=panel_admin_keyboard)
    else:
        await message.answer('К сожалению, я не знаю данную команду')


@dp.message_handler(text='Добавить новый Сервисный Центр')
async def addNewService(message: types.Message, state: FSMContext):
    if message.from_user.id == int(ADMIN_ID):
        async with state.proxy() as data:
            data['tele_id'] = message.from_user.id
            data['owner_tele_nick'] = message.from_user.username
        await message.answer('Пожалуйста, напишите свое ФИО')
        await NewService.gettingFIO.set()
    else:
        await message.answer('К сожалению, я не знаю данную команду')


@dp.message_handler(state=NewService.gettingFIO)
async def getNameNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['owner_name'] = message.text
    await message.answer('Пожалуйста, напишите название Вашего Сервиса')
    await NewService.next()


@dp.message_handler(state=NewService.gettingName)
async def getNameNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['service_name'] = message.text
    await message.answer('Пожалуйста, напишите номер телефона Вашего Сервиса/ Личный номер ')
    await NewService.next()


@dp.message_handler(state=NewService.gettingPhone)
async def getNameNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['number'] = message.text
    await message.answer('Пожалуйста, напишите адрес Вашего Сервиса ')
    await NewService.next()


@dp.message_handler(state=NewService.gettingAddress)
async def getNameNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    await message.answer('Пожалуйста, отправьте Фото Помещения')
    await NewService.next()


@dp.message_handler(content_types=['photo'], state=NewService.gettingPhotoRoom)
async def getPhotoNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo_room'] = message.photo[0].file_id
    await message.answer('Пожалуйста, отправьте Фото Здания')
    await NewService.next()


@dp.message_handler(lambda message: not message.photo, state=NewService.gettingPhotoRoom)
async def getPhotoNewService(message: types.Message):
    await message.answer('Пожалуйста, отправьте Фото Помещения, это обязательный пункт!')


@dp.message_handler(content_types=['photo'], state=NewService.gettingPhotoBuilding)
async def getPhotoNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo_building'] = message.photo[0].file_id
    await message.answer('Пожалуйста, отправьте Фото Оборудования')
    await NewService.next()


@dp.message_handler(lambda message: not message.photo, state=NewService.gettingPhotoBuilding)
async def getPhotoNewService(message: types.Message):
    await message.answer('Пожалуйста, отправьте Фото Здания, это обязательный пункт!')


@dp.message_handler(content_types=['photo'], state=NewService.gettingPhotoEquipment)
async def getPhotoNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo_equipment'] = message.photo[0].file_id
    await message.answer('Пожалуйста, отправьте Описание Сервиса (какие работы выполняете и тд)')
    await NewService.next()


@dp.message_handler(lambda message: not message.photo, state=NewService.gettingPhotoEquipment)
async def getPhotoNewService(message: types.Message):
    await message.answer('Пожалуйста, отправьте Фото Оборудования, это обязательный пункт!')


@dp.message_handler(state=NewService.gettingDescription)
async def getNameNewService(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
    await database.add_new_service(state)
    message_text = f"""⚠️ Новый Сервис для сотрудничества!\n
    ФИО владельца: {data['owner_name']}\n
    Ник: @{data['owner_tele_nick']}\n
    Номер: {data['number']}\n
    Название Сервиса: {data['service_name']}\n
    Адрес: {data['address']}\n
    Описание: {data['description']}"""
    media_group = []
    media_group.append(types.InputMediaPhoto(data['photo_room'], caption=message_text))
    media_group.append(types.InputMediaPhoto(data['photo_building']))
    media_group.append(types.InputMediaPhoto(data['photo_equipment']))
    await bot.send_media_group(GENERAL_GROUP_ID, media=media_group)
    await bot.send_media_group(GROUP_ID, media=media_group)
    await message.answer('Благодарим за Ваше сотрудничество! Надеемся, что оно будет продуктивным 😎')
    await state.finish()


@dp.message_handler(text='Выйти из админ-панели')
async def adminPanel(message: types.Message):
    if message.from_user.id == int(ADMIN_ID):
        await message.answer('Вы вышли из Админ-панели', reply_markup=main_admin_keyboard)
    else:
        await message.answer('К сожалению, я не знаю данную команду')


@dp.message_handler()
async def unknownAnswer(message: types.Message):
    await message.reply("К сожалению, я не знаю данную команду")


if __name__ == '__main__':
    dp.middleware.setup(AlbumMiddleware())
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)

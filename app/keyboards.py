from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add('Ввести быстрый код 🔐🔢')
main_keyboard.add('Сдать в ремонт')
main_keyboard.add('Наши сервисные центры 🛠(Как добраться, контакты)', 'Не могу разобраться, позвоните мне ☎️')
main_keyboard.add('Наши соц. сети 📲', 'Франшиза💰')

main_admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_admin_keyboard.add('Ввести быстрый код 🔐🔢')
main_admin_keyboard.add('Сдать в ремонт')
main_admin_keyboard.add('Наши сервисные центры 🛠(Как добраться, контакты)', 'Не могу разобраться, позвоните мне ☎️')
main_admin_keyboard.add('Наши соц. сети 📲', 'Франшиза💰', 'Админ-панель')

panel_admin_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
panel_admin_keyboard.add('Добавить новый Сервисный Центр')
panel_admin_keyboard.add('Выйти из админ-панели')

photo_keyboard = InlineKeyboardMarkup()
button = InlineKeyboardButton("Не хочу отправлять", callback_data="dont_send")
photo_keyboard.add(button)

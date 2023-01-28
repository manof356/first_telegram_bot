from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
import vigenere_cipher

bot = Bot(TOKEN)
dp = Dispatcher(bot)

HELP="""
/help - список команд бота
/start - начать
/use_vigenere_cipher - использовать шифр Виженера
/description - описание способностей бота"""
DESCRIPTION="""
Данный бот способен зашифровать и расшифровать
фразу, используя ключ.
Подробнее про шифр Виженера можете почитать здесь:
https://ru.wikipedia.org/wiki/%D0%A8%D0%B8%D1%84%D1%80_%D0%92%D0%B8%D0%B6%D0%B5%D0%BD%D0%B5%D1%80%D0%B0"""

@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,text=HELP)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,text=f"Эй, {message.from_user.first_name}, привет")

@dp.message_handler(commands=["description"])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id,text=DESCRIPTION)


executor.start_polling(dp)

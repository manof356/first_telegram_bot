from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from vigenere_cipher import encrypt_phrase

bot = Bot(TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

HELP = """
/help - список команд бота
/start - начать
/use_vigenere_cipher - использовать шифр Виженера
/description - описание способностей бота"""
DESCRIPTION = """
Данный бот способен зашифровать и расшифровать
фразу, используя ключ.
Подробнее про шифр Виженера можете почитать здесь:
https://ru.wikipedia.org/wiki/%D0%A8%D0%B8%D1%84%D1%80_%D0%92%D0%B8%D0%B6%D0%B5%D0%BD%D0%B5%D1%80%D0%B0"""


kb = ReplyKeyboardMarkup(resize_keyboard=True)  # create a keyboard
kb.add(KeyboardButton("/help"))  # add a new button to keyboard
kb.add(KeyboardButton("/description"))  # add a new button to keyboard
kb.add(KeyboardButton("/use_vigenere_cipher"))  # add a new button to keyboard

kb_lang = ReplyKeyboardMarkup(resize_keyboard=True)  # create a language keyboard
kb_lang.add(KeyboardButton("/Русский"))
kb_lang.add(KeyboardButton("/English"))

kb_en_dec = ReplyKeyboardMarkup(resize_keyboard=True)  # create a language keyboard
kb_en_dec.add(KeyboardButton("/Зашифровать"))
kb_en_dec.add(KeyboardButton("/Расшифровать"))


class CryptText(StatesGroup):
    choosing_command = State()
    choosing_language = State()
    choosing_en_decrypt = State()
    entering_phrase = State()
    entering_key = State()


@dp.message_handler(commands=["help"])
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=HELP)
    await message.delete()


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"Эй, {message.from_user.first_name}, привет",
                           reply_markup=kb)
    await message.delete()
    await CryptText.choosing_command.set()


@dp.message_handler(commands=["description"])
async def description_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=DESCRIPTION)
    await message.delete()


@dp.message_handler(commands=["use_vigenere_cipher"], state=CryptText.choosing_command)
async def vigenere_start(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="На каком языке будет фраза?",
                           reply_markup=kb_lang)
    await message.delete()
    await CryptText.next()


@dp.message_handler(commands=['Русский', "English"], state=CryptText.choosing_language)
async def vigenere_1(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['lang'] = message.text
    await CryptText.next()
    await bot.send_message(chat_id=message.chat.id, text="Зашифровать или расшифровать?",
                           reply_markup=kb_en_dec)
    await message.delete()


@dp.message_handler(commands=['Зашифровать', "Расшифровать"], state=CryptText.choosing_en_decrypt)
async def vigenere_2(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['en_or_de'] = message.text
    await CryptText.next()
    await bot.send_message(chat_id=message.chat.id, text="Введите фразу")
    await message.delete()


@dp.message_handler(state=CryptText.entering_phrase)
async def vigenere_3(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['phrase'] = message.text
    await CryptText.next()
    await bot.send_message(chat_id=message.chat.id, text="Введите ключ")

@dp.message_handler(state=CryptText.entering_key)
async def vigenere_4(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['key'] = message.text
        lang = data['lang'] == '/Русский'  # Pass the language to the cypher
        en_dec = data['en_or_de'] == '/Зашифровать'  # Pass the encryption ot decryption option to the cypher
        res = encrypt_phrase(data['phrase'], data['key'], lang, en_dec)
    await bot.send_message(chat_id=message.chat.id, text='Конечный результат:')
    await bot.send_message(chat_id=message.chat.id, text=res)
    await state.finish()

    await bot.send_message(chat_id=message.chat.id, text=f"Эй, {message.from_user.first_name}, привет",
                           reply_markup=kb)
    await CryptText.choosing_command.set()

executor.start_polling(dp)

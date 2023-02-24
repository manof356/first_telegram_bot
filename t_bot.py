from aiogram import Bot, Dispatcher, executor, types
from config import TOKEN
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ContentType
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from vigenere_cipher import encrypt_phrase, is_letters, is_rus_eng_letters
from aiogram.dispatcher.filters import Text

bot = Bot(TOKEN)  # создаем бота с данным нам токеном от BotFather
storage = MemoryStorage()  # создание ячейки памяти для хранения данных шифрования
dp = Dispatcher(bot, storage=storage)  # создание диспетчера
lang_dict = {"English": [False, "English"],
             "Русский": [True, "Русском"]}  # костыльный словарь для работы функции is_rus_eng_letters

HELP = """
/start - начать работу бота
Помощь - список команд бота
Использовать шифр - использовать шифр Виженера
Описание бота - описание способностей бота"""
DESCRIPTION = """
Данный бот способен зашифровать и расшифровать
фразу, используя ключ.
Подробнее про шифр Виженера можете почитать здесь:
https://ru.wikipedia.org/wiki/%D0%A8%D0%B8%D1%84%D1%80_%D0%92%D0%B8%D0%B6%D0%B5%D0%BD%D0%B5%D1%80%D0%B0"""

kb = ReplyKeyboardMarkup(resize_keyboard=True)  # create a start keyboard
kb.add(KeyboardButton("Помощь"))  # add a new button to keyboard
kb.add(KeyboardButton("Описание бота"))  # add a new button to keyboard
kb.add(KeyboardButton("Использовать шифр"))  # add a new button to keyboard

kb_lang = ReplyKeyboardMarkup(resize_keyboard=True)  # create a language keyboard
kb_lang.add(KeyboardButton("Русский"))  # add a new button to keyboard
kb_lang.add(KeyboardButton("English"))  # add a new button to keyboard
kb_lang.add(KeyboardButton("Отмена"))  # add a new button to keyboard

kb_en_dec = ReplyKeyboardMarkup(resize_keyboard=True)  # create an encrypt keyboard
kb_en_dec.add(KeyboardButton("Зашифровать"))  # add a new button to keyboard
kb_en_dec.add(KeyboardButton("Расшифровать"))  # add a new button to keyboard
kb_en_dec.add(KeyboardButton("Отмена"))  # add a new button to keyboard


# Создание нескольких машинных состояний. Aiogram переключает эти состояния, когда получает
# ответ на свой запрос. Также по этим состояниям можно делать фильтрацию в декораторе
class CryptText(StatesGroup):
    # start_state = State()  # create a new state
    choosing_command = State()  # create a new state
    choosing_language = State()  # create a new state
    choosing_en_decrypt = State()  # create a new state
    entering_phrase = State()  # create a new state
    entering_key = State()  # create a new state


# Функция вызова справки по команде "/help"
@dp.message_handler(Text(equals="Помощь"), state=CryptText.choosing_command)
# фильтр декоратора нацелен на поиск команды "help" а также работает из любого машинного состояния
async def help_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=HELP)
    await message.delete()  # команда удаляется перед ответом бота


# Функция вызова главной клавиатуры работы с ботом по команде "/start"
# а так же бот нас приветствует
@dp.message_handler(commands=["start"], state="*")
async def start_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"Эй, {message.from_user.first_name}, привет",
                           reply_markup=kb)
    await message.delete()
    await CryptText.choosing_command.set()  # устанавливается первое состояние


# Функция показа описания шифра виженера. Тупо ссылка на Вики.
@dp.message_handler(Text(equals="Описание бота"), state=CryptText.choosing_command)
async def description_command(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=DESCRIPTION)
    await message.delete()


# Функция начала работы с шифром
@dp.message_handler(Text(equals="Использовать шифр"), state=CryptText.choosing_command)
# залетаем сюда когда используется команда "use_vigenere_cipher" и при состоянии "choosing_command"
async def vigenere_start(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="На каком языке будет фраза?",
                           reply_markup=kb_lang)  # вызывается клавиатура выбора языка
    await message.delete()  # наше сообщение удаляется
    await CryptText.next()  # машинное состояние меняется на следующее по списку


# Функция кнопки "отмена"
@dp.message_handler(Text(equals="Отмена"), state=[CryptText.choosing_language, CryptText.choosing_en_decrypt])
# Залетаем сюда при нажатии "Отмена" и при состояниях из списка выше
async def cancel(message: types.Message, state=FSMContext):
    await message.delete()  # удаляем сообщание
    await state.finish()  # сбрасываем машинное состояение
    await bot.send_message(chat_id=message.chat.id, text="Бот готов", reply_markup=kb)  # отправляем сообщение
    await CryptText.choosing_command.set()  # ставим первое состояние


# Функция записывает в data выбранный язык, меняет клавиатуру и машинное состояние
@dp.message_handler(Text(equals=['Русский', "English"]), state=CryptText.choosing_language)
# Залетаем сюда при языковых командах и при состоянии "choosing_language"
async def vigenere_1(message: types.Message, state=FSMContext):
    global data  # делаем переменную data глобальной, чтобы можно было её пользоваться ниже
    async with state.proxy() as data:  # ??? что то типа открытия data как словаря
        data['lang'] = message.text  # и запись значения языка по ключу "lang"
    await CryptText.next()  # ставим следующее по списку состояние
    await bot.send_message(chat_id=message.chat.id, text="Зашифровать или расшифровать?",
                           reply_markup=kb_en_dec)  # показываем клавиатуру выбора зашифр/расшифр
    await message.delete()  # удаляем сообщение


# Функция записывает в data выбранное действие: зашифровать или расшифровать,
# меняет машинное состояние и просит ввести фразу
@dp.message_handler(Text(equals=['Зашифровать', "Расшифровать"]), state=CryptText.choosing_en_decrypt)
# Залетаем сюда при командах в списке и при машинном состоянии "choosing_en_decrypt"
async def vigenere_2(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['en_or_de'] = message.text  # записываем в словарь data значение зашифр/расшифр
    await CryptText.next()  # переключаем машинное состояние на следующее
    await bot.send_message(chat_id=message.chat.id, text="Введите фразу",
                           reply_markup=ReplyKeyboardRemove())  # Убираем всякую клавиатуру
    await message.delete()


# функция если ввел во фразу все что угодно без единой буквы
@dp.message_handler(lambda message: not is_letters(message.text), content_types=ContentType.TEXT,
                    state=CryptText.entering_phrase)
# Залетаем сюда, когда находимся в состоянии "entering_phrase", так же когда тип введенной ответной
# информации является текстом, а лямбда функция отбирает только тот текст, который не содержит
# ни единой буквы любого алфавита
async def is_phrase_letters(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Фраза должна содержать хотя бы одну букву")


# функция если ввел во фразу все буквы не из выбранного языка
@dp.message_handler(lambda message: not is_rus_eng_letters(message.text, lang_dict[data['lang']][0]),
                    content_types=ContentType.TEXT,
                    state=CryptText.entering_phrase)
# Залетаем сюда, когда находимся в состоянии "entering_phrase", так же когда тип введенной ответной
# информации является текстом, а лямбда функция отбирает только тот текст, который содержит все буквы
# одного алфавита, а выбран другой алфавит
async def is_phrase_right_alph(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"Вы выбрали {data['lang']}, "
                                                         f"а ввели фразу не на {lang_dict[data['lang']][1]}!")


# отработка функции в обычном режиме
@dp.message_handler(content_types=ContentType.TEXT, state=CryptText.entering_phrase)
# Обработки выше написаны выше и сработают первее, а если в тексте нет ошибок, то он залетит в эту функцию
# Она отбирает тип отправленных данных - текст и состояние "entering_phrase"
async def vigenere_3(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['phrase'] = message.text  # записываем в data фразу
    await CryptText.next()  # сменяем состояние
    await bot.send_message(chat_id=message.chat.id, text="Введите ключ")


# функция если отправил не текст (картинку, голосовое или что-то иное)
@dp.message_handler(content_types=ContentType.ANY, state=CryptText.entering_phrase)
# В эту функцию залетаем если было отправлено все что угодно, кроме текста.
# Она написана ниже, потому что если написать её выше, то сюда будет залетать и обычный текст.
# А так текст перехватывается выше, то сюда мы точно не залетим.
async def is_phrase_text(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Фраза должна быть текстом!")


# функция если ввел в ключ все что угодно без единой буквы
@dp.message_handler(lambda message: not is_letters(message.text), content_types=ContentType.TEXT,
                    state=CryptText.entering_key)
async def is_key_letters(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Ключ должен содержать хотя бы одну букву")


# функция если ввел в ключ все буквы не из выбранного языка
@dp.message_handler(lambda message: not is_rus_eng_letters(message.text, lang_dict[data['lang']][0]),
                    content_types=ContentType.TEXT,
                    state=CryptText.entering_key)
async def is_key_right_alph(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"Вы выбрали {data['lang']}, "
                                                         f"а ввели ключ не на {lang_dict[data['lang']][1]}!")


@dp.message_handler(content_types=ContentType.TEXT, state=CryptText.entering_key)
async def vigenere_5(message: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['key'] = message.text
        lang = data['lang'] == 'Русский'  # Pass the language to the cypher
        en_dec = data['en_or_de'] == 'Зашифровать'  # Pass the encryption ot decryption option to the cypher
        res = encrypt_phrase(data['phrase'], data['key'], lang, en_dec)
    await bot.send_message(chat_id=message.chat.id, text='Конечный результат:')
    await bot.send_message(chat_id=message.chat.id, text=res)
    await state.finish()
    await bot.send_message(chat_id=message.chat.id, text="Бот готов", reply_markup=kb)
    await CryptText.choosing_command.set()


# функция если отправил не текст (картинку, голосовое или что-то иное)
@dp.message_handler(content_types=ContentType.ANY, state=CryptText.entering_key)
async def is_key_text(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text="Ключ должен быть текстом!")


executor.start_polling(dp)

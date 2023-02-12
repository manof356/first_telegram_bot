import string

RUS_low_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

RUS_upp_alphabet = RUS_low_alphabet.upper()

ENG_low_alphabet = string.ascii_lowercase
ENG_upp_alphabet = string.ascii_uppercase

RUS_ENG_low_alph = [ENG_low_alphabet, RUS_low_alphabet]
RUS_ENG_upp_alph = [ENG_upp_alphabet, RUS_upp_alphabet]

def is_letters(txt: str):
    for i in txt:
        if i.isalpha():
            return True
    return False


def is_rus_eng_letters(txt: str, alph: bool):
    letters = [ENG_low_alphabet + ENG_upp_alphabet, RUS_low_alphabet + RUS_upp_alphabet]
    for i in txt:
        if i in letters[alph]:
            return False
    return True

def result_alph(lang: bool):
    global low_alph, upp_alph
    low_alph = RUS_ENG_low_alph[lang]
    upp_alph = RUS_ENG_upp_alph[lang]
    return low_alph + upp_alph


def del_all_punctuation(phrase: str, language: bool):
    """
    deletes all punctuations in phrase
    :param phrase: phrase to encrypt or decrypt
    :return: phase without any punctuations
    """
    res_alph = result_alph(language)
    phrase_only_letters = ""
    for i in phrase:
        if i in res_alph:
            phrase_only_letters += i
    return phrase_only_letters


def repeat_key(key: str, phrase: str, language: bool):
    """
    loops key as many times as length phrase
    :param key: encryption key
    :param phrase: phrase to encrypt or decrypt. it is needed to count its length
    :return: looped key
    """
    new_phrase = del_all_punctuation(phrase, language)
    new_key = del_all_punctuation(key, language)
    res = del_all_punctuation(key.lower(), language)
    res *= (len(new_phrase) // len(new_key) + 1)
    return res[:len(new_phrase)]


def en_or_de_crypt_it(phrase: str, key: str, language: bool, en_or_de: bool = True):
    """
    encrypts or decrypts phase with key without any punctuations
    :param phrase: phrase to encrypt or decrypt
    :param key: encryption key
    :param en_or_de: encrypt = True, decrypt = False
    :return: encrypted/decrypted phrase without any punctuations
    """
    new_phrase = del_all_punctuation(phrase, language)
    res_key = repeat_key(key, phrase, language)
    res_alph = result_alph(language)
    result = ""
    for i, j in zip(new_phrase, res_key):
        if i in res_alph:
            if i.islower():
                res_index = (low_alph.index(i) + [-1, 1][en_or_de] * low_alph.index(j)) % len(low_alph)
                result += low_alph[res_index]
            else:
                res_index = (upp_alph.index(i) + [-1, 1][en_or_de] * low_alph.index(j)) % len(upp_alph)
                result += upp_alph[res_index]
        else:
            result += i
    return result


def encrypt_phrase(phrase: str, key: str, language: bool, en_or_de: bool = True):
    """
    encrypts or decrypts phase with key and with punctuation according to entry phrase
    :param phrase: phrase to encrypt or decrypt
    :param key: encryption key
    :return: phrase with punctuation according to entry phrase
    """
    res_phrase_only_letters = en_or_de_crypt_it(phrase, key, language, en_or_de)
    res_alph = result_alph(language)
    result = ""
    j = 0
    for i in phrase:
        if i in res_alph:
            result += res_phrase_only_letters[j]
            j += 1
        else:
            result += i
    return result

# print(encrypt_phrase("Привет","кей",True,True))
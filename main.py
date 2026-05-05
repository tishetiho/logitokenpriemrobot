import asyncio
import random
import string
import re
import aiohttp
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Файл для хранения уже сданных токенов (защита от дублей)
DB_FILE = "used_tokens.txt"

# Твой обновленный список названий
NAMES = ["Вектор", "Виктор", "Пробив", "Пробить", "Докс", "Шоколадный глаз", "Глаз бога", "Пробивала", "Шерлок", "Духлес"]

# Функция генерации рандомного юзернейма
def gen_username():
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for _ in range(8))
    return f"{random_str}_bot"

# Регулярка для проверки формата токена
TOKEN_PATTERN = re.compile(r'^\d{8,10}:[a-zA-Z0-9_-]{35,45}$')

# Клавиатура (Текст на кнопке должен совпадать с обработчиком ниже)
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Подобрать задание ⚙️")]],
    resize_keyboard=True
)

# Проверка токена на валидность через API Telegram
async def check_token_validity(token: str):
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("result")
                return None
        except:
            return None

# Проверка на дубликаты
def is_duplicate(token: str):
    if not os.path.exists(DB_FILE):
        return False
    with open(DB_FILE, "r") as f:
        used_tokens = f.read().splitlines()
    return token in used_tokens

# Сохранение токена
def save_token(token: str):
    with open(DB_FILE, "a") as f:
        f.write(token + "\n")

@dp.message(Command("start"))
async def cmd_start(message
                    

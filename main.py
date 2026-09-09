import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
from openai import OpenAI
import os

# --- TOKENLAR ---
TOKEN = "8793117472:AAlhTjcP0dtatu7XD4SIatTdT RJiq494b1_nE"  # Telegram bot tokeningiz
GROQ_API_KEY = "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"      # Groq'dan olgan gsk_... bilan boshlanuvchi kalitingiz

# Groq mijozi (OpenAI formatida ishlaydi)
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


class AcademyState(StatesGroup):
    waiting_for_code_request = State()


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 0 dan Botsozlik Darslari", callback_data="lessons"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🛠 Tayyor Kodlar Bazasi", callback_data="snippets"
                ),
                InlineKeyboardButton(
                    text="🧩 Bot Konstruktorlari", callback_data="constructor"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🤖 AI Kod Generator va Yordamchi", callback_data="ai_help"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🌐 GitHub va 24/7 Server Qo'llanmasi",
                    callback_data="github_info",
                )
            ],
        ]
    )


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_name = message.from_user.first_name
    text = (
        f"Salom, **{user_name}**! 🌟\n\n"
        "Bu bot — noldan boshlab milliardlab funksiyali Telegram botlar, "
        "konstruktorlar va sun'iy intellekt tizimlarini yaratishni "
        "o'rgatadigan **Nurly Al** akademiyasi!\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")


@dp.callback_query(F.data == "ai_help")
async def ai_help_handler(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "🤖 **Nurly Al — AI Kod Markazi**\n\n"
        "Qanday bot yoki funksiya kodi kerakligini yozib yuboring "
        "(masalan: *'Majburiy obuna boti kodi'* yoki *'Referral tizim kodi'*):\n\n"
        "✍️ *Marhamat, savolingizni yuboring:*"
    )
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Ortga", callback_data="back_home")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
    await state.set_state(AcademyState.waiting_for_code_request)
    await callback.answer()


@dp.message(AcademyState.waiting_for_code_request)
async def process_user_query(message: types.Message, state: FSMContext):
    user_text = message.text
  
    wait_msg = await message.answer(
        "⏳ *Nurly Al siz uchun maxsus kod yozmoqda, iltimos kuting...*",
        parse_mode="Markdown"
    )
  
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # Groq'dagi eng kuchli va tez model
            messages=[
                {
                    "role": "system",
                    "content": "Sen professional Telegram botsozlik va Python ustozi-sun'iy intellektmisan. Foydalanuvchining savoliga aiogram 3.x yordamida ishlaydigan mukammal kod va tushuntirish yozib ber."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ]
        )
        generated_code = response.choices[0].message.content
    except Exception as e:
        generated_code = f"⚠️ Xatolik yuz berdi: {e}\nIltimos, API kalitingizni tekshiring."
  
    await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)
    
    if len(generated_code) > 4000:
        for x in range(0, len(generated_code), 4000):
            await message.answer(generated_code[x:x+4000], parse_mode="Markdown")
    else:
        await message.answer(generated_code, parse_mode="Markdown")
        
    await message.answer(
        "🏠 Boshqa savolingiz bormi?", 
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="🏠 Asosiy Menyu", callback_data="back_home")]]
        )
    )
    await state.clear()


@dp.callback_query(F.data == "github_info")
async def github_info_handler(callback: types.CallbackQuery):
    text = (
        "🌐 **GitHub va Render 24/7 Sozlamasi**\n\n"
        "1. `main.py` fayliga ushbu kodni joylaysiz.\n"
        "2. Render'ga Web Service sifatida ulab, bepul ishlatasiz!"
    )
    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Ortga", callback_data="back_home")]
        ]
    )
    await callback.message.edit_text(text, reply_markup=back_kb, parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data == "back_home")
async def process_back(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Asosiy menyu:", reply_markup=main_menu(), parse_mode="Markdown"
    )
    await callback.answer()


# --- RENDER PORTINI TA'MINLASH UCHUN WEB SERVER ---
async def handle(request):
    return web.Response(text="Bot is online and working!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()


async def main():
    await web_server()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

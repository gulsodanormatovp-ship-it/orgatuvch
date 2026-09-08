import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import google.generativeai as genai

# --- TOKENLARNI SHU YERGA YOZASIZ ---
TOKEN = "8793117472:AAGpcmb_OQ92ob_dDMYx-HLZVszXkv52p3M"          # BotFather'dan olingan Telegram bot tokeni
GEMINI_API_KEY = "sk-6488598bfbe24fcdb2ecb0f7bc372360"  # Google AI Studio'dan olingan Gemini API kaliti

# Gemini'ni sozlash
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

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
        "o'rgatadigan eng zo'r milliy akademiya!\n\n"
        "Kerakli bo'limni tanlang:"
    )
    await message.answer(text, reply_markup=main_menu(), parse_mode="Markdown")


@dp.callback_query(F.data == "ai_help")
async def ai_help_handler(callback: types.CallbackQuery, state: FSMContext):
    text = (
        "🤖 **AI Kod Markazi**\n\n"
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
        "⏳ *AI siz uchun maxsus kod yozmoqda, iltimos kuting...*",
        parse_mode="Markdown"
    )
  
    try:
        # Gemini orqali haqiqiy javob va kod generatsiya qilish
        prompt = (
            "Sen professional Telegram botsozlik va dasturlash ustozi-sun'iy intellektmisan. "
            f"Foydalanuvchining so'rovi: '{user_text}'. "
            "Shu so'rov bo'yicha Python (aiogram 3.x) yordamida ishlaydigan mukammal kod va uni tushuntiruvchi qo'llanma yozib ber."
        )
        response = model.generate_content(prompt)
        generated_code = response.text
    except Exception as e:
        generated_code = f"⚠️ Xatolik yuz berdi: {e}\nIltimos, API kalitingizni tekshiring."
  
    await bot.delete_message(chat_id=message.chat.id, message_id=wait_msg.message_id)
    
    # Xabar uzunligi Telegram limitidan (4000 ta belgi) oshib ketsa, bo'lib yuborish yoki to'g'ridan-to'g'ri yuborish
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
        "🌐 **GitHub'ga Joylash va 24/7 Ishlatish tartibi**\n\n"
        "1. GitHub'da yangi repozitoriy ochasiz (masalan: `bot-academy`).\n"
        "2. `main.py` fayliga mana shu kodni joylaysiz.\n"
        "3. Yoniga `requirements.txt` faylini ochib quyidagilarni yozasiz:\n"
        "   `aiogram>=3.0.0`\n"
        "   `google-generativeai`\n"
        "4. Render yoki boshqa serverga ulangach, botingiz 24 soat uzluksiz ishlaydi!"
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


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

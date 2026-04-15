import logging
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (LabeledPrice, PreCheckoutQuery, ContentType, 
                           InlineKeyboardButton, InlineKeyboardMarkup, 
                           ReplyKeyboardMarkup, KeyboardButton)

# --- КОНФИГУРАЦИЯ ---
BOT_TOKEN = "ВАШ_ТОКЕН_БОТА"
PAYMENT_TOKEN = "ВАШ_ПЛАТЕЖНЫЙ_ТОКЕН"
SUPPORT_USER = "vash_nik_v_tg"
VPN_LINK = "https://raw.githubusercontent.com/ileo-g/NexaVPN-Base/main/online.txt"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ВЕБ-СЕРВЕР ДЛЯ HUGGING FACE ---
async def handle(request):
    return web.Response(text="Бот NexaVPN запущен и работает!")

async def start_webserver():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    # Порт 7860 — стандарт для Hugging Face Spaces
    site = web.TCPSite(runner, "0.0.0.0", 7860)
    await site.start()

# --- КЛАВИАТУРЫ ---
def main_menu():
    kb = [
        [KeyboardButton(text="⚡ Купить подписку")],
        [KeyboardButton(text="📖 Инструкция (Happ)"), KeyboardButton(text="🆘 Поддержка")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def pay_inline():
    btn = [[InlineKeyboardButton(text="Оплатить 300₽", callback_data="start_pay")]]
    return InlineKeyboardMarkup(inline_keyboard=btn)

# --- ХЕНДЛЕРЫ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("👋 Добро пожаловать в NexaVPN! Используйте меню ниже:", reply_markup=main_menu())

@dp.message(F.text == "🆘 Поддержка")
async def support_info(message: types.Message):
    await message.answer(f"По вопросам оплаты пишите: @{SUPPORT_USER}")

@dp.message(F.text == "📖 Инструкция (Happ)")
async def manual_happ(message: types.Message):
    text = (
        "🍏 **Инструкция для Happ:**\n\n"
        "1. Скопируйте ссылку после оплаты.\n"
        "2. В приложении Happ нажмите **«+»**.\n"
        "3. Выберите **«Add from Clipboard»**.\n"
        "4. Нажмите на кнопку подключения."
    )
    await message.answer(text, parse_mode="Markdown")

@dp.message(F.text == "⚡ Купить подписку")
async def buy_process(message: types.Message):
    await message.answer("Стоимость: 300 руб/мес.", reply_markup=pay_inline())

@dp.callback_query(F.data == "start_pay")
async def send_invoice(callback: types.CallbackQuery):
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="NexaVPN: 30 дней",
        description="Подписка для Happ Utility",
        payload="vpn_pay",
        provider_token=PAYMENT_TOKEN,
        currency="RUB",
        prices=[LabeledPrice(label="Подписка", amount=30000)]
    )

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def success_payment(message: types.Message):
    await message.answer(f"✅ Оплата принята! Ваша ссылка:\n`{VPN_LINK}`", parse_mode="Markdown")

# --- ЗАПУСК ---
async def main():
    # Запускаем веб-сервер, чтобы HF не "усыплял" бота
    asyncio.create_task(start_webserver())
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

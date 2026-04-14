import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Токен из Railway
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# --- Клавиатуры ---

def main_kb():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👤 Профиль", callback_data="profile"),
        InlineKeyboardButton("💎 Купить подписку", callback_data="tariffs"), # Главная кнопка здесь
        InlineKeyboardButton("🆘 Поддержка", url="https://t.me/твой_ник"),
        InlineKeyboardButton("📢 Канал", url="https://t.me/твой_канал")
    )
    return kb

def tariffs_kb():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📱 1 устройство — 159₽", callback_data="pay_159"),
        InlineKeyboardButton("📱 2 устройства — 209₽", callback_data="pay_209"),
        InlineKeyboardButton("📱 3 устройства — 289₽", callback_data="pay_289"),
        InlineKeyboardButton("⬅️ Назад в меню", callback_data="start_back")
    )
    return kb

def pay_kb(amount, pay_url):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton(f"💳 Оплатить {amount}₽", url=pay_url),
        InlineKeyboardButton("✅ Я оплатил", callback_data="check_pay"),
        InlineKeyboardButton("⬅️ Назад к тарифам", callback_data="tariffs")
    )
    return kb

# --- Обработчики ---

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    text = (
        "👋 **Добро пожаловать в NexaVPN!**\n\n"
        "Здесь ты можешь приобрести стабильный VPN для любых устройств.\n"
        "Выбери нужное действие ниже:"
    )
    await message.answer(text, reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'profile')
async def profile(call: types.CallbackQuery):
    user_id = call.from_user.id
    text = (
        f"👤 **Ваш профиль:**\n\n"
        f"├ ID: `{user_id}`\n"
        f"├ Статус: Не активна\n"
        f"└ Баланс: 0 ₽\n\n"
        f"Чтобы пользоваться VPN, нажми кнопку ниже 👇"
    )
    await call.message.edit_text(text, reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'tariffs')
async def show_tariffs(call: types.CallbackQuery):
    await call.message.edit_text("💎 **Выберите подходящий тариф:**", reply_markup=tariffs_kb(), parse_mode="Markdown")

# Логика перехода к оплате
@dp.callback_query_handler(lambda c: c.data.startswith('pay_'))
async def go_to_pay(call: types.CallbackQuery):
    amount = call.data.split('_')[1]
    
    # СЮДА ВСТАВЬ СВОЮ ССЫЛКУ (на оплату, на карту или на бота для чеков)
    pay_url = f"https://t.me/твой_ник" # Пока просто ссылка на тебя для ручной оплаты
    
    text = (
        f"📦 **Оформление подписки**\n\n"
        f"Сумма к оплате: **{amount}₽**\n"
        "После нажатия на кнопку «Оплатить», вы будете перенаправлены на страницу оплаты.\n\n"
        "⚠️ После перевода нажмите кнопку «Я оплатил»."
    )
    await call.message.edit_text(text, reply_markup=pay_kb(amount, pay_url), parse_mode="Markdown")

@dp.callback_query_handler(lambda c: c.data == 'check_pay')
async def check_pay(call: types.CallbackQuery):
    await call.answer("⏳ Платеж проверяется модератором. Обычно это занимает 5-10 минут.", show_alert=True)

@dp.callback_query_handler(lambda c: c.data == 'start_back')
async def back_home(call: types.CallbackQuery):
    await start(call.message)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

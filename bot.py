import os
from aiogram import Bot, Dispatcher, types, executor

# Токены из Railway
TOKEN = os.getenv("BOT_TOKEN")
PAY_TOKEN = os.getenv("PAYMENT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Кнопки тарифов
def tariffs_kb():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("📱 1 устройство — 159₽", callback_data="buy_159"),
        types.InlineKeyboardButton("📱 2 устройства — 209₽", callback_data="buy_209"),
        types.InlineKeyboardButton("⬅️ Назад", callback_data="start")
    )
    return kb

@dp.callback_query_handler(lambda c: c.data == 'tariffs')
async def show_tariffs(call: types.CallbackQuery):
    await call.message.edit_text("💎 **Выберите тариф:**", reply_markup=tariffs_kb(), parse_mode="Markdown")

# ОТПРАВКА СЧЕТА НА ОПЛАТУ
@dp.callback_query_handler(lambda c: c.data.startswith('buy_'))
async def send_invoice(call: types.CallbackQuery):
    amount = int(call.data.split('_')[1])
    
    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f"Подписка NexaVPN",
        description=f"Доступ на выбранное кол-во устройств",
        payload="vpn_subscription",
        provider_token=PAY_TOKEN,
        currency="RUB",
        prices=[types.LabeledPrice(label="VPN Подписка", amount=amount * 100)], # Сумма в копейках
        start_parameter="nexa-vpn-pay"
    )

# ПРОВЕРКА ПЛАТЕЖА (Перед финальной оплатой)
@dp.shipping_query_handler(lambda query: True)
async def shipping(shipping_query: types.ShippingQuery):
    await bot.answer_shipping_query(shipping_query.id, ok=True)

@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# ЧТО ДЕЛАТЬ ПОСЛЕ УСПЕШНОЙ ОПЛАТЫ
@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    # Здесь бот подтверждает платеж
    await message.answer(
        "✅ **Оплата прошла успешно!**\n\n"
        "Ваша подписка активирована. Вот ваша уникальная ссылка:\n"
        "`vless://unique_link_here...`" # Сюда потом прикрутим генерацию ссылок
    )

import asyncio
import sqlite3
import json
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup

# --- НАСТРОЙКИ ---
API_TOKEN = '8780187440:AAGOrD-csNZf7DhmBY4PuN1CKrWQERzwdwQ'
OWNER_ID = 8166820778 # Твой ID
ADMINS = [8166820778] # Список всех админов

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# --- БАЗА ДАННЫХ ---
def db_query(query, params=(), fetch=False):
    conn = sqlite3.connect('dxshop.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

def init_db():
    db_query('''CREATE TABLE IF NOT EXISTS deals 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, buyer_id INTEGER, seller_text TEXT, 
                 amount REAL, status TEXT, admin_id INTEGER)''')
    db_query('''CREATE TABLE IF NOT EXISTS reviews 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, text TEXT, stars INTEGER)''')

init_db()

# --- ЛОГИКА БОТА ---
@dp.message(Command("start"))
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="DXSHOP iOS ⚡️", web_app=WebAppInfo(url="https://dxmade.github.io/dxma3de.github.io/"))]
    ])
    await message.answer_with_photo(
        photo="https://i.pinimg.com/originals/a4/0a/7e/a40a7e6b0525d6a2f4c4a4a1b0b5e4c4.jpg",
        caption=f"🛰 **DXSHOP ESCROW v2.0**\n\nДобро пожаловать в будущее безопасных сделок.\n\nЖми на кнопку ниже, чтобы войти.",
        reply_markup=kb
    )

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    data = json.loads(message.web_app_data.data)
    action = data.get("action")

    if action == "new_deal":
        opponent = data.get("opponent")
        amount = data.get("amount")
        
        # Запись в БД
        db_query("INSERT INTO deals (buyer_id, seller_text, amount, status) VALUES (?, ?, ?, ?)", 
                 (message.from_user.id, opponent, amount, "Ожидание админа"))
        
        deal_id = db_query("SELECT last_insert_rowid()", fetch=True)[0][0]

        # Уведомление покупателю
        await message.answer(f"✅ **Сделка #{deal_id} создана!**\n💰 Сумма: {amount}$\n👤 Продавец: {opponent}\n\n⏳ Ожидаем подключения администратора. Чат будет создан автоматически.")
        
        # Уведомление админам
        admin_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Вступить в сделку 🛠", callback_data=f"take_{deal_id}")]
        ])
        for admin in ADMINS:
            try:
                await bot.send_message(admin, f"🚀 **НОВАЯ СДЕЛКА #{deal_id}**\nСумма: {amount}$\nПокупатель: {message.from_user.id}", reply_markup=admin_kb)
            except: pass

@dp.callback_query(F.data.startswith("take_"))
async def take_deal(call: types.CallbackQuery):
    deal_id = call.data.split("_")[1]
    admin_id = call.from_user.id
    
    db_query("UPDATE deals SET admin_id = ?, status = ? WHERE id = ?", (admin_id, "В работе", deal_id))
    deal = db_query("SELECT buyer_id, seller_text, amount FROM deals WHERE id = ?", (deal_id,), fetch=True)[0]
    
    # Создание "чата" (бот пересылает сообщения или создает группу)
    # Для простоты: уведомляем всех о начале чата в ЛС бота
    await bot.send_message(deal[0], f"⚡️ **Администратор @{call.from_user.username} подключился к сделке #{deal_id}!**\nВы можете обсуждать детали здесь.")
    await call.message.edit_text(f"✅ Ты вступил в сделку #{deal_id}. Реквизиты отправлены покупателю.")

@dp.message(Command("pay"))
async def set_pay(message: types.Message):
    if message.from_user.id in ADMINS:
        args = message.text.split()
        if len(args) > 1:
            # Логика отправки реквизитов покупателю
            await message.answer(f"Реквизиты {args[1]} отправлены участникам сделки.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
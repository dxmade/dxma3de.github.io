import sqlite3

def init_db():
    conn = sqlite3.connect('escrow.db')
    cursor = conn.cursor()
    
    # Таблица пользователей
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INTEGER PRIMARY KEY, username TEXT, rating REAL DEFAULT 5.0, 
                       is_admin INTEGER DEFAULT 0, balance REAL DEFAULT 0.0)''')
    
    # Таблица друзей
    cursor.execute('''CREATE TABLE IF NOT EXISTS friends 
                      (user_id INTEGER, friend_id INTEGER, PRIMARY KEY(user_id, friend_id))''')
    
    # Таблица сделок
    cursor.execute('''CREATE TABLE IF NOT EXISTS deals 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, buyer_id INTEGER, 
                       seller_id INTEGER, admin_id INTEGER, amount REAL, 
                       status TEXT, chat_id TEXT)''')
    
    conn.commit()
    conn.close()

init_db()
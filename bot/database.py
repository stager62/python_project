import sqlite3

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        first_name TEXT, 
        last_name TEXT
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL, 
        category_name TEXT NOT NULL, 
        category_type TEXT NOT NULL CHECK (category_type IN ("income", "expense")), 
        UNIQUE(user_id, category_name, category_type)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL, 
        account_name TEXT NOT NULL, 
        account_balance REAL DEFAULT 0, 
        UNIQUE(user_id, account_name)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL, 
        transaction_amount REAL NOT NULL, 
        category_name TEXT NOT NULL, 
        account_name TEXT NOT NULL, 
        transaction_type TEXT NOT NULL CHECK (transaction_type IN ("income", "expense")), 
        transaction_date DATE NOT NULL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS transfers (
        transfer_id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER NOT NULL, 
        from_account_id INTEGER NOT NULL, 
        to_account_id INTEGER NOT NULL, 
        transfer_amount REAL NOT NULL, 
        transfer_date DATE NOT NULL,
        FOREIGN KEY (from_account_id) REFERENCES accounts(account_id),
        FOREIGN KEY (to_account_id) REFERENCES accounts(account_id)
    )""")
    conn.commit()
    conn.close()

def db_execute(db_path, sql, params=()):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    conn.close()

def db_fetchone(db_path, sql, params=()):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    result = cursor.fetchone()
    conn.close()
    return result

def db_fetchall(db_path, sql, params=()):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    result = cursor.fetchall()
    conn.close()
    return result

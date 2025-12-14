from telegram import Update
from telegram.ext import ContextTypes
import database
import keyboards
import config

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    database.db_execute(config.DB_PATH, "INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)", (user.id, user.username, user.first_name, user.last_name))
    categories = database.db_fetchall(config.DB_PATH, 'SELECT category_name FROM categories WHERE user_id = ? AND category_name = "Прочее"', (user.id,))
    if not categories:
        database.db_execute(config.DB_PATH, 'INSERT OR IGNORE INTO categories (user_id, category_name, category_type) VALUES (?, "Прочее", "income")', (user.id,))
        database.db_execute(config.DB_PATH, 'INSERT OR IGNORE INTO categories (user_id, category_name, category_type) VALUES (?, "Прочее", "expense")', (user.id,))
    await update.message.reply_text(f"👋 Привет, {user.first_name}!\n\n💼 Я здесь, чтобы помочь тебе контролировать твои финансы.", reply_markup=keyboards.main_menu())

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("💼 Главное меню:", reply_markup=keyboards.main_menu())

async def balance_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_name, account_balance FROM accounts WHERE user_id = ?", (user_id,))
    text = "💰 Ваш баланс:\n\n"
    total_balance = 0
    for account_name, account_balance in accounts:
        text += f"• 💳 {account_name}: {account_balance:.2f} руб.\n"
        total_balance += account_balance
    text += f"\n💵 Общий баланс: {total_balance:.2f} руб."
    await query.edit_message_text(text, reply_markup=keyboards.main_menu())

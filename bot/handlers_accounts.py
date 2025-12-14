from telegram import Update
from telegram.ext import ContextTypes
import database
import keyboards
import config

async def accounts_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("💰 Управление счетами:", reply_markup=keyboards.accounts_menu())

async def add_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["step"] = config.WAITING_ACCOUNT_NAME
    await query.edit_message_text("📝 Введите название счета:", reply_markup=keyboards.cancel("accounts_menu"))

async def add_account_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account_name = update.message.text.strip()
    user_id = update.effective_user.id
    existing = database.db_fetchone(config.DB_PATH, "SELECT account_id FROM accounts WHERE user_id = ? AND account_name = ?", (user_id, account_name))
    if existing:
        await update.message.reply_text(f'❌ Счет с названием "{account_name}" уже существует.', reply_markup=keyboards.cancel("accounts_menu"))
        return
    context.user_data["account_name"] = account_name
    context.user_data["step"] = config.WAITING_ACCOUNT_BALANCE
    await update.message.reply_text("💰 Введите начальный баланс:", reply_markup=keyboards.cancel("accounts_menu"))

async def add_account_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account_balance = update.message.text.strip()
    account_balance = account_balance.replace(",", ".")
    try:
        account_balance = float(account_balance)
        if account_balance < 0 or account_balance > 1000000000000000:
            raise ValueError
    except:
        await update.message.reply_text("❌ Неверная сумма. Возможно вы ввели текст, отрицательное число или вы слишком богатый.", reply_markup=keyboards.cancel("accounts_menu"))
        return
    account_name = context.user_data["account_name"]
    user_id = update.effective_user.id
    database.db_execute(config.DB_PATH, "INSERT INTO accounts (user_id, account_name, account_balance) VALUES (?, ?, ?)", (user_id, account_name, account_balance))
    context.user_data.clear()
    await update.message.reply_text(f'✅ Счет "{account_name}" успешно создан с балансом {account_balance:.2f} руб.', reply_markup=keyboards.main_menu())

async def delete_account_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_id, account_name, account_balance FROM accounts WHERE user_id = ?", (user_id,))
    if not accounts:
        await query.edit_message_text("❌ У вас нет счетов для удаления.", reply_markup=keyboards.accounts_menu())
        return
    await query.edit_message_text("👇 Выберите счет для удаления:", reply_markup=keyboards.account(accounts, "deleted", "accounts_menu"))

async def deleted_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    account_id = int(query.data[15:])
    account = database.db_fetchone(config.DB_PATH, "SELECT user_id, account_name, account_balance FROM accounts WHERE account_id = ?", (account_id,))
    user_id, account_name, account_balance = account
    transactions_count = database.db_fetchone(config.DB_PATH, "SELECT COUNT(*) FROM transactions WHERE account_name = ? AND user_id = ?", (account_name, user_id))[0]
    transfers_count = database.db_fetchone(config.DB_PATH, "SELECT COUNT(*) FROM transfers WHERE (from_account_id = ? OR to_account_id = ?) AND user_id = ?", (account_id, account_id, user_id))[0]
    context.user_data["account_id"] = account_id
    context.user_data["account_name"] = account_name
    text = f"⚠️ Внимание!\n\n💳 Счет: {account_name}\n💰 Баланс: {account_balance:.2f} руб.\n📊 Количество транзакций: {transactions_count}\n🔄 Количество переводов: {transfers_count}\n\n⁉️ Удалить счет и все связанные операции? Отменить это действие будет невозможно!"
    await query.edit_message_text(text, reply_markup=keyboards.confirm_deletion("clean_account", "accounts_menu"))

async def clean_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    account_id = context.user_data.get("account_id")
    account_name = context.user_data.get("account_name")
    database.db_execute(config.DB_PATH, "DELETE FROM transactions WHERE account_name = ? AND user_id = ?", (account_name, user_id))
    database.db_execute(config.DB_PATH, "DELETE FROM transfers WHERE (from_account_id = ? OR to_account_id = ?) AND user_id = ?", (account_id, account_id, user_id))
    database.db_execute(config.DB_PATH, "DELETE FROM accounts WHERE account_id = ?", (account_id,))
    context.user_data.clear()
    await query.edit_message_text(f'✅ Счет "{account_name}" и все его операции успешно удалены.', reply_markup=keyboards.main_menu())

async def accounts_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_name, account_balance FROM accounts WHERE user_id = ? ORDER BY account_name", (user_id,))
    if not accounts:
        await query.edit_message_text("📝 У вас пока нет счетов.", reply_markup=keyboards.accounts_menu())
        return
    text = "💰 Ваши счета:\n\n"
    total_balance = 0
    for account_name, account_balance in accounts:
        text += f"• 💳 {account_name}: {account_balance:.2f} руб.\n"
        total_balance += account_balance
    text += f"\n💵 Общий баланс: {total_balance:.2f} руб."
    await query.edit_message_text(text, reply_markup=keyboards.accounts_menu())

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import database
import keyboards
import config
from utils import parse_date, generate_transactions_file

async def transactions_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("💳 Управление транзакциями:", reply_markup=keyboards.transactions_menu())

async def add_transaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_id, account_name, account_balance FROM accounts WHERE user_id = ?", (user_id,))
    if not accounts:
        await query.edit_message_text("❌ У вас нет счетов. Сначала создайте хотя бы один счет.", reply_markup=keyboards.transactions_menu())
        return
    await query.edit_message_text("💳 📊 Выберите тип операции:", reply_markup=keyboards.transaction_type())

async def add_transaction_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    transaction_type = query.data.replace("transaction_", "")
    context.user_data["transaction_type"] = transaction_type
    context.user_data["step"] = config.WAITING_TRANSACTION_AMOUNT
    await query.edit_message_text("💰 Введите сумму транзакции:", reply_markup=keyboards.cancel("transactions_menu"))

async def add_transaction_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transaction_amount = update.message.text.strip()
    transaction_amount = transaction_amount.replace(",", ".")
    try:
        transaction_amount = float(transaction_amount)
        if transaction_amount < 0 or transaction_amount > 1000000000000000:
            raise ValueError
    except:
        await update.message.reply_text("❌ Неверная сумма. Возможно вы ввели текст, отрицательное число или вы слишком богатый.", reply_markup=keyboards.cancel("transactions_menu"))
        return
    context.user_data["transaction_amount"] = transaction_amount
    user_id = update.effective_user.id
    transaction_type = context.user_data["transaction_type"]
    categories = database.db_fetchall(config.DB_PATH, "SELECT category_id, category_name FROM categories WHERE user_id = ? AND category_type = ?", (user_id, transaction_type))
    await update.message.reply_text("📂 Выберите категорию:", reply_markup=keyboards.category(categories, "select"))

async def add_transaction_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_id = query.data.replace("select_category", "")
    category = database.db_fetchone(config.DB_PATH, "SELECT category_name FROM categories WHERE category_id = ?", (category_id,))
    category_name = category[0] if category else "Прочее"
    context.user_data["category_name"] = category_name
    user_id = query.from_user.id
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_id, account_name, account_balance FROM accounts WHERE user_id = ?", (user_id,))
    await query.edit_message_text("💳 Выберите счет:", reply_markup=keyboards.account(accounts, "select", "transactions_menu"))

async def add_transaction_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    account_id = query.data.replace("select_account", "")
    user_id = query.from_user.id
    account = database.db_fetchone(config.DB_PATH, "SELECT account_name, account_balance FROM accounts WHERE user_id = ? AND account_id = ?", (user_id, account_id))
    account_name = account[0]
    context.user_data["account_id"] = account_id
    context.user_data["account_name"] = account_name
    await query.edit_message_text("📅 Выберите дату транзакции:", reply_markup=keyboards.transaction_date())

async def add_transaction_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "transaction_date_today":
        transaction_date = datetime.now().strftime("%d.%m.%Y")
        await add_transaction_complete(query, context, transaction_date)
    else:
        context.user_data["step"] = config.WAITING_TRANSACTION_DATE_CUSTOM
        await query.edit_message_text("📅 Введите дату в формате ДД.ММ.ГГГГ:", reply_markup=keyboards.cancel("transactions_menu"))

async def add_transaction_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transaction_date = update.message.text.strip()
    transaction_date = parse_date(transaction_date)
    if not transaction_date:
        await update.message.reply_text("❌ Неверный формат даты. Вводите дату в таком формате ДД.ММ.ГГГГ:", reply_markup=keyboards.cancel("transactions_menu"))
        return
    await add_transaction_complete(update, context, transaction_date)

async def add_transaction_complete(query_or_update, context, transaction_date):
    if hasattr(query_or_update, "edit_message_text"):
        query = query_or_update
        user_id = query.from_user.id
        message_func = query.edit_message_text
    else:
        update = query_or_update
        user_id = update.effective_user.id
        message_func = update.message.reply_text
    transaction_type = context.user_data["transaction_type"]
    transaction_amount = context.user_data["transaction_amount"]
    category_name = context.user_data["category_name"]
    account_id = context.user_data["account_id"]
    account_name = context.user_data["account_name"]
    database.db_execute(config.DB_PATH, """INSERT INTO transactions (user_id, transaction_amount, category_name, account_name, transaction_type, transaction_date) VALUES (?, ?, ?, ?, ?, ?)""", (user_id, transaction_amount, category_name, account_name, transaction_type, transaction_date))
    if transaction_type == "income":
        database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance + ? WHERE user_id = ? AND account_id = ?", (transaction_amount, user_id, account_id))
        type_text = "📈 ДОХОД"
    else:
        database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance - ? WHERE user_id = ? AND account_id = ?", (transaction_amount, user_id, account_id))
        type_text = "📉 РАСХОД"
    context.user_data.clear()
    await message_func(f"✅ Транзакция успешно добавлена.\n\n{type_text}\n📂 Категория: {category_name}\n💳 Счет: {account_name}\n📅 Дата: {transaction_date}\n💰 Сумма: {transaction_amount:.2f} руб.", reply_markup=keyboards.main_menu())

async def transaction_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    transactions, filename, file_buffer = generate_transactions_file(config.DB_PATH, user_id)
    if not transactions:
        await query.edit_message_text("❌ У вас нет транзакций.", reply_markup=keyboards.transactions_menu())
        return
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=file_buffer, 
        filename=filename,
        caption="📜 История транзакций:"
    )
    file_buffer.close()
    await query.message.reply_text("📜 Файл с историей транзакций отправлен.", reply_markup=keyboards.transactions_menu())

async def delete_transaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    transactions, filename, file_buffer = generate_transactions_file(config.DB_PATH, user_id)
    if not transactions:
        await query.edit_message_text("❌ У вас нет транзакций для удаления.", reply_markup=keyboards.transactions_menu())
        return
    context.user_data["transactions"] = transactions
    context.user_data["step"] = config.WAITING_DELETE_TRANSACTION
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=file_buffer,
        filename=filename,
        caption="📜 История транзакций:"
    )
    file_buffer.close()
    await query.message.reply_text("👇 Введите номер транзакции из файла:", reply_markup=keyboards.cancel("transactions_menu"))

async def delete_transaction_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    index = int(text) - 1
    transactions = context.user_data.get("transactions", [])
    if not text.isdigit() or index < 0 or index >= len(transactions):
        await update.message.reply_text("❌ Номер транзакции должен быть числом и не должен превышать количсество транзакций.", reply_markup=keyboards.cancel("transactions_menu"))
        return
    transaction_id, transaction_amount, category_name, account_name, transaction_type, transaction_date = transactions[index]
    database.db_execute(config.DB_PATH, "DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
    if transaction_type == "income":
        database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance - ? WHERE account_name = ? AND user_id = ?", (transaction_amount, account_name, user_id))
    else:
        database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance + ? WHERE account_name = ? AND user_id = ?", (transaction_amount, account_name, user_id))
    context.user_data.clear()
    await update.message.reply_text("✅ Транзакция успешно удалена.", reply_markup=keyboards.main_menu())

from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
import database
import keyboards
import config
from utils import parse_date, generate_transfers_file

async def transfers_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("🔄 Управление переводами:", reply_markup=keyboards.transfers_menu())

async def add_transfer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_id, account_name, account_balance FROM accounts WHERE user_id = ?", (user_id,))
    if len(accounts) < 2:
        await query.edit_message_text("❌ Нельзя выполнить перевод. Для перевода нужно как минимум два счета.", reply_markup=keyboards.transfers_menu())
        return
    await query.edit_message_text("👇 Выберите счет списания:", reply_markup=keyboards.account(accounts, "select_from", "transfers_menu"))

async def add_transfer_from(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    transfer_from_id = query.data.replace("select_from_account", "")
    user_id = query.from_user.id
    account = database.db_fetchone(config.DB_PATH, "SELECT account_name FROM accounts WHERE account_id = ?", (transfer_from_id,))
    transfer_from_name = account[0]
    context.user_data["transfer_from_id"] = transfer_from_id
    context.user_data["transfer_from_name"] = transfer_from_name
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_id, account_name, account_balance FROM accounts WHERE account_id != ? AND user_id = ?", (transfer_from_id, user_id))
    await query.edit_message_text("👇 Выберите счет зачисления:", reply_markup=keyboards.account(accounts, "select_to", "transfers_menu"))

async def add_transfer_to(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    transfer_to_id = query.data.replace("select_to_account", "")
    account = database.db_fetchone(config.DB_PATH, "SELECT account_name FROM accounts WHERE account_id = ?", (transfer_to_id,))
    transfer_to_name = account[0]
    context.user_data["transfer_to_id"] = transfer_to_id
    context.user_data["transfer_to_name"] = transfer_to_name
    context.user_data["step"] = config.WAITING_TRANSFER_AMOUNT
    transfer_from_name = context.user_data.get("transfer_from_name")
    await query.edit_message_text(f'💰 Введите сумму перевода со счета "{transfer_from_name}" на счет "{transfer_to_name}":', reply_markup=keyboards.cancel("transfers_menu"))

async def add_transfer_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transfer_amount = update.message.text.strip()
    transfer_amount = transfer_amount.replace(",", ".")
    try:
        transfer_amount = float(transfer_amount)
        if transfer_amount < 0 or transfer_amount > 1000000000000000:
            raise ValueError
    except:
        await update.message.reply_text("❌ Неверная сумма. Возможно вы ввели текст, отрицательное число или вы слишком богатый.", reply_markup=keyboards.cancel("transfers_menu"))
        return
    context.user_data["transfer_amount"] = transfer_amount
    await update.message.reply_text("📅 Выберите дату перевода:", reply_markup=keyboards.transfer_date())

async def add_transfer_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "transfer_date_today":
        transfer_date = datetime.now().strftime("%d.%m.%Y")
        await add_transfer_complete(query, context, transfer_date)
    else:
        context.user_data["step"] = config.WAITING_TRANSFER_DATE_CUSTOM
        await query.edit_message_text("📅 Введите дату в формате ДД.ММ.ГГГГ:", reply_markup=keyboards.cancel("transfers_menu"))

async def add_transfer_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    transfer_date = update.message.text.strip()
    transfer_date = parse_date(transfer_date)
    if not transfer_date:
        await update.message.reply_text("❌ Неверный формат даты. Вводите дату в таком формате ДД.ММ.ГГГГ:", reply_markup=keyboards.cancel("transfers_menu"))
        return
    await add_transfer_complete(update, context, transfer_date)

async def add_transfer_complete(query_or_update, context, transfer_date):
    if hasattr(query_or_update, "edit_message_text"):
        query = query_or_update
        user_id = query.from_user.id
        message_func = query.edit_message_text
    else:
        update = query_or_update
        user_id = update.effective_user.id
        message_func = update.message.reply_text
    transfer_amount = context.user_data["transfer_amount"]
    transfer_from_id = context.user_data["transfer_from_id"]
    transfer_to_id = context.user_data["transfer_to_id"]
    transfer_from_name = context.user_data.get("transfer_from_name")
    transfer_to_name = context.user_data.get("transfer_to_name")
    database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance - ? WHERE account_id = ?", (transfer_amount, transfer_from_id))
    database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance + ? WHERE account_id = ?", (transfer_amount, transfer_to_id))
    database.db_execute(config.DB_PATH, """INSERT INTO transfers (user_id, from_account_id, to_account_id, transfer_amount, transfer_date) VALUES (?, ?, ?, ?, ?)""", (user_id, transfer_from_id, transfer_to_id, transfer_amount, transfer_date))
    context.user_data.clear()
    await message_func(f"✅ Перевод успешно выполнен.\n\n💰 Сумма: {transfer_amount:.2f} руб.\n📤 Со счета: {transfer_from_name}\n📥 На счет: {transfer_to_name}\n📅 Дата: {transfer_date}", reply_markup=keyboards.main_menu())

async def transfer_history_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    transfers, filename, file_buffer = generate_transfers_file(config.DB_PATH, user_id)
    if not transfers:
        await query.edit_message_text("❌ У вас нет переводов.", reply_markup=keyboards.transfers_menu())
        return
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=file_buffer, 
        filename=filename,
        caption="📜 История переводов:"
    )
    file_buffer.close()
    await query.message.reply_text("📜 Файл с историей переводов отправлен.", reply_markup=keyboards.transfers_menu())

async def delete_transfer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    transfers, filename, file_buffer = generate_transfers_file(config.DB_PATH, user_id)
    if not transfers:
        await query.edit_message_text("❌ У вас нет переводов для удаления.", reply_markup=keyboards.transfers_menu())
        return
    context.user_data["transfers"] = transfers
    context.user_data["step"] = config.WAITING_DELETE_TRANSFER
    await context.bot.send_document(
        chat_id=query.message.chat_id,
        document=file_buffer,
        filename=filename,
        caption="📜 История переводов:"
    )
    file_buffer.close()
    await query.message.reply_text("👇 Введите номер перевода из файла:", reply_markup=keyboards.cancel("transfers_menu"))

async def delete_transfer_by_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    index = int(text) - 1
    transfers = context.user_data.get("transfers", [])
    if not text.isdigit() or index < 0 or index >= len(transfers):
        await update.message.reply_text("❌ Номер перевода должен быть числом и не должен превышать количсество транзакций.", reply_markup=keyboards.cancel("transfers_menu"))
        return
    transfer_id, from_account_id, to_account_id, transfer_amount, transfer_date = transfers[index]
    database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance + ? WHERE account_id = ?", (transfer_amount, from_account_id))
    database.db_execute(config.DB_PATH, "UPDATE accounts SET account_balance = account_balance - ? WHERE account_id = ?", (transfer_amount, to_account_id))
    database.db_execute(config.DB_PATH, "DELETE FROM transfers WHERE transfer_id = ?", (transfer_id,))
    context.user_data.clear()
    await update.message.reply_text("✅ Перевод успешно удален.", reply_markup=keyboards.main_menu())

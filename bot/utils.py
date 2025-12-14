import io
import database
from datetime import datetime
from telegram.error import BadRequest

def parse_date(date):
    try:
        date = datetime.strptime(date.strip(), "%d.%m.%Y")
        return date.strftime("%d.%m.%Y")
    except ValueError:
        return None

def parse_custom_date(date):
    try:
        date = date.strip()
        if "-" in date:
            start_custom_date, end_custom_date = date.split("-")
            start_custom_date = datetime.strptime(start_custom_date.strip(), "%d.%m.%Y")
            end_custom_date = datetime.strptime(end_custom_date.strip(), "%d.%m.%Y")
            return start_custom_date.strftime("%d.%m.%Y"), end_custom_date.strftime("%d.%m.%Y")
        start_end_custom_date = datetime.strptime(date, "%d.%m.%Y")
        return start_end_custom_date.strftime("%d.%m.%Y"), start_end_custom_date.strftime("%d.%m.%Y")
    except ValueError:
        return None, None

async def generate_statistics_text(db_path, user_id, account, account_name, start_date=None, end_date=None):
    params = [user_id]
    date_condition = ""
    if start_date and end_date:
        date_condition = " AND transaction_date BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    account_condition = ""
    if account != "all":
        account_condition = " AND account_name = ?"
        params.append(account)
    income_query = f'SELECT COALESCE(SUM(transaction_amount), 0) FROM transactions WHERE user_id = ? AND transaction_type = "income" {date_condition} {account_condition}'
    total_income = database.db_fetchone(db_path, income_query, params)[0]
    expense_query = f'SELECT COALESCE(SUM(transaction_amount), 0) FROM transactions WHERE user_id = ? AND transaction_type = "expense" {date_condition} {account_condition}'
    total_expense = database.db_fetchone(db_path, expense_query, params)[0]
    income_categories_query = f"""SELECT category_name, COALESCE(SUM(transaction_amount), 0) as total FROM transactions WHERE user_id = ? AND transaction_type = "income" {date_condition} {account_condition} GROUP BY category_name ORDER BY total DESC"""
    income_categories = database.db_fetchall(db_path, income_categories_query, params)
    expense_categories_query = f"""SELECT category_name, COALESCE(SUM(transaction_amount), 0) as total FROM transactions WHERE user_id = ? AND transaction_type = "expense" {date_condition} {account_condition} GROUP BY category_name ORDER BY total DESC"""
    expense_categories = database.db_fetchall(db_path, expense_categories_query, params)
    expense_categories = database.db_fetchall(db_path, expense_categories_query, params)
    text = f"📊 СТАТИСТИКА\n\n"
    text += f"💳 Счет: {account_name}\n"
    if start_date and end_date:
        text += f"📅 Период: {start_date} - {end_date}\n\n"
    else:
        text += f"📅 Период: За все время\n\n"
    text += f"📈 Общие доходы: {total_income:.2f} руб.\n"
    text += f"📉 Общие расходы: {total_expense:.2f} руб.\n"
    if income_categories:
        text += f"\n📈 Доходы по категориям:\n"
        for i, (category, amount) in enumerate(income_categories, 1):
            text += f"{i}. {category}: {amount:.2f} руб.\n"
    else:
        text += f"\n📈 Доходы по категориям:\nНет доходов за указанный период\n"
    if expense_categories:
        text += f"\n📉 Расходы по категориям:\n"
        for i, (category, amount) in enumerate(expense_categories, 1):
            text += f"{i}. {category}: {amount:.2f} руб.\n"
    else:
        text += f"\n📉 Расходы по категориям:\nНет расходов за указанный период\n"
    return text

def generate_transactions_file(db_path, user_id):
    import database
    transactions = database.db_fetchall(db_path, """SELECT transaction_id, transaction_amount, category_name, account_name, transaction_type, transaction_date FROM transactions WHERE user_id = ? ORDER BY transaction_date DESC, transaction_id DESC """, (user_id,))
    output = io.StringIO()
    for i, transaction in enumerate(transactions, 1):
        transaction_id, transaction_amount, category_name, account_name, transaction_type, transaction_date = transaction
        if transaction_type == "income":
            emoji = "📈 ДОХОД"
        else:
            emoji = "📉 РАСХОД"
        output.write(f"{i}. {emoji}\n")
        output.write(f"   Сумма: {transaction_amount:.2f} руб.\n")
        output.write(f"   Категория: {category_name}\n")
        output.write(f"   Счет: {account_name}\n")
        output.write(f"   Дата: {transaction_date}\n")
        output.write(f"   ID: {transaction_id}\n")
        output.write("\n")
    file_buffer = io.BytesIO(output.getvalue().encode("utf-8"))
    file_buffer.seek(0)
    output.close()
    return transactions, "transactions.txt", file_buffer

def generate_transfers_file(db_path, user_id):
    import database
    transfers = database.db_fetchall(db_path, """SELECT transfer_id, from_account_id, to_account_id, transfer_amount, transfer_date FROM transfers WHERE user_id = ? ORDER BY transfer_date DESC, transfer_id DESC""", (user_id,))
    output = io.StringIO()
    for i, transfer in enumerate(transfers, 1):
        transfer_id, from_account_id, to_account_id, transfer_amount, transfer_date = transfer
        output.write(f"{i}. 🔄 ПЕРЕВОД\n")
        output.write(f"   Сумма: {transfer_amount:.2f} руб.\n")
        output.write(f"   Со счета: {from_account_id}\n")
        output.write(f"   На счет: {to_account_id}\n")
        output.write(f"   Дата: {transfer_date}\n")
        output.write(f"   ID: {transfer_id}\n")
        output.write("\n")
    file_buffer = io.BytesIO(output.getvalue().encode("utf-8"))
    file_buffer.seek(0)
    output.close()
    return transfers, "transfers.txt", file_buffer

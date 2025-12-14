from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Баланс", callback_data="balance_menu")],
        [InlineKeyboardButton("💳 Транзакции", callback_data="transactions_menu")],
        [InlineKeyboardButton("📁 Категории", callback_data="categories_menu")],
        [InlineKeyboardButton("💰 Счета", callback_data="accounts_menu")],
        [InlineKeyboardButton("📊 Статистика", callback_data="stats_menu")]
    ])

def transactions_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💵 Добавить транзакцию", callback_data="add_transaction")],
        [InlineKeyboardButton("🗑 Удалить транзакцию", callback_data="delete_transaction")],
        [InlineKeyboardButton("📜 История транзакций", callback_data="transactions_history")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

def categories_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
        [InlineKeyboardButton("🗑 Удалить категорию", callback_data="delete_category")],
        [InlineKeyboardButton("📋 Список категорий", callback_data="categories_list")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

def accounts_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Добавить счет", callback_data="add_account")],
        [InlineKeyboardButton("🗑 Удалить счет", callback_data="delete_account")],
        [InlineKeyboardButton("📋 Список счетов", callback_data="accounts_list")],
        [InlineKeyboardButton("🔄 Переводы", callback_data="transfers_menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

def stats_menu(accounts):
    keyboard = [[InlineKeyboardButton("📊 Все счета", callback_data="stats_account_all")]]
    for account in accounts:
        keyboard.append([InlineKeyboardButton(f"💳 {account[0]}", callback_data=f"stats_account_{account[0]}")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(keyboard)

def transfers_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Добавить перевод", callback_data="add_transfer")],
        [InlineKeyboardButton("🗑 Удалить перевод", callback_data="delete_transfer")],
        [InlineKeyboardButton("📜 История переводов", callback_data="transfers_history")],
        [InlineKeyboardButton("🔙 Назад", callback_data="accounts_menu")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ])

def transaction_type():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Доход", callback_data="transaction_income")],
        [InlineKeyboardButton("📉 Расход", callback_data="transaction_expense")],
        [InlineKeyboardButton("❌ Отмена", callback_data="transactions_menu")]
    ])

def transaction_date():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Сегодня", callback_data="transaction_date_today")],
        [InlineKeyboardButton("📝 Ввести дату", callback_data="transaction_date_custom")],
        [InlineKeyboardButton("❌ Отмена", callback_data="transactions_menu")]
    ])

def category_type(add_or_delete):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Доход", callback_data=f"{add_or_delete}_category_income")],
        [InlineKeyboardButton("📉 Расход", callback_data=f"{add_or_delete}_category_expense")],
        [InlineKeyboardButton("❌ Отмена", callback_data="categories_menu")]
    ])

def category(categories, select_or_deleted):
    keyboard = []
    for category_id, category_name in categories:
        keyboard.append([InlineKeyboardButton(category_name, callback_data=f"{select_or_deleted}_category{category_id}")])
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="categories_menu")])
    return InlineKeyboardMarkup(keyboard)

def account(accounts, select_or_deleted, menu):
    keyboard = []
    for account_id, account_name, account_balance in accounts:
        keyboard.append([InlineKeyboardButton(f"{account_name} ({account_balance:.2f} руб.)", callback_data=f"{select_or_deleted}_account{account_id}")])
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data=menu)])
    return InlineKeyboardMarkup(keyboard)

def stats_date():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 За все время", callback_data="stats_date_all_time")],
        [InlineKeyboardButton("📝 Ввести период", callback_data="stats_date_custom")],
        [InlineKeyboardButton("❌ Отмена", callback_data="stats_menu")]
    ])

def transfer_date():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📅 Сегодня", callback_data="transfer_date_today")],
        [InlineKeyboardButton("📝 Ввести дату", callback_data="transfer_date_custom")],
        [InlineKeyboardButton("❌ Отмена", callback_data="transfers_menu")]
    ])

def confirm_deletion(clean, menu):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Да, удалить", callback_data=clean)],
        [InlineKeyboardButton("❌ Отмена", callback_data=menu)]
    ])

def cancel(menu):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Отмена", callback_data=menu)]
    ])

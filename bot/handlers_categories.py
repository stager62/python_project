from telegram import Update
from telegram.ext import ContextTypes
import database
import keyboards
import config

async def categories_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("📁 Управление категориями:", reply_markup=keyboards.categories_menu())

async def add_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["step"] = config.WAITING_CATEGORY_NAME
    await query.edit_message_text("📝 Введите название категории:", reply_markup=keyboards.cancel("categories_menu"))

async def add_category_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category_name = update.message.text.strip()
    context.user_data["category_name"] = category_name
    await update.message.reply_text("📊 Выберите тип категории:", reply_markup=keyboards.category_type("add"))

async def add_category_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_type = query.data.replace("add_category_", "")
    category_name = context.user_data.get("category_name")
    user_id = query.from_user.id
    existing = database.db_fetchone(config.DB_PATH, "SELECT category_id FROM categories WHERE user_id = ? AND category_name = ? AND category_type = ?", (user_id, category_name, category_type))
    if existing:
        await query.edit_message_text(f'❌ Категория "{category_name}" уже существует.', reply_markup=keyboards.cancel("categories_menu"))
        return
    database.db_execute(config.DB_PATH, "INSERT INTO categories (user_id, category_name, category_type) VALUES (?, ?, ?)", (user_id, category_name, category_type))
    if category_type == "income":
        type_text = "доход"
        emoji = "📈"
    else:
        type_text = "расход"
        emoji = "📉"
    context.user_data.clear()
    await query.edit_message_text(f'{emoji} Категория "{category_name}" ({type_text}) успешно добавлена.', reply_markup=keyboards.main_menu())

async def delete_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("📊 Выберите тип категории:", reply_markup=keyboards.category_type("delete"))

async def delete_category_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_type = query.data.replace("delete_category_", "")
    user_id = query.from_user.id
    categories = database.db_fetchall(config.DB_PATH, 'SELECT category_id, category_name FROM categories WHERE user_id = ? AND category_type = ? AND category_name != "Прочее"', (user_id, category_type))
    if not categories:
        if category_type == "income":
            type_text = "доходах"
        else:
            type_text = "расходах"
        await query.edit_message_text(f"❌ У вас нет категорий для удаления в {type_text}.", reply_markup=keyboards.categories_menu())
        return
    await query.edit_message_text("👇 Выберите категорию для удаления:", reply_markup=keyboards.category(categories, "deleted"))

async def deleted_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_id = int(query.data[16:])
    context.user_data["category_id"] = category_id
    user_id = query.from_user.id
    category = database.db_fetchone(config.DB_PATH, "SELECT category_name, category_type FROM categories WHERE category_id = ?", (category_id,))
    category_name, category_type = category
    transactions_count = database.db_fetchone(config.DB_PATH, "SELECT COUNT(*) FROM transactions WHERE category_name = ? AND user_id = ?", (category_name, user_id))[0]
    text = f'⚠️ Внимание! У категории "{category_name}" есть {transactions_count} транзакций.\n\nПри удалении категории все транзакции будут перемещены в категорию "Прочее". Продолжить?'
    await query.edit_message_text(text, reply_markup=keyboards.confirm_deletion("clean_category", "category_menu"))

async def clean_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    category_id = context.user_data["category_id"]
    user_id = query.from_user.id
    category = database.db_fetchone(config.DB_PATH, "SELECT category_name, category_type FROM categories WHERE category_id = ?", (category_id,))
    category_name, category_type = category
    other_category_name = "Прочее"
    database.db_execute(config.DB_PATH, "UPDATE transactions SET category_name = ? WHERE category_name = ? AND user_id = ?", (other_category_name, category_name, user_id))
    database.db_execute(config.DB_PATH, "DELETE FROM categories WHERE category_id = ?", (category_id,))
    transactions_count = database.db_fetchone(config.DB_PATH, "SELECT COUNT(*) FROM transactions WHERE category_name = ? AND user_id = ?", (other_category_name, user_id))[0]
    context.user_data.clear()
    await query.edit_message_text(f'✅ Категория "{category_name}" удалена!\n📊 {transactions_count} транзакций перемещено в категорию "Прочее".', reply_markup=keyboards.main_menu())

async def categories_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    categories = database.db_fetchall(config.DB_PATH, "SELECT category_name, category_type FROM categories WHERE user_id = ? ORDER BY category_type, category_name", (user_id,))
    if not categories:
        await query.edit_message_text("📝 У вас пока нет категорий.", reply_markup=keyboards.categories_menu())
        return
    income = []
    expense = []
    for category_name, category_type in categories:
        if category_type == "income":
            income.append(category_name)
        else:
            expense.append(category_name)
    text = "📁 Ваши категории:\n\n"
    if income:
        text += "📈 Доходы:\n• " + "\n• ".join(income) + "\n\n"
    if expense:
        text += "📉 Расходы:\n• " + "\n• ".join(expense)
    await query.edit_message_text(text, reply_markup=keyboards.categories_menu())

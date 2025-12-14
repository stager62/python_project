from telegram import Update
from telegram.ext import ContextTypes
import database
import keyboards
import config
from utils import parse_custom_date, generate_statistics_text

async def stats_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str = None):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_name FROM accounts WHERE user_id = ?", (user_id,))
    if text:
        await query.edit_message_text(text, reply_markup=keyboards.stats_menu(accounts))
    else:
        await query.edit_message_text("👇 Выберите счет для просмотра статистики:", reply_markup=keyboards.stats_menu(accounts))

async def add_stats_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "stats_account_all":
        context.user_data["stats_account"] = "all"
        context.user_data["stats_account_name"] = "Все счета"
    else:
        account_name = data.replace("stats_account_", "")
        context.user_data["stats_account"] = account_name
        context.user_data["stats_account_name"] = account_name
    await query.edit_message_text(f"📅 Выберите период:", reply_markup=keyboards.stats_date()
    )

async def add_stats_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "stats_date_all_time":
        stats_account = context.user_data.get("stats_account")
        stats_account_name = context.user_data.get("stats_account_name")
        user_id = query.from_user.id
        text = await generate_statistics_text(config.DB_PATH, user_id, stats_account, stats_account_name)
        await stats_menu_handler(update, context, text = text)
    else:
        context.user_data["step"] = config.WAITING_STATS_CUSTOM_DATE
        await query.edit_message_text(f"📅 Введите период в формате ДД.ММ.ГГГГ-ДД.ММ.ГГГГ или ДД.ММ.ГГГГ:", reply_markup=keyboards.cancel("stats_menu"))

async def add_stats_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    start_custom_date, end_custom_date = parse_custom_date(text)
    if not start_custom_date or not end_custom_date:
        await update.message.reply_text("❌ Неверный формат. Вводите дату в таком формате ДД.ММ.ГГГГ-ДД.ММ.ГГГГ или ДД.ММ.ГГГГ:")
        return
    user_id = update.effective_user.id
    stats_account = context.user_data.get("stats_account")
    stats_account_name = context.user_data.get("stats_account_name")
    text = await generate_statistics_text(config.DB_PATH, user_id, stats_account, stats_account_name, start_custom_date, end_custom_date)
    accounts = database.db_fetchall(config.DB_PATH, "SELECT account_name FROM accounts WHERE user_id = ?", (user_id,))
    await update.message.reply_text(text, reply_markup=keyboards.stats_menu(accounts))

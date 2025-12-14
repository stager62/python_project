from telegram import Update
from telegram.ext import ContextTypes
import keyboards
import config
from handlers_transactions import add_transaction_amount, add_transaction_custom_date, delete_transaction_by_number
from handlers_categories import add_category_name
from handlers_accounts import add_account_name, add_account_balance
from handlers_transfers import add_transfer_amount, add_transfer_custom_date, delete_transfer_by_number
from handlers_stats import add_stats_custom_date

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    step = context.user_data.get("step", "")
    
    if step == config.WAITING_TRANSACTION_AMOUNT:
        await add_transaction_amount(update, context)
    elif step == config.WAITING_TRANSACTION_DATE_CUSTOM:
        await add_transaction_custom_date(update, context)
    elif step == config.WAITING_CATEGORY_NAME:
        await add_category_name(update, context)
    elif step == config.WAITING_ACCOUNT_NAME:
        await add_account_name(update, context)
    elif step == config.WAITING_ACCOUNT_BALANCE:
        await add_account_balance(update, context)
    elif step == config.WAITING_TRANSFER_AMOUNT:
        await add_transfer_amount(update, context)
    elif step == config.WAITING_TRANSFER_DATE_CUSTOM:
        await add_transfer_custom_date(update, context)
    elif step == config.WAITING_DELETE_TRANSACTION:
        await delete_transaction_by_number(update, context)
    elif step == config.WAITING_DELETE_TRANSFER:
        await delete_transfer_by_number(update, context)
    elif step == config.WAITING_STATS_CUSTOM_DATE:
        await add_stats_custom_date(update, context)
    else:
        await update.message.reply_text("❌ Неизвестная команда. Возвращаю в главное меню.", reply_markup=keyboards.main_menu())

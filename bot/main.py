import database
import config
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from handlers_start import start, main_menu_handler, balance_menu_handler
from handlers_transactions import transactions_menu_handler, add_transaction_handler, add_transaction_type, add_transaction_category, add_transaction_account, add_transaction_date, add_transaction_complete, transaction_history_handler, delete_transaction_handler
from handlers_categories import categories_menu_handler, add_category_handler, add_category_type, delete_category_handler, delete_category_type, deleted_category, clean_category, categories_list_handler
from handlers_accounts import accounts_menu_handler, add_account_handler, delete_account_handler, deleted_account, clean_account, accounts_list_handler
from handlers_transfers import transfers_menu_handler, add_transfer_handler, add_transfer_from, add_transfer_to, add_transfer_amount, add_transfer_date, add_transfer_complete, transfer_history_handler, delete_transfer_handler
from handlers_stats import stats_menu_handler, add_stats_account, add_stats_date
from handlers_messages import handle_message

def main():
    database.init_db(config.DB_PATH)
    print("Бот запущен...")
    application = Application.builder().token(config.TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(main_menu_handler, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(balance_menu_handler, pattern="^balance_menu$"))
    application.add_handler(CallbackQueryHandler(transactions_menu_handler, pattern="^transactions_menu$"))
    application.add_handler(CallbackQueryHandler(categories_menu_handler, pattern="^categories_menu$"))
    application.add_handler(CallbackQueryHandler(accounts_menu_handler, pattern="^accounts_menu$"))
    application.add_handler(CallbackQueryHandler(transfers_menu_handler, pattern="^transfers_menu$"))
    application.add_handler(CallbackQueryHandler(stats_menu_handler, pattern="^stats_menu$"))
    application.add_handler(CallbackQueryHandler(add_category_handler, pattern="^add_category$"))
    application.add_handler(CallbackQueryHandler(add_category_type, pattern="^(add_category_income|add_category_expense)$"))
    application.add_handler(CallbackQueryHandler(delete_category_handler, pattern="^delete_category$"))
    application.add_handler(CallbackQueryHandler(delete_category_type, pattern="^(delete_category_income|delete_category_expense)$"))
    application.add_handler(CallbackQueryHandler(deleted_category, pattern="^deleted_category"))
    application.add_handler(CallbackQueryHandler(clean_category, pattern="^clean_category"))
    application.add_handler(CallbackQueryHandler(categories_list_handler, pattern="^categories_list$"))
    application.add_handler(CallbackQueryHandler(add_transaction_handler, pattern="^add_transaction$"))
    application.add_handler(CallbackQueryHandler(add_transaction_type, pattern="^(transaction_income|transaction_expense)$"))
    application.add_handler(CallbackQueryHandler(add_transaction_category, pattern="^select_category"))
    application.add_handler(CallbackQueryHandler(add_transaction_account, pattern="^select_account"))
    application.add_handler(CallbackQueryHandler(add_transaction_date, pattern="^(transaction_date_today|transaction_date_custom)$"))
    application.add_handler(CallbackQueryHandler(delete_transaction_handler, pattern="^delete_transaction$"))
    application.add_handler(CallbackQueryHandler(transaction_history_handler, pattern="^transactions_history$"))
    application.add_handler(CallbackQueryHandler(add_account_handler, pattern="^add_account$"))
    application.add_handler(CallbackQueryHandler(delete_account_handler, pattern="^delete_account$"))
    application.add_handler(CallbackQueryHandler(deleted_account, pattern="^deleted_account"))
    application.add_handler(CallbackQueryHandler(clean_account, pattern="^clean_account$"))
    application.add_handler(CallbackQueryHandler(accounts_list_handler, pattern="^accounts_list$"))
    application.add_handler(CallbackQueryHandler(add_transfer_handler, pattern="^add_transfer$"))
    application.add_handler(CallbackQueryHandler(add_transfer_from, pattern="^select_from_account"))
    application.add_handler(CallbackQueryHandler(add_transfer_to, pattern="^select_to_account"))
    application.add_handler(CallbackQueryHandler(add_transfer_date, pattern="^(transfer_date_today|transfer_date_custom)$"))
    application.add_handler(CallbackQueryHandler(transfer_history_handler, pattern="^transfers_history$"))
    application.add_handler(CallbackQueryHandler(delete_transfer_handler, pattern="^delete_transfer$"))
    application.add_handler(CallbackQueryHandler(add_stats_account, pattern="^stats_account_"))
    application.add_handler(CallbackQueryHandler(add_stats_date, pattern="^(stats_date_all_time|stats_date_custom)$"))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

if __name__ == "__main__":
    main()

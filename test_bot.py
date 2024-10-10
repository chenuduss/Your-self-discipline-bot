from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes



async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}!')

if __name__ == '__main__':
    app = ApplicationBuilder().token("7694651318:AAGsCIDTAqTCXcNRrVKaCKYc6XNwfgUvx4I").build()

    app.add_handler(CommandHandler("status", status))

    app.run_polling()

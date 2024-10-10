from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import argparse


async def push(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text(f'push {update.effective_user.first_name}!')

async def pop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text(f'pop {update.effective_user.first_name}!')    

async def mystat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text(f'mystat {update.effective_user.first_name}!')    

async def stat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text(f'stat {update.effective_user.first_name}!')     

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    await update.message.reply_text(f'Hello {update.effective_user.first_name}!')    

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
            prog = 'YSDB',
            description = '''Your self-discipline bot''',
            epilog = '''(c) 2024'''
            )

    parser.add_argument ('--host', dest='host', action="store", type=str, required=True)
    parser.add_argument ('--port', dest='port', action="store", type=str, default=5432, type=int)
    parser.add_argument ('--db', dest='db', action="store", type=str, required=True)
    parser.add_argument ('--user', dest='user', action="store", type=str, required=True)
    parser.add_argument ('--password', dest='password', action="store", type=str, required=True)
    parser.add_argument ('--bot_token', dest='bot_token', action="store", type=str, required=True)

    args = parser.parse_args()

    app = ApplicationBuilder().token(args.bot_token).build()

    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("push", push))
    app.add_handler(CommandHandler("pop", pop))
    app.add_handler(CommandHandler("mystat", mystat))
    app.add_handler(CommandHandler("stat", stat))

    app.run_polling()

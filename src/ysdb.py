from telegram import Update, User, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import argparse
from db_worker import DbWorkerService
import logging

class YSDBot:
    def __init__(self, db_worker:DbWorkerService):
        self.Db = db_worker

    @staticmethod
    def GetUserTitleForLog(user:User) -> str:
        return "["+str(user.id)+"]{"+user.name+"}" 
    
    @staticmethod
    def GetChatTitleForLog(ch:Chat) -> str:
        return "["+str(ch.id)+"]{"+ch.effective_name+"}"     

    @staticmethod    
    def MakeUserTitle(user:User) -> str:
        result = user.full_name
        if (len(result) < 2):
            result = user.name
        if (len(result) < 1):
            result = "@"+str(user.id)
        return result
    
    @staticmethod    
    def MakeChatTitle(ch:Chat) -> str:
        result = ch.effective_name
        if (len(result) < 1):
            result = "@"+str(ch.id)
        return result    

    async def push(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[STAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    

        self.Db.EnsureUserExists(update.effective_user.id, YSDBot.MakeUserTitle(update.effective_user))
        self.Db.EnsureChatExists(update.effective_chat.id, YSDBot.MakeChatTitle(update.effective_chat))

        await update.message.reply_text(f'push {update.effective_user.first_name}!')

    async def pop(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[STAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    
        await update.message.reply_text(f'pop {update.effective_user.first_name}!')    

    async def mystat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[STAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    
        await update.message.reply_text(f'mystat {update.effective_user.first_name}!')    

    async def stat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
        logging.info("[STAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    

        await update.message.reply_text(f'stat {update.effective_user.first_name}!')     

    async def status(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[STATUS] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    

        await update.message.reply_text(f'Hello {update.effective_user.first_name}!')





if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(
        prog = 'YSDB', description = '''Your self-discipline bot''', epilog = '''(c) 2024''')

    parser.add_argument ('--host', dest='host', action="store", type=str, required=True)
    parser.add_argument ('--port', dest='port', action="store", type=str, default=5432, type=int)
    parser.add_argument ('--db', dest='db', action="store", type=str, required=True)
    parser.add_argument ('--user', dest='user', action="store", type=str, required=True)
    parser.add_argument ('--password', dest='password', action="store", type=str, required=True)
    parser.add_argument ('--bot_token', dest='bot_token', action="store", type=str, required=True)

    args = parser.parse_args()

    db = DbWorkerService({
        'host': args.host,
        'port': args.port,
        'db': args.db,
        'username': args.user,
        'password': args.password
    })

    app = ApplicationBuilder().token(args.bot_token).build()

    bot = YSDBot(db)

    app.add_handler(CommandHandler("status", bot.status))
    app.add_handler(CommandHandler("push", bot.push))
    app.add_handler(CommandHandler("pop", bot.pop))
    app.add_handler(CommandHandler("mystat", bot.mystat))
    app.add_handler(CommandHandler("stat", bot.stat))

    app.run_polling()

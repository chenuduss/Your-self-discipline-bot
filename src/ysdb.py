from telegram import Update, User, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import argparse
from db_worker import DbWorkerService
import logging
import json

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

    @staticmethod
    def ParsePushMessage(msg:str) -> int:
        parts = msg.strip().split(" ", 1)
        second_part = parts[1].strip()
        koeff = 1
        if second_part[-1] in ['k', 'K', 'к', 'К']:
            second_part = second_part[:-1]
            koeff = 1000
        return int(second_part)*koeff


    async def push(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[PUSH] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat) + ", text: "+update.message.text)    

        self.Db.EnsureUserExists(update.effective_user.id, YSDBot.MakeUserTitle(update.effective_user))
        self.Db.EnsureChatExists(update.effective_chat.id, YSDBot.MakeChatTitle(update.effective_chat))

        amount = 0
        try:
            amount = YSDBot.ParsePushMessage(update.message.text)
        except BaseException as ex:
            logging.error("[PUSH] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat) + ", text: "+update.message.text + ". EXCEPTION: "+str(ex))       

        if amount < 1:
            await update.message.reply_text("Меньше одного символа пушить нельзя") 
        if amount > 100000:
            await update.message.reply_text("Больше 100k пушить нельзя")     
            
        self.Db.InsertSelfContribRecord(update.effective_user.id, update.effective_chat.id, amount)

        await update.message.reply_text("Сохранено "+str(amount)+" символов. \n\nПоследние 5 записей:") 

    async def pop(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[POP] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    
        await update.message.reply_text(f'pop {update.effective_user.first_name}!')    

    async def mystat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[MYSTAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    
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


    parser.add_argument ('--conf', dest='conf', action="store", type=str, required=True)

    args = parser.parse_args()

    
    with open(args.conf, 'r') as file:
        conf = json.load(file)

    db = DbWorkerService(conf['db'])

    app = ApplicationBuilder().token(conf['bot_token']).build()

    bot = YSDBot(db)

    app.add_handler(CommandHandler("status", bot.status))
    app.add_handler(CommandHandler("push", bot.push))
    app.add_handler(CommandHandler("pop", bot.pop))
    app.add_handler(CommandHandler("mystat", bot.mystat))
    app.add_handler(CommandHandler("stat", bot.stat))

    app.run_polling()

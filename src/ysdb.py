from telegram import Update, User, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import argparse
from db_worker import DbWorkerService
import logging
import json
import time
from datetime import timedelta, datetime
from ysdb_exception import YSDBException

    
def MakeHumanReadableAmount(value:int) -> str: 
    if value > 1000:
        return str(round(float(value)/1000.0, 1))+"k" 
        
    return str(value)

class YSDBot:
    def __init__(self, db_worker:DbWorkerService):
        self.Db = db_worker
        self.StartTS = int(time.time())
        self.LastHandledPushCommand = time.time()
        self.PushCommandMinimunInterval = 0.8
        self.LastHandledPopCommand = time.time()
        self.PopCommandMinimunInterval = 1.5
        self.LastHandledMyStatCommand = time.time()
        self.MyStatCommandMinimunInterval = 5
        self.LastHandledStatCommand = time.time()
        self.StatCommandMinimunInterval = 10

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
        try:
            parts = msg.strip().split(" ", 1)
            second_part = parts[1].strip()
            koeff = 1
            if second_part[-1] in ['k', 'K', 'к', 'К']:
                second_part = second_part[:-1]
                koeff = 1000
            return int(second_part)*koeff
        except BaseException as ex:
            raise YSDBException("Некорректный формат команды /push")     


    def MakeLastPushingInfo(self, user_id:int, chat_id:int, count:int) -> str:
        user_contribs = self.Db.SelectLastUserSelfContribs(user_id, chat_id, count)
        result = ""
        cc = 0
        for uc in user_contribs:
            if cc > 0:
                result += "\n"

            result += "№"+str(cc) +" " + uc.TS.strftime("%d.%m.%Y %H:%M")+": "+MakeHumanReadableAmount(uc.Amount)
            cc += 1

        return result

    def MakeLastPushingInfoBlock(self, user_id:int, chat_id:int) -> str:
        result = "Последние 5 записей:\n"

        return result+self.MakeLastPushingInfo(user_id, chat_id, 5)

    async def push(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[PUSH] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat) + ", text: "+update.message.text)    
        if time.time() - self.LastHandledPushCommand < self.PushCommandMinimunInterval:
            logging.warning("[PUSH] Ignore command from user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat) + ", text: "+update.message.text)
            return
        self.LastHandledPushCommand = time.time()

        try:
            self.Db.EnsureUserExists(update.effective_user.id, YSDBot.MakeUserTitle(update.effective_user))
            self.Db.EnsureChatExists(update.effective_chat.id, YSDBot.MakeChatTitle(update.effective_chat))            
        
            amount = YSDBot.ParsePushMessage(update.message.text)            

            if amount < 1:
                raise YSDBException("Меньше одного символа пушить нельзя") 
            if amount > 100000:
                raise YSDBException("Больше 100k пушить нельзя")     
            
            self.Db.InsertSelfContribRecord(update.effective_user.id, update.effective_chat.id, amount)

            reply_message = "Сохранено "+MakeHumanReadableAmount(amount)+" символов. \n\n"+self.MakeLastPushingInfoBlock(update.effective_user.id, update.effective_chat.id)

            await update.message.reply_text(reply_message) 
        except YSDBException as ex:
            await update.message.reply_text("Ошибка!\n\n"+str(ex)) 
        except BaseException as ex:    
            logging.error("[PUSH] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat) + ", text: "+update.message.text + ". EXCEPTION: "+str(ex))       
            await update.message.reply_text("Ошибка при выполнении команды: "+str(ex))
    

    async def pop(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[POP] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat)+ ", text: "+update.message.text)    
        if time.time() - self.LastHandledPopCommand < self.PopCommandMinimunInterval:
            logging.warning("[POP] Ignore command from user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat)+ ", text: "+update.message.text)
            return
        self.LastHandledPopCommand = time.time()

        await update.message.reply_text(f'pop {update.effective_user.first_name}!')    

    async def mystat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.info("[MYSTAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    
        if time.time() - self.LastHandledMyStatCommand < self.MyStatCommandMinimunInterval:
            logging.warning("[MYSTAT] Ignore command from user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))        
            return
        self.LastHandledMyStatCommand = time.time()

        try:
            stat_message = "Привет, " + YSDBot.MakeUserTitle(update.effective_user) + "!\n\n"
            stat_message += self.MakeLastPushingInfoBlock(update.effective_user.id, update.effective_chat.id)

            stat_message += "\n"
            stat_message += "\nЗа последние сутки: "+MakeHumanReadableAmount(self.Db.GetAmountSum(update.effective_user.id, update.effective_chat.id, datetime.now() - timedelta(days=1), datetime.now()))
            stat_message += "\nЗа последние 3 суток: "+MakeHumanReadableAmount(self.Db.GetAmountSum(update.effective_user.id, update.effective_chat.id, datetime.now() - timedelta(days=3), datetime.now()))
            stat_message += "\nЗа последние 7 суток: "+MakeHumanReadableAmount(self.Db.GetAmountSum(update.effective_user.id, update.effective_chat.id, datetime.now() - timedelta(days=7), datetime.now()))
            stat_message += "\nЗа последние 15 суток: "+MakeHumanReadableAmount(self.Db.GetAmountSum(update.effective_user.id, update.effective_chat.id, datetime.now() - timedelta(days=15), datetime.now()))
            stat_message += "\nЗа последние 30 суток: "+MakeHumanReadableAmount(self.Db.GetAmountSum(update.effective_user.id, update.effective_chat.id, datetime.now() - timedelta(days=30), datetime.now()))
            stat_message += "\nЗа всё время: "+MakeHumanReadableAmount(self.Db.GetAmountSum(update.effective_user.id, update.effective_chat.id, datetime.now() - timedelta(days=3600), datetime.now()))

            if update.effective_user.id == update.effective_chat.id:
                stat_message += "\n\n((Тут будет статистика по всем чатам))"

            await update.message.reply_text(stat_message)     
        except YSDBException as ex:
            await update.message.reply_text("Ошибка!\n\n"+str(ex)) 
        except BaseException as ex:    
            logging.error("[MYSTAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat) + ", text: "+update.message.text + ". EXCEPTION: "+str(ex))       
            await update.message.reply_text("Ошибка при выполнении команды: "+str(ex))  

    async def stat(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:        
        logging.info("[STAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    
        if time.time() - self.LastHandledStatCommand < self.StatCommandMinimunInterval:
            logging.warning("[STAT] Ignore command from user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))                
            return
        self.LastHandledStatCommand = time.time()

        try:
            stat_message = "Это чат " + YSDBot.MakeChatTitle(update.effective_chat) + "\n\n"

                     

            await update.message.reply_text(stat_message)     
        except YSDBException as ex:
            await update.message.reply_text("Ошибка!\n\n"+str(ex)) 
        except BaseException as ex:    
            logging.error("[MYSTAT] user id "+YSDBot.GetUserTitleForLog(update.effective_user)+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat) + ", text: "+update.message.text + ". EXCEPTION: "+str(ex))       
            await update.message.reply_text("Ошибка при выполнении команды: "+str(ex))  

    @staticmethod
    def get_help() -> str:
        result = "Команды: "
        result +="\n* Моя статиcтика: /mystat"
        result +="\n*Добавление знаков: /push <количетво знаков>"
        result +="\n** Примеры:"
        result +="\n** /push 190"
        result +="\n** /push 5k"

        return result

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        ut = YSDBot.GetUserTitleForLog(update.effective_user)
        logging.info("[STATUS] user id "+ut+", chat id "+YSDBot.GetChatTitleForLog(update.effective_chat))    
        status_msg = "Привет, "+YSDBot.MakeUserTitle(update.effective_user)+"! ("+ut+")"
        status_msg +="\nЭто чат: "+YSDBot.MakeChatTitle(update.effective_chat)
        uptime_sec = time.time() - self.StartTS
        uptime = timedelta(seconds = uptime_sec)
        status_msg +="\nАптайм "+ str(uptime)
        status_msg += "\n\n"+ YSDBot.get_help()

        #status_msg +="\nВерсия "+ str(uptime)
        await update.message.reply_text(status_msg)


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


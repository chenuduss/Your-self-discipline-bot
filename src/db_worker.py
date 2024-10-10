import psycopg2
import psycopg2.extras
from psycopg2 import pool

def ConnectionPool(function_to_decorate):    
    def wrapper(*args, **kwargs):
        obj = args[0]
        conn = obj.Pool.getconn()
        kwargs['connection'] = conn
        try:
            return function_to_decorate(*args, **kwargs)
        finally:
            obj.Pool.putconn(conn)     
        
    return wrapper

class DbWorkerService:   
    def __init__(self, config:dict):
        psycopg2.extras.register_uuid()
        self.Pool = psycopg2.pool.ThreadedConnectionPool(
            5, 20,
            user = config["username"],
            password = config["password"],
            host = config["host"],
            port = config["port"],
            database = config["db"])       

        
    @ConnectionPool    
    def EnsureUserExists(self, user_id:int, title:str,  connection=None) -> None:
        ps_cursor = connection.cursor()          
        ps_cursor.execute("SELECT id FROM sd_user WHERE id = %s", (user_id, ))        
        rows = ps_cursor.fetchall()
        if len(rows) < 1:            
            ps_cursor.execute("INSERT INTO sd_user (id, title) VALUES (%s, %s)", (user_id, title)) 
            connection.commit()
        

    @ConnectionPool    
    def EnsureChatExists(self, chat_id:int, title:str, connection=None) -> None:
        ps_cursor = connection.cursor()          
        ps_cursor.execute("SELECT id FROM chat WHERE id = %s", (chat_id, ))        
        rows = ps_cursor.fetchall()
        if len(rows) < 1:            
            ps_cursor.execute("INSERT INTO chat (id, title) VALUES (%s, %s)", (chat_id, title)) 
            connection.commit()   
        
    @ConnectionPool    
    def InsertSelfContribRecord(self, user_id:int, chat_id:int, amount:int, connection=None) -> None:
        ps_cursor = connection.cursor() 
        ps_cursor.execute("INSERT INTO self_contrib_record (user_id, chat_id, amount) VALUES (%s, %s, %s)", (user_id, chat_id, amount)) 
        connection.commit() 
    
    @ConnectionPool    
    def CalcAllUserStat(self, user_id:int, connection=None) -> None:
        raise NotImplementedError("DbWorkerService.CalcAllUserStat")   

    @ConnectionPool    
    def CalcUserStat(self, user_id:int, chat_id:int, connection=None) -> None:
        raise NotImplementedError("DbWorkerService.CalcUserStat")     
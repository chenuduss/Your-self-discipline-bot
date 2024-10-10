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
        raise NotImplementedError("DbWorkerService.EnsureUserExists")    

    @ConnectionPool    
    def EnsureChatExists(self, chat_id:int, title:str, connection=None) -> None:
        raise NotImplementedError("DbWorkerService.EnsureChatExists")        
        
    @ConnectionPool    
    def InsertSelfContribRecord(self, user_id:int, chat_id:int, amount:int, connection=None) -> None:
        raise NotImplementedError("DbWorkerService.InsertSelfContribRecord")
    
    @ConnectionPool    
    def CalcAllUserStat(self, user_id:int, connection=None) -> None:
        raise NotImplementedError("DbWorkerService.CalcAllUserStat")   

    @ConnectionPool    
    def CalcUserStat(self, user_id:int, chat_id:int, connection=None) -> None:
        raise NotImplementedError("DbWorkerService.CalcUserStat")     
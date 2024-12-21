from typing import Optional, List, Dict
from fastapi import HTTPException,status

class AppException(Exception):
    def __init__(self,message:str,status_code:int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class DatabaseException(AppException):
    def __init__(self,message:str="Database Error"):
        super().__init__(message,status.HTTP_503_SERVICE_UNAVAILABLE)  

class EmbeddingException(AppException):
    def __init__(self,message:str="Embedding Error"):
        super().__init__(message,status.HTTP_500_INTERNAL_SERVER_ERROR)

def handle_exception(e:AppException):
    return {
        "error":e.message,
        "message":e.message,
        "status_code":e.status_code
    }

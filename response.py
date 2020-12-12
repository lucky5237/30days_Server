from pydantic import BaseModel
from config import SERVER_ERROR_MESSAGE


def makeBaseResponseDict(code, message, data):
    if data:
        return {"code": code, "message": message, "data": data}
    else:
        return {"code": code, "message": message}


def SucResponse(code=200, message="Success", data=None):
    return makeBaseResponseDict(code, message, data)


def BaseErrResponse(code, message, data=None):
    return makeBaseResponseDict(code, message, data)


def ServerErrorResponse(code=500, message=SERVER_ERROR_MESSAGE, data=None):
    return makeBaseResponseDict(code, message, data)



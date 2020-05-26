from motor.motor_asyncio import AsyncIOMotorClient


class DataBase:
    connection: AsyncIOMotorClient = None
    history_loans = None
    loans = None
    users = None
    clients = None


db = DataBase()

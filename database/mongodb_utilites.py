from motor.motor_asyncio import AsyncIOMotorClient
import logging
from database.mongodb import db


async def connect_to_mongo():
    logging.info("connecting to loansAnalyzerDb ...")
    db.connection = AsyncIOMotorClient(
        "mongodb+srv://aicserrock:LekrsFCWcwP0ygSm@cluster0-bqeb1.azure.mongodb.net/test?retryWrites=true&w=majority",
        maxPoolSize=10, minPoolSize=10)
    db.clients = db.connection.loansAnalyzerDb.clients
    db.users = db.connection.loansAnalyzerDb.users
    db.history_loans = db.connection.loansAnalyzerDb.history_loans
    db.loans = db.connection.loansAnalyzerDb.loans
    logging.info("connected to loansAnalyzerDb")


async def disconnect_from_mongo():
    logging.info("closing connection ...")
    db.connection.close()
    logging.info("closed connection")

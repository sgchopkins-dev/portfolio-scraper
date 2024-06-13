import os
import certifi
from pymongo import MongoClient

MONGODB_USERNAME = os.getenv('MONGODB_USERNAME')
MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD')
MONGODB_DB = os.getenv('MONGODB_DB')
MONGODB_SERVER = os.getenv('MONGODB_SERVER')

DB_URL = (
    "mongodb+srv://"
    + MONGODB_USERNAME
    + ":"
    + MONGODB_PASSWORD
    + "@"
    + MONGODB_SERVER
    + "/?retryWrites=true&w=majority"
)

client = MongoClient(
    DB_URL,
    tlsCAFile=certifi.where(),
)
db = client[MONGODB_DB]
funds_col = db.funds

def list_databases():
    """
    Obtains a list of databases from Atlas MongoDB
    Returns: List
    -------
    """
    return client.list_database_names()


def list_funds():
    funds_cursor = funds_col.find({})
    funds_list = []
    for fund in funds_cursor:
        funds_list.append(fund)
    return funds_list


def list_distinct_funds():
    funds_list = []
    for fund in funds_col.aggregate(
        [{"$group": {"_id": {"name": "$name", "url": "$url", "units": "$units"}}}]
    ):
        funds_list.append(fund)
    return funds_list

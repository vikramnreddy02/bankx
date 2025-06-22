from pymongo import MongoClient
from os import getenv

MONGO_URL = getenv("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client.analytics

def get_collection():
    return db.events

import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ["MONGODB_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]
COLLECTION_NAME = os.environ["COLLECTION_NAME"]

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
warehouse_collection = db[COLLECTION_NAME]
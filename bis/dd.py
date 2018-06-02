import os
mongoURI = "mongodb://"+os.environ["MONGOUSER"]+":"+os.environ["MONGOPASS"]+"@"+os.environ["MONGOSERVER"]+os.environ["MONGOPATH"]

def getDB(dbname):
    from pymongo import MongoClient
    client = MongoClient(mongoURI)
    return client[dbname]
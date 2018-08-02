

def getDB(dbname):
    import os
    from pymongo import MongoClient
    mongoURI = "mongodb://"+os.environ["DB_USERNAME"]+":"+os.environ["DB_PASSWORD"]+"@"+os.environ["MONGODB_SERVER"]+"/"+os.environ["DB_DATABASE"]
    client = MongoClient(mongoURI)
    return client[dbname]
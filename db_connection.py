import pymongo
import sys


if 'test' in sys.argv:
    url = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(url)
    db = client['snapple_test']
else:
    url = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(url)
    db = client['snapple']


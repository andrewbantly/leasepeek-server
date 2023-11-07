import pymongo
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if 'test' in sys.argv:
    logger.info("Using Test MongoDB")
    url = 'mongodb://mongo:27017'
    client = pymongo.MongoClient(url)
    db = client['snapple_test']
else:
    url = 'mongodb://mongo:27017'
    client = pymongo.MongoClient(url)
    db = client['snapple']


from pymongo import MongoClient
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_name = 'snapple_test' if 'test' in sys.argv else 'snapple'
url = 'mongodb://mongo:27017'

client = MongoClient(url)
db = client[db_name]

logger.info(f"Using MongoDB at {url} in database '{db_name}'")

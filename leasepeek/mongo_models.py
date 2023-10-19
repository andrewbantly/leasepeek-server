"""
Database Connection Module for leasepeek_backend Project.

This module establishes a connection to the MongoDB database and specifically targets the 'data' collection within the database. It leverages the connection settings defined in the `db_connection` module to interact with MongoDB.
"""

from db_connection import db

data_collection = db['data']

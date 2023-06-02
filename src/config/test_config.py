"""
The module defines the configuration used by the application when running tests.
By using these configurations we can set up a test environment with a mock MongoDB
client and appropriate database settings for testing our FastAPI application.
"""

import os
import logging
import sys
from mongomock_motor import AsyncMongoMockClient

#This variable retrieves the value of the "MONGODB_URL" environment variable, and if it is not
#defined, it defaults to "mongodb://user:aa@localhost:27017/". This allows you to specify the
#MongoDB connection URL for the test environment.
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://user:aa@localhost:27017/")
MONGODB_ENGINE = AsyncMongoMockClient()
MONGODB_DB = "college"
MONGODB_COLLECTION = "students"

LOG_CONFIG = {
    'name': 'fast-api-webapp-test',
    'level': logging.INFO,
    'format': '[%(asctime)s] [%(process)s] [%(levelname)s] %(message)s',
    'date_fmt': '%Y-%m-%d %H:%M:%S %z',
    'stream_handler': logging.StreamHandler(sys.stdout)
}

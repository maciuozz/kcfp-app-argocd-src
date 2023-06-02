"""
This module provides the configuration values needed to run the app
"""

import os
import logging
import sys


FASTAPI_CONFIG = {
    "port": 8081,
}

#We set the MONGODB_URL environment variable after the creation of the image when installing
#the Helm chart and pass it as a secret to the deployment. In the deployment we are using the
#envFrom field with a secretRef to include environment variables from a secret. The secret we
#defined includes the MONGODB_URL value generated using a template expression and encoded
#using base64. The Helm chart will create the secret and inject the environment variable into
#the container at deployment time. This allows us to configure the MONGODB_URL dynamically
#based on the environment or requirements.
MONGODB_URL = os.environ["MONGODB_URL"]
MONGODB_DB = "college"
MONGODB_COLLECTION = "students"

LOG_CONFIG = {
    'name': 'fast-api-webapp',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '[%(asctime)s] [%(process)s] [%(levelname)s] %(message)s',
    'date_fmt': '%Y-%m-%d %H:%M:%S %z',
}

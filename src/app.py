
"""
Module that sets up the necessary components, such as the MongoDB connection and the FastAPI server, and
starts the server while allowing it to run continuously. Additionally, it starts an HTTP server for
exposing Prometheus metrics.
"""

import asyncio
from prometheus_client import start_http_server
from motor.motor_asyncio import AsyncIOMotorClient
from application.app import StudentsServer
from config import config


class Container:
    """
    Class Container to configure the necessary methods to launch the application
    """

#MONGODB_DB is the name of the MongoDB database. The MONGODB_URL property from the configuration is used
#to create an instance of AsyncIOMotorClient, which connects to the MongoDB database. The client is then
#accessed using the _db_name attribute to obtain the specific database handler.An instance of the
#StudentsServer class is created, passing the config object and the MongoDB database handler (_db_handler)
#as parameters. This sets up the FastAPI server with the appropriate configuration and database connection.
    def __init__(self):
        self._db_name = config.MONGODB_DB
        self._db_handler = AsyncIOMotorClient(config.MONGODB_URL)[self._db_name]
        self._students_server = StudentsServer(config, self._db_handler)

    async def start_server(self):
        """Function to start the server"""
        await self._students_server.run_server()

#The start_http_server() function from the prometheus_client module is called with an argument of 8000, which
#starts a Prometheus metrics endpoint on port 8000. An instance of the Container class is created.
#The event loop is retrieved. The start_server method is scheduled as a future task.
#The event loop runs indefinitely.
if __name__ == "__main__":
    start_http_server(8000)
    container = Container()
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(container.start_server(), loop=loop)
    loop.run_forever()

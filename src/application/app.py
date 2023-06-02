"""
This module  defines a FastAPI application with 4 endpoints
"""

from typing import Optional
import logging
from fastapi import FastAPI, Body, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from prometheus_client import Counter
import requests

#The endpoint counters are used to collect metrics on the total number of requests received by each of these endpoints.
REQUESTS = Counter('server_requests_total', 'Total number of requests to this webserver')
HEALTHCHECK_REQUESTS = Counter('healthcheck_requests_total', 'Total number of requests to healthcheck')
MAIN_ENDPOINT_REQUESTS = Counter('main_requests_total', 'Total number of requests to main endpoint')
STUDENT_CREATE_REQUESTS = Counter('students_create_total', 'Total number of requests to the endpoint for create a student')
JOKE_ENDPOINT_REQUESTS = Counter('joke_requests_total', 'Total number of requests to joke endpoint')

#The PyObjectId class is defined, which extends the ObjectId class from the bson module. It validates whether a given
#ID is a valid ObjectId and provides a string representation of the ID.
class PyObjectId(ObjectId):
    """
    PyObjectId defines id of students
    """
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """Check if a student id is valid
        Parameters
        ----------
        cls: Type of id
        value: Value used to define id

        Returns
        -------
        Representation of id using ObjectId
        """
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid objectid")
        return ObjectId(value)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

#The StudentModel class is defined using Pydantic's BaseModel. It represents the attributes of a student and includes
#validation rules. The Config class inside StudentModel is used to configure MongoDB access and serialization
class StudentModel(BaseModel):
    """
    StudentModel defines student attributes used for creation
    """
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    course: str = Field(...)
    gpa: float = Field(..., le=4.0)

    class Config:
        """
        Configure access to MongoDB using StudentsModel class
        """
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }

#The UpdateStudentModel class is similar to StudentModel but includes optional fields to update student information.
class UpdateStudentModel(BaseModel):
    """
    UpdateStudentModel define attributes of students used to update
    """
    name: Optional[str]
    email: Optional[EmailStr]
    course: Optional[str]
    gpa: Optional[float]

    class Config:
        """
        Configure access to MongoDB using UpdateStudentModel class
        """
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }

#The FastAPI() function is called to create a new instance of the FastAPI application.
app = FastAPI()

#The StudentsServer is the main class that configures the FastAPI server and defines endpoint routes.
class StudentsServer:
    """
    StudentsServer class defines fastapi configuration using StudentsAction to access internal API
    """
    _hypercorn_config = None

#This is the constructor method of the class. It initializes the StudentsServer object and sets its
#configuration parameters, logger, and database handler.
    def __init__(self, config, db_handler):
        self._hypercorn_config = HyperCornConfig()
        self._config = config
        self._logger = self.__get_logger()
        self._db_handler = db_handler

#This method creates and configures a logger object for logging purposes. It sets the logger's level,
#formatter and handler based on the configuration provided.
    def __get_logger(self):
        logger = logging.getLogger(self._config.LOG_CONFIG['name'])
        logger.setLevel(self._config.LOG_CONFIG['level'])
        log_handler = self._config.LOG_CONFIG['stream_handler']
        log_formatter = logging.Formatter(
            fmt=self._config.LOG_CONFIG['format'],
            datefmt=self._config.LOG_CONFIG['date_fmt']
        )
        log_handler.setFormatter(log_formatter)
        logger.addHandler(log_handler)
        return logger

#This method uses the Hypercorn 'serve' function to start the server with the specified configuration parameters.
#Hypercorn server is being used to serve the FastAPI application that listens on port 8081.
#It keeps the connection alive for a specified timeout and adds the API routes.
    async def run_server(self):
        """Starts the server with the config parameters"""

        self._hypercorn_config.bind = [f'0.0.0.0:{self._config.FASTAPI_CONFIG["port"]}']
        self._hypercorn_config.keep_alive_timeout = 90
        self.add_routes()
        await serve(app, self._hypercorn_config)

#The add_routes method maps the endpoint routes to their respective methods using FastAPI's add_api_route function.
    def add_routes(self):
        """Maps the endpoint routes with their methods."""

        app.add_api_route(
            path="/health",
            endpoint=self.health_check,
            methods=["GET"]
        )

        app.add_api_route(
            path="/api/student",
            endpoint=self.create_student,
            summary="Add a new student",
            methods=["POST"],
            response_model=StudentModel,
            response_description="Create a new student",
        )

        app.add_api_route(
            path="/",
            endpoint=self.read_main,
            methods=["GET"]
        )

#Definition of endpoints.
    async def read_main(self):
        """Simple main endpoint"""
        self._logger.info("Main endpoint called")

        #Increase the counter used to record the overall number of requests made to the webserver.
        REQUESTS.inc()
        #Increase the counter used to record the requests made to the main endpoint
        MAIN_ENDPOINT_REQUESTS.inc()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"msg": "Hello World"})

    async def health_check(self):
        """Simple health check."""
        self._logger.info("Healthcheck endpoint called")

        REQUESTS.inc()
        HEALTHCHECK_REQUESTS.inc()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"health": "ok"})

    async def create_student(self, student: StudentModel = Body(...)):
        """Add a new student
        Parameters
        ----------
        student: Student representation
        Returns
        -------
        Response from the action layer
        """
        STUDENT_CREATE_REQUESTS.inc()
        REQUESTS.inc()

        student = jsonable_encoder(student)
        self._logger.debug('Trying to add student %s', student)
        new_student = await self._db_handler[self._config.MONGODB_COLLECTION].insert_one(student)
        created_student = await self._db_handler[self._config.MONGODB_COLLECTION].\
            find_one({"_id": new_student.inserted_id})
        self._logger.debug('Added student successfully with _id %s', new_student.inserted_id)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)

    @staticmethod
    @app.get("/joke")
    async def tell_joke():
        """Tell a joke"""
        REQUESTS.inc()
        JOKE_ENDPOINT_REQUESTS.inc()

        #Use requests library to get a random joke from an API.
        url = "https://official-joke-api.appspot.com/random_joke"
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": "Failed to get a joke"}

        joke = response.json()
        return {"setup": joke["setup"], "punchline": joke["punchline"]}

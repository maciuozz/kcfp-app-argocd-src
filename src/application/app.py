"""
This module  defines a FastAPI application with 4 endpoints
"""
from typing import Optional
import logging
import re
import requests
from pymongo import ReturnDocument
from fastapi import FastAPI, Body, status, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from hypercorn.asyncio import serve
from hypercorn.config import Config as HyperCornConfig
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from prometheus_client import Counter

#The endpoint counters are used to collect metrics on the total number of requests received by each of these endpoints.
REQUESTS = Counter('server_requests_total', 'Total number of requests to this webserver')
HEALTHCHECK_REQUESTS = Counter('healthcheck_requests_total', 'Total number of requests to healthcheck')
FREQUENCY_ANALYZER_REQUESTS = Counter('frequencies_requests_total', 'Total number of requests to frequencY_analyzer')
MAIN_ENDPOINT_REQUESTS = Counter('main_requests_total', 'Total number of requests to main endpoint')
STUDENT_CREATE_REQUESTS = Counter('students_create_total', 'Total number of requests to the endpoint to create a student')
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

root_endpoint_message = {"message": "Hello world will be updated automatically in private repository 10"}

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
            path="/",
            endpoint=self.read_main,
            methods=["GET"]
        )

        app.add_api_route(
            path="/analyze-text-file",
            endpoint=self.analyze_text_file,
            methods=["POST"]
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
            "/students/{student_id}/{field}/{value}",
            endpoint=self.update_student,
            methods=["PUT"]
        )

#Definition of endpoints.

    async def health_check(self):
        """Simple health check."""
        self._logger.info("Healthcheck endpoint called")

        # Increment counter used for register the total number of calls in the webserver
        REQUESTS.inc()
        # Increment counter used for register the requests to healtcheck endpoint
        HEALTHCHECK_REQUESTS.inc()
        return JSONResponse(status_code=status.HTTP_200_OK, content={"health": "ok"})

    async def read_main(self):
        """Simple main endpoint"""
        self._logger.info("Main endpoint called")

        #Increase the counter used to record the overall number of requests made to the webserver.
        REQUESTS.inc()
        #Increase the counter used to record the requests made to the main endpoint
        MAIN_ENDPOINT_REQUESTS.inc()
        return JSONResponse(status_code=status.HTTP_200_OK, content=root_endpoint_message)

    async def analyze_text_file(self, file: UploadFile = File(...)):
        """Frequencies analyzer"""
        self._logger.info("Frequency analyzer endpoint called")

        REQUESTS.inc()
        FREQUENCY_ANALYZER_REQUESTS.inc()

        # Read the contents of the uploaded text file
        file_content = await file.read()

        # Check if the file is empty
        if len(file_content) == 0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "Empty file"})

        # Convert file content to lowercase and split into words
        words = re.findall(r"\b[A-Za-z]+\b", file_content.decode().lower())

        # Check if there are no valid words in the file
        if len(words) == 0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"Error": "No valid words in file"})

        # Count word frequencies
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1

        # Calculate total number of words
        total_words = len(words)

        # Determine the word(s) with the highest frequency
        max_frequency = max(word_counts.values())
        most_frequent_words = [word for word, count in word_counts.items() if count == max_frequency]

        # Prepare the response JSON
        analysis_result = {
            "filename": file.filename,
            "total_words": total_words,
            "highest_frequency": max_frequency
        }

        # Check if all words have the same frequency
        if len(set(word_counts.values())) == 1:
            analysis_result["message"] = f"All words have the same frequency of {max_frequency}"
        else:
            analysis_result["most_frequent_words"] = most_frequent_words

        # Check if there is only one word in the file
        if len(words) == 1:
            analysis_result["message"] = "Only one word found in the file"

        # Return the analysis result as JSON response
        return JSONResponse(status_code=status.HTTP_200_OK, content=analysis_result)



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

    async def update_student(self, student_id: str, field: str, value: str):
        """Update a student's field based on their ID"""
        updated_student = await self._db_handler[self._config.MONGODB_COLLECTION].find_one_and_update(
            {"_id": ObjectId(student_id)},
            {"$set": {field: value}},
            return_document=ReturnDocument.AFTER
        )
        if updated_student:
            return JSONResponse(status_code=status.HTTP_200_OK, content=updated_student)

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"message": "Student not found"})

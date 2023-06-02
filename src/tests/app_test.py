"""
Module to test API endpoints using unit tests
"""

import json
import pytest
import httpx
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from application.app import StudentsServer, StudentModel, app
from config import test_config as config


client = TestClient(app)

class TestFastAPIApp:
    """
    Class define tests for testing FastAPI application
    """
    _valid_student_id = "62422b3329661ce0eab2066f"
    _valid_student_name = "Jane Doe"
    _valid_student_email = "jdoe@example.com"
    _valid_student_course = "Experiments, Science, and Fashion in Nanophotonics"
    _valid_student_gpa = 3.0
    _valid_student_data = {
        "_id": f"{_valid_student_id}",
        "name": f"{_valid_student_name}",
        "email": f"{_valid_student_email}",
        "course": f"{_valid_student_course}",
        "gpa": _valid_student_gpa,
    }
    _valid_student_data_mongo = StudentModel(
        id=_valid_student_id,
        name=_valid_student_name,
        email=_valid_student_email,
        course=_valid_student_course,
        gpa=_valid_student_gpa,
    )

    @pytest.mark.asyncio
    async def read_health_test(self):
        """Test the call to the root endpoint"""
        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        result = await students_server.health_check()
        result_data = json.loads(result.body.decode())

        assert result.status_code == 200
        assert result_data == {"health": "ok"}

    @pytest.mark.asyncio
    async def read_main_test(self):
        """Test the call to the root endpoint"""
        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        result = await students_server.read_main()
        result_data = json.loads(result.body.decode())

        assert result.status_code == 200
        assert result_data == {"msg": "Hello World"}

#In this method the database handler is mocked using AsyncMongoMockClient(). This allows the test to run
#without actually interacting with a real MongoDB database. Instead, the test uses a mock implementation
#of the MongoDB client that operates in memory.
#By mocking the database handler, the test can focus on verifying the behavior of the create_student method
#in isolation. It ensures that the method correctly handles the input data and produces the expected response
#without relying on an actual database connection. Using a mock database handler in unit tests allows for faster
#and more controlled testing, as it eliminates dependencies on external resources and provides a predictable
#environment for testing specific functionality.
    @pytest.mark.asyncio
    async def create_student_test(self):
        """Test the creation of a student"""
        #The db_handler variable is created by initializing an instance of AsyncMongoMockClient and accessing
        #the MongoDB database specified in the test configuration.
        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        #An instance of StudentsServer is created, passing the test configuration and the db_handler as arguments.
        students_server = StudentsServer(config, db_handler)
        #The create_student method of the students_server instance is called with self._valid_student_data_mongo
        #as the argument. This method is responsible to create a new student in the database.
        result = await students_server.create_student(self._valid_student_data_mongo)
        #The result variable holds the response received from the create_student method. This response contains
        #information such as the status code and the response body. The response body, which is in bytes, is
        #decoded into a string using result.body.decode(). The decoded response body string is parsed as JSON using
        #json.loads(), converting it into a Python object.
        result_data = json.loads(result.body.decode())
        #Assertions are performed to verify the expected behavior. In this case, it checks that the status code of
        #the response is 201 (indicating a successful creation), and the result_data matches the _valid_student_data
        #that was used to create the student.
        assert result.status_code == 201
        assert result_data == self._valid_student_data

    @pytest.mark.asyncio
    async def joke_endpoint_test(self):
        """Tests the joke endpoint"""
        async with httpx.AsyncClient(app=app, base_url="http://test") as async_client:
            response = await async_client.get("/joke")
        assert response.status_code == 200
        data = response.json()
        assert "setup" in data
        assert isinstance(data["setup"], str)
        assert "punchline" in data
        assert isinstance(data["punchline"], str)
        assert len(data["setup"]) > 0
        assert len(data["punchline"]) > 0

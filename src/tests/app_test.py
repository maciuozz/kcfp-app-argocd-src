"""
Module to test API endpoints using unit tests
"""

import json
import pytest
import httpx
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from application.app import StudentsServer, StudentModel, app, root_endpoint_message
from config import test_config as config


client = TestClient(app)

class TestFastAPIApp:
    """
    Class that defines tests for the FastAPI application
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
        """Tests the health check endpoint"""
        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        result = await students_server.health_check()
        result_data = json.loads(result.body.decode())

        assert result.status_code == 200
        assert result_data == {"health": "ok"}

    @pytest.mark.asyncio
    async def read_main_test(self):
        """Tests the root endpoint"""
        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        result = await students_server.read_main()
        result_data = json.loads(result.body.decode())

        assert result.status_code == 200
        assert result_data == root_endpoint_message

    @pytest.mark.asyncio
    async def analyze_text_file_test(self):
        """Tests the frequency analyzer endpoint"""

        db_handler = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler)

        # Create a mock UploadFile object
        class MockUploadFile:
            """A mock implementation of an upload file object for testing purposes"""
            def __init__(self, filename, content):
                self.filename = filename
                self.content = content

            async def read(self):
                """
                This method encodes the content of the mock upload file using the default encoding
                and returns it as bytes. It can be used to simulate reading the content of the file
                asynchronously.
                """
                return self.content.encode()

        # Define the test input and expected output
        test_input = MockUploadFile("test.txt", "This is a test file.")
        expected_output = {
            "filename": "test.txt",
            "total_words": 5,
            "highest_frequency": 1,
            "message": "All words have the same frequency of 1",
        }

        # Call the analyze_text_file endpoint
        result = await students_server.analyze_text_file(test_input)

        # Parse the response JSON
        result_data = json.loads(result.body.decode())

        # Perform assertions to verify the response
        assert result.status_code == 200
        assert result_data == expected_output

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

    @pytest.mark.asyncio
    async def update_student_test(self):
        """Tests the update_student endpoint"""

        # If we want to modify a student we need to create one first. The only one we are going to create is the
        # one defined using _valid_student_data_mongo and it will be the only one we can modify. That is why when
        # defining student_id we need to use the same id we used for the student in the TestFastAPIApp class above.
        student_id = "62422b3329661ce0eab2066f"
        field_name = "course"  # Example field name to update
        field_value = "Devops & Cloud Computing"  # Example new value for the field

        # Mock the database handler
        db_handler_mock = AsyncMongoMockClient()[config.MONGODB_DB]
        # Create the students_server instance using the mocked db_handler
        students_server = StudentsServer(config, db_handler_mock)

        # The create_student method of the students_server instance is called with self._valid_student_data_mongo
        # (defined above in the TestFastAPIApp class) as the argument. This creates a student record in the database
        # that we need in order to make the modification.
        await students_server.create_student(self._valid_student_data_mongo)

        # Call the update_student method. This updates the specified field of the student record.
        result = await students_server.update_student(student_id, field_name, field_value)

        # Verify the behavior.
        assert result.status_code == 200  # Assuming a successful update returns a 200 status code

        # Retrieve the updated student from the database. This represents the collection in the database
        # where the student records are stored.
        collection = db_handler_mock[config.MONGODB_COLLECTION]
        # The find_one method is called on the collection object with {"_id": student_id} as the filter. This
        # retrieves the updated student record from the database.
        updated_student = await collection.find_one({"_id": student_id})

        # Verify that the field value is updated. It's checking course == Devops & Cloud Computing.
        assert updated_student[field_name] == field_value

    @pytest.mark.asyncio
    async def get_all_students_test(self):
        """Tests the get_all_students endpoint"""

        # Set up dependencies
        db_handler_mock = AsyncMongoMockClient()[config.MONGODB_DB]
        students_server = StudentsServer(config, db_handler_mock)

        # Insert the student into the collection
        await students_server.create_student(self._valid_student_data_mongo)

        # Call the get_all_students method
        students=await students_server.get_all_students()

        assert isinstance(students, list)  # Check if the returned value is a list
        assert len(students) == 1  # Check if there is only one student in the returned list

        # Convert dictionaries (each student is a dictionary) to StudentModel objects.
        # In the line StudentModel(**student), **student is unpacking the student dictionary and passing its
        # key-value pairs as keyword arguments to the StudentModel constructor.
        # By using **student, we are essentially passing each key-value pair from the student dictionary as a separate
        # keyword argument to the StudentModel constructor. This allows the constructor to initialize the attributes of
        # the StudentModel object with the corresponding values from the dictionary.
        student_models = [StudentModel(**student) for student in students]

        # Verify the student fields
        assert student_models[0].id == self._valid_student_data_mongo.id
        assert student_models[0].name == self._valid_student_data_mongo.name
        assert student_models[0].email == self._valid_student_data_mongo.email
        assert student_models[0].course == self._valid_student_data_mongo.course
        assert student_models[0].gpa == self._valid_student_data_mongo.gpa

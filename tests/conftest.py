import json
import os

import pytest

from ytissues.ytlib import Project


class MockResponse:

    PROJECT = """
          {
            "shortName": "FIRST",
            "name": "First Project",
            "id": "0-1",
            "$type": "Project"
          }
        """

    PROJECT_LIST = """
        [
          {
            "shortName": "FIRST",
            "name": "First Project",
            "id": "0-1",
            "$type": "Project"
          },
          {
            "shortName": "SECOND",
            "name": "Second Project",
            "id": "0-2",
            "$type": "Project"
          },
          {
            "shortName": "THIRD",
            "name": "Third Project",
            "id": "0-3",
            "$type": "Project"
          },
          {
            "shortName": "FOURTH",
            "name": "Fourth Project",
            "id": "0-4",
            "$type": "Project"
          },
          {
            "shortName": "FIFTH",
            "name": "Fifth Project",
            "id": "0-5",
            "$type": "Project"
          }
        ]
    """

    ERROR_MESSAGE = """
        {
          "error": "Not Found",
          "error_description": "Entity with id {project_id} not found"
        }
        """

    @staticmethod
    def getcode():
        return 200


class MockResponseListOf5Projects(MockResponse):
    @staticmethod
    def read() -> str:
        return MockResponse.PROJECT_LIST


class MockResponseOneProject(MockResponse):
    @staticmethod
    def read() -> str:
        return MockResponse.PROJECT


class MockedResponseError(MockResponse):
    @staticmethod
    def read() -> str:
        return MockResponse.ERROR_MESSAGE


class MockedResponseServerError(MockResponse):
    @staticmethod
    def getcode():
        return 500


@pytest.fixture(autouse=True)
def set_environment():
    os.environ["YT_URL"] = "https://not.a.valid.host/to_test/youtrack"
    os.environ["YT_AUTH"] = "perm:not-a-valid-authorization"


@pytest.fixture
def list_5_projects():
    projects = []
    json_data = json.loads(MockResponse.PROJECT_LIST)
    for data in json_data:
        projects.append(
            Project(
                project_id=data["id"], shortname=data["shortName"], name=data["name"]
            )
        )
    return projects

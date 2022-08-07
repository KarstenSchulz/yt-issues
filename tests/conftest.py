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


class MockedIssueResponseEmpty:
    ISSUE_LIST = """[]"""
    STATUS_CODE = 200

    def getcode(self):
        return self.STATUS_CODE

    def read(self) -> str:
        return self.ISSUE_LIST


class MockedIssueResponseError(MockedIssueResponseEmpty):
    ISSUE_LIST = """{
  "error": "Not Found",
  "error_description": "Entity with id NOT_EXISTENT not found"
}"""
    STATUS_CODE = 404


class MockedIssueResponseFilledList(MockedIssueResponseEmpty):
    ISSUE_LIST = """
        [
          {
            "created": 1637587282538,
            "description": "Some explanations of the first issue.",
            "idReadable": "FIRST-1",
            "summary": "The title of the first issue",
            "updated": 1654071471241,
            "resolved": null,
            "id": "2-1",
            "commentsCount": 0,
            "$type": "Issue"
          },
          {
            "created": 1637000282583,
            "description": "Some explanations of the second issue.",
            "idReadable": "FIRST-2",
            "summary": "The title of the second issue",
            "updated": 1654072471241,
            "resolved": null,
            "id": "2-2",
            "commentsCount": 1,
            "$type": "Issue"
          },
          {
            "created": 1637460000000,
            "description": "Some explanations of the third issue.",
            "idReadable": "FIRST-3",
            "summary": "The title of the third issue",
            "updated": 1637990000000,
            "resolved": 1637990000000,
            "id": "2-3",
            "commentsCount": 42,
            "$type": "Issue"
          }
        ]
    """


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


@pytest.fixture
def project_0_1() -> Project:
    return Project(project_id="0-1", shortname="PROJEKT_0_1", name="Projekt 0-1")


@pytest.fixture
def empty_issue_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedIssueResponseEmpty()

    return mocked_urlopen


@pytest.fixture
def filled_issue_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedIssueResponseFilledList()

    return mocked_urlopen


@pytest.fixture
def error_issue_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedIssueResponseError()

    return mocked_urlopen

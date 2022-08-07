import json
import os
from datetime import datetime

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


@pytest.fixture
def project_0_1() -> Project:
    return Project(project_id="0-1", shortname="PROJEKT_0_1", name="Projekt 0-1")


class MockedIssueResponseEmpty:
    ISSUELIST = """[]"""

    @staticmethod
    def getcode():
        return 200

    @staticmethod
    def read() -> str:
        return MockedIssueResponseEmpty.ISSUELIST


class MockedIssueResponse:
    EMPTY_ISSUELIST = """[]"""

    ISSUE_ID_LIST = """
        [
          {
            "id": "2-1",
            "$type": "Issue"
          },
          {
            "id": "2-2",
            "$type": "Issue"
          },
          {
            "id": "2-3",
            "$type": "Issue"
          }
        ]
    """

    time_stamps = {
        "FIRST-1": {
            "created": datetime(2021, 11, 22, 14, 21, 22, 538000),
            "updated": datetime(2022, 6, 1, 10, 17, 51, 241000),
            "resolved": None,
        },
        "FIRST-2": {
            "created": datetime(2021, 11, 15, 19, 18, 2, 583000),
            "updated": datetime(2022, 6, 1, 10, 34, 31, 241000),
            "resolved": None,
        },
        "FIRST-3": {
            "created": datetime(2021, 11, 21, 3, 0),
            "updated": datetime(2021, 11, 27, 6, 13, 20),
            "resolved": datetime(2021, 11, 27, 6, 13, 20),
        },
    }

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

    ERROR_MESSAGE = """
        {
          "error": "Not Found",
          "error_description": "Entity with id {project_id} not found"
        }
        """

    @staticmethod
    def getcode():
        return 200


class MockedIssueList(MockedIssueResponse):
    @staticmethod
    def read() -> str:
        return MockedIssueList.ISSUE_LIST


@pytest.fixture
def mock_urlopen():
    def mocked_urlopen(*args, **kwargs):
        return MockedIssueList()

    return mocked_urlopen


@pytest.fixture
def empty_issue_list(*args, **kwargs):
    def mocked_urlopen(*args, **kwargs):
        return MockedIssueResponseEmpty()

    return mocked_urlopen

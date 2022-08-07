import os
from urllib import request

import pytest

from ytissues.ytlib import Project, get_projects


@pytest.fixture
def yt_url():
    return os.environ["YT_URL"]


@pytest.fixture
def yt_auth():
    return os.environ["YT_AUTH"]


class MockedResponse:
    RESPONSE = ""
    STATUS_CODE = 500

    def getcode(self):
        return self.STATUS_CODE

    def read(self) -> str:
        return self.RESPONSE


class MockedResponseError(MockedResponse):
    RESPONSE = """{
  "error": "Not Found",
  "error_description": "Entity with id NOT_EXISTENT not found"
}"""
    STATUS_CODE = 404


class MockedResponseEmpty(MockedResponse):
    RESPONSE = """[]"""
    STATUS_CODE = 200


class MockedProjectResponseOneProjectList(MockedResponse):
    RESPONSE = """
             {
               "shortName": "FIRST",
               "name": "First Project",
               "id": "0-1",
               "$type": "Project"
             }
           """
    STATUS_CODE = 200


class MockedProjectResponseFilledList(MockedResponse):
    RESPONSE = """
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
    STATUS_CODE = 200


class MockedIssueResponseOneIssueList(MockedResponse):
    RESPONSE = """[
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
      }
]"""
    STATUS_CODE = 200


class MockedIssueResponseFilledList(MockedResponse):
    RESPONSE = """
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

    STATUS_CODE = 200


@pytest.fixture(autouse=True)
def set_environment():
    os.environ["YT_URL"] = "https://not.a.valid.host/to_test/youtrack"
    os.environ["YT_AUTH"] = "perm:not-a-valid-authorization"


@pytest.fixture
def one_project() -> Project:
    return Project(project_id="0-1", shortname="PROJEKT_0_1", name="Projekt 0-1")


@pytest.fixture
def filled_project_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedProjectResponseFilledList()

    return mocked_urlopen


@pytest.fixture
def one_project_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedProjectResponseOneProjectList()

    return mocked_urlopen


@pytest.fixture
def empty_issue_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedResponseEmpty()

    return mocked_urlopen


@pytest.fixture
def one_issue_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedIssueResponseOneIssueList()

    return mocked_urlopen


@pytest.fixture
def filled_issue_list():
    def mocked_urlopen(*args, **kwargs):
        return MockedIssueResponseFilledList()

    return mocked_urlopen


@pytest.fixture
def error_response():
    def mocked_urlopen(*args, **kwargs):
        return MockedResponseError()

    return mocked_urlopen


@pytest.fixture
def list_5_projects(monkeypatch, filled_project_list):
    monkeypatch.setattr(request, "urlopen", filled_project_list)
    return get_projects()

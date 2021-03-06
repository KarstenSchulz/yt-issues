"""Test Issue class."""
from datetime import datetime
from urllib import request

import pytest

from ytissues.ytlib import Issue, Project


@pytest.fixture
def project_0_1() -> Project:
    return Project(project_id="0-1", shortname="PROJEKT_0_1", name="Projekt 0-1")


class MockIssueResponse:
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


class MockIssueList(MockIssueResponse):
    @staticmethod
    def read() -> str:
        return MockIssueList.ISSUE_LIST


class MockIssueError(MockIssueResponse):
    @staticmethod
    def read() -> str:
        return MockIssueList.ERROR_MESSAGE


# noinspection PyUnusedLocal
class TestIssueStructure:
    def test_issue_init(self):
        assert Issue(issue_id="", project_id="")

    def test_issue_list(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        assert len(project_0_1.issues) == 3

    def test_issue_has_id(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        assert project_0_1.issues[0].issue_id == "2-1"
        assert project_0_1.issues[1].issue_id == "2-2"
        assert project_0_1.issues[2].issue_id == "2-3"

    def test_first_issue_is_type_issue(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        assert isinstance(project_0_1.issues[0], Issue)

    def test_issues_have_ids(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        for i in range(0, 3):
            assert project_0_1.issues[i].issue_id == f"2-{i + 1}"

    def test_get_issues_list_len_is_correct(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        assert len(project_0_1.issues) == 3

    def test_get_issue_has_correct_data(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        for number, issue in enumerate(project_0_1.issues, start=1):
            assert issue.issue_id == f"2-{number}"
            assert issue.id_readable == f"FIRST-{number}"
            assert issue.project_id == "0-1"

    def test_has_timestamps(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        tstamp = MockIssueResponse.time_stamps
        for issue in project_0_1.issues:
            assert issue.created == tstamp[issue.id_readable]["created"]
            assert issue.updated == tstamp[issue.id_readable]["updated"]
            assert issue.resolved == tstamp[issue.id_readable]["resolved"]

    def test_has_summary_and_description(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        for number, issue in zip(("first", "second", "third"), project_0_1.issues):
            assert issue.description == f"Some explanations of the {number} issue."
            assert issue.summary.endswith(f"The title of the {number} issue")

    def test_has_comments_count(self, monkeypatch, project_0_1):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        for number, issue in zip((0, 1, 42), project_0_1.issues):
            assert issue.comments_count == number

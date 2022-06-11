"""Test request objects, urls and mocked API calls."""
import os
from urllib import request

import pytest

from ytissues.ytlib import Project, get_projects, get_request


class MockResponse:
    project_list_api = """
    [
  {
    "shortName": "BD",
    "name": "bd",
    "id": "0-16",
    "$type": "Project"
  },
  {
    "shortName": "COM",
    "name": "com",
    "id": "0-6",
    "$type": "Project"
  },
  {
    "shortName": "CPP",
    "name": "cpp",
    "id": "0-9",
    "$type": "Project"
  },
  {
    "shortName": "DENTA",
    "name": "denta",
    "id": "0-11",
    "$type": "Project"
  },
  {
    "shortName": "DSHELP",
    "name": "dshelp",
    "id": "0-2",
    "$type": "Project"
  },
  {
    "shortName": "DTG",
    "name": "dtg",
    "id": "0-12",
    "$type": "Project"
  },
  {
    "shortName": "EHRUK",
    "name": "ehruk",
    "id": "0-14",
    "$type": "Project"
  },
  {
    "shortName": "GAMBIT",
    "name": "gambit",
    "id": "0-18",
    "$type": "Project"
  },
  {
    "shortName": "HASE",
    "name": "hase",
    "id": "0-10",
    "$type": "Project"
  },
  {
    "shortName": "PFEFFER",
    "name": "pfeffer",
    "id": "0-13",
    "$type": "Project"
  },
  {
    "shortName": "KS",
    "name": "ks",
    "id": "0-3",
    "$type": "Project"
  },
  {
    "shortName": "NORTH",
    "name": "north",
    "id": "0-15",
    "$type": "Project"
  }
]
"""

    @staticmethod
    def read():
        return MockResponse.project_list_api

    @staticmethod
    def getcode():
        return 200


class TestGetProjects:
    def test_test_environment_is_set(self):
        assert os.environ["YT_URL"] == "https://not.a.valid.host/to_test/youtrack"
        assert os.environ["YT_AUTH"] == "perm:not-a-valid-authorization"

    @pytest.fixture
    def yt_url(self):
        return os.environ["YT_URL"]

    @pytest.fixture
    def yt_auth(self):
        return os.environ["YT_AUTH"]

    def test_get_request_raises_missing_slash(self, yt_url, yt_auth):
        with pytest.raises(ValueError):
            get_request("resource", "query")

    def test_get_request_raises_question_mark(self, yt_url, yt_auth):
        with pytest.raises(ValueError):
            get_request("/resource", "?query")

    def test_get_request_correct_url(self, yt_url, yt_auth):
        the_request = get_request("/resource", "query")
        assert the_request.full_url == f"{yt_url}/resource?query"

    def test_get_projects(self, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockResponse()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        projects = get_projects()
        p1 = Project(project_id="0-16", shortname="BD", name="bd")
        assert p1 == projects[0]
        p2 = Project(project_id="0-15", shortname="NORTH", name="north")
        assert p2 == projects[11]

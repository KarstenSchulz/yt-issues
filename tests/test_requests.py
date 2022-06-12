"""Test request objects, urls and mocked API calls."""
import os
from urllib import request

import pytest

from tests.conftest import MockedResponseEmptyProjectList, MockResponseWithProjects
from ytissues.ytlib import get_projects, get_request


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
            return MockResponseWithProjects()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        projects = get_projects()
        assert projects[0].project_id == "0-16"
        assert projects[0].shortname == "BD"
        assert projects[0].name == "bd"
        assert projects[1].project_id == "0-6"
        assert projects[1].shortname == "COM"
        assert projects[1].name == "com"

    def test_get_projects_list_len_is_correct(self, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockResponseWithProjects()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        projects = get_projects()
        assert len(projects) == 12

    def test_get_empty_project_list_succeeds(self, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockedResponseEmptyProjectList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        projects = get_projects()
        assert isinstance(projects, list)
        assert len(projects) == 0

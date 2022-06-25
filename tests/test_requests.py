"""Test request objects, urls and mocked API calls."""
import os
from urllib import request

import pytest

from tests.conftest import (
    MockedResponseError,
    MockedResponseServerError,
    MockResponseListOf5Projects,
    MockResponseOneProject,
)
from ytissues.ytlib import get_projects, get_request


# noinspection PyUnusedLocal
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
        the_request = get_request("/resource", "fields=test")
        assert the_request.full_url == f"{yt_url}/resource?fields=test"

    def test_get_full_projects_list_len_is_correct(self, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockResponseListOf5Projects()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        projects = get_projects()
        assert len(projects) == 5

    def test_get_one_project_succeeds(self, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockResponseOneProject()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        projects = get_projects(project_id="0-1")
        assert isinstance(projects, list)
        assert len(projects) == 1

    def test_wrong_project_gets_error(self, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockedResponseError()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        projects = get_projects(project_id="NOT_EXISTENT")
        assert projects == []

    def test_server_error_raises(self, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockedResponseServerError()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        with pytest.raises(IOError):
            _ = get_projects(project_id="raises Server Error")

    def test_get_request_request_is_well_formed(self):
        with pytest.raises(ValueError):
            _ = get_request("please_no_trailing_slash/", "")
        with pytest.raises(ValueError):
            _ = get_request("please_start_with_slash", "")
        with pytest.raises(ValueError):
            _ = get_request("/please_do_not_start_query_with_?", "?_is_wrong")

    def test_get_request_combines_query(self):
        r = get_request("/path", "fields=the_query")
        assert r.full_url == f"{os.environ['YT_URL']}/path?fields=the_query"

    def test_get_request_works_with_empty_query(self):
        r = get_request("/path", "")
        assert r.full_url == f"{os.environ['YT_URL']}/path"

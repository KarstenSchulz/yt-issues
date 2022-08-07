"""Test request objects, urls and mocked API calls."""
import os
from urllib import request

import pytest

from ytissues.ytlib import get_projects, get_request


def test_test_environment_is_set():
    assert os.environ["YT_URL"] == "https://not.a.valid.host/to_test/youtrack"
    assert os.environ["YT_AUTH"] == "perm:not-a-valid-authorization"


def test_get_request_raises_missing_slash(yt_url, yt_auth):
    with pytest.raises(ValueError):
        get_request("resource", "query")


def test_get_request_raises_question_mark(yt_url, yt_auth):
    with pytest.raises(ValueError):
        get_request("/resource", "?query")


def test_get_request_correct_url(yt_url, yt_auth):
    the_request = get_request("/resource", "fields=test")
    assert the_request.full_url == f"{yt_url}/resource?fields=test"


# noinspection PyUnusedLocal
class TestGetProjects:
    def test_get_full_projects_list_len_is_correct(
        self, monkeypatch, filled_project_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_project_list)
        projects = get_projects()
        assert len(projects) == 5

    def test_get_one_project_succeeds(self, monkeypatch, one_project_list):
        monkeypatch.setattr(request, "urlopen", one_project_list)
        projects = get_projects(project_id="0-1")
        assert isinstance(projects, list)
        assert len(projects) == 1

    def test_wrong_project_gets_error(self, monkeypatch, error_response):
        monkeypatch.setattr(request, "urlopen", error_response)
        with pytest.raises(IOError):
            _ = get_projects(project_id="NOT_EXISTENT")

    def test_server_error_raises(self, monkeypatch, error_response):
        monkeypatch.setattr(request, "urlopen", error_response)
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

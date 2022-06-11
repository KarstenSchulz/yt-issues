"""Test request objects, urls and mocked API calls."""
import os

import pytest

from ytissues.ytlib import get_request

project_list_api = [
    {"shortName": "AB", "name": "ab", "id": "0-16", "$type": "Project"},
    {"shortName": "BC", "name": "bc", "id": "0-6", "$type": "Project"},
    {"shortName": "CCP", "name": "ccp", "id": "0-9", "$type": "Project"},
    {"shortName": "DEPIWE", "name": "depiwe", "id": "0-11", "$type": "Project"},
    {"shortName": "DJANGO", "name": "django", "id": "0-2", "$type": "Project"},
    {"shortName": "DENTA", "name": "denta", "id": "0-12", "$type": "Project"},
    {"shortName": "EHRN", "name": "ehrn", "id": "0-14", "$type": "Project"},
    {"shortName": "GOUDA", "name": "gouda", "id": "0-18", "$type": "Project"},
    {"shortName": "HASE", "name": "hase", "id": "0-10", "$type": "Project"},
    {"shortName": "JECKYLL", "name": "jeckyll", "id": "0-13", "$type": "Project"},
    {"shortName": "KS", "name": "ks", "id": "0-3", "$type": "Project"},
    {"shortName": "NORTH", "name": "north", "id": "0-15", "$type": "Project"},
]


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
        request = get_request("/resource", "query")
        assert request.full_url == f"{yt_url}/resource?query"

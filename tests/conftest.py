import os

import pytest

from ytissues.ytlib import Project


@pytest.fixture(autouse=True)
def set_environment():
    os.environ["YT_URL"] = "https://not.a.valid.host/to_test/youtrack"
    os.environ["YT_AUTH"] = "perm:not-a-valid-authorization"


class MockResponseWithProjects:
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
        return MockResponseWithProjects.project_list_api

    @staticmethod
    def getcode():
        return 200


class MockedResponseEmptyProjectList:
    @staticmethod
    def read():
        return "[]"

    @staticmethod
    def getcode():
        return 200


@pytest.fixture
def list_0_projects():
    return []


@pytest.fixture
def list_empty_str_projects():
    return [""]


@pytest.fixture
def list_1_projects():
    return [Project("0-1", "FIRST", "First Project")]


@pytest.fixture
def list_5_projects():
    projects = []
    for init_data in [
        ("0-1", "FIRST", "First Project"),
        ("0-2", "SECOND", "Second Project"),
        ("0-3", "THIRD", "Third Project"),
        ("0-4", "FORCE", "Yedi Project"),
        ("0-5", "SITH", "Evil Project"),
    ]:
        projects.append(Project(*init_data))
    return projects

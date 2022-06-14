"""
Test Project and Issues classes
"""
from urllib import request

import pytest

from tests.test_issues import MockIssueList
from ytissues.ytlib import Issue, Project, print_as_list, print_as_table, print_projects


class TestProjectDisplaynames:
    data_displaynames = [
        (
            {"project_id": "P_ID", "shortname": "", "name": ""},
            {"name": "P_ID", "plaintext": "P_ID None None"},
        ),
        (
            {"project_id": "P_ID", "shortname": "S_NAME", "name": "NAME"},
            {"name": "S_NAME", "plaintext": "P_ID S_NAME NAME"},
        ),
        (
            {"project_id": "P_ID", "shortname": "", "name": "NAME"},
            {"name": "NAME", "plaintext": "P_ID None NAME"},
        ),
        (
            {"project_id": "", "shortname": "S_NAME", "name": "NAME"},
            {"name": "S_NAME", "plaintext": "None S_NAME NAME"},
        ),
    ]

    @pytest.mark.parametrize("init, result", data_displaynames)
    def test_displayname_text(self, init, result):
        p = Project(**init)
        assert p.displayname == result["name"]

    @pytest.mark.parametrize("init, result", data_displaynames)
    def test_as_plaintext(self, init, result):
        p = Project(**init)
        assert p.as_plaintext() == result["plaintext"]


class TestProject:
    def test_plain_text(self):
        p = Project("P_ID")
        assert p.as_plaintext() == "P_ID None None"
        assert p.displayname == "P_ID"

    def test_displayname(self):
        p = Project("0-1")
        assert p.displayname == "0-1"
        assert str(p) == "0-1"
        p = Project("0-1", "ShortName")
        assert p.displayname == "ShortName"
        assert str(p) == "ShortName"
        p = Project("0-1", "ShortName")
        assert p.displayname == "ShortName"
        assert str(p) == "ShortName"
        p = Project("0-1", "ShortName", "Name")
        assert p.displayname == "ShortName"
        assert str(p) == "ShortName"

    def test_equality(self):
        p1 = Project("0-1")
        p2 = Project("0-1")
        p3 = Project("1-99")
        assert p1 == p2
        assert p1 != p3

    def test_project_print(self, capfd):
        p1 = Project("0-1")
        p1.print()
        out, err = capfd.readouterr()
        assert out == "0-1 None None\n"

    def test_print_as_list(self, list_5_projects, capfd):
        print_as_list(list_5_projects)
        out, err = capfd.readouterr()
        for i in range(0, 5):
            assert list_5_projects[i].displayname in out
        assert err == ""

    def test_print_as_table(self, list_5_projects, capfd):
        print_as_table(list_5_projects)
        out, err = capfd.readouterr()
        for i in range(0, 5):
            assert list_5_projects[i].displayname in out
        assert err == ""

    def test_list_projects_as_list(self, list_5_projects, capfd):
        print_projects(list_5_projects)
        out, err = capfd.readouterr()
        for i in range(0, 5):
            assert list_5_projects[i].displayname in out
        assert err == ""

    def test_list_projects_as_table(self, list_5_projects, capfd):
        print_projects(list_5_projects, as_table=True)
        out, err = capfd.readouterr()
        for i in range(0, 5):
            assert list_5_projects[i].displayname in out
        assert err == ""


class TestProjectDetails:
    @pytest.fixture
    def project1(self):
        return Project("0-1", "FIRST", "First Project")

    def test_get_list_of_issues(self, project1, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        assert isinstance(project1.issues, list)

    def test_type_of_first_issue(self, project1, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        assert isinstance(project1.issues[0], Issue)

    def test_loads_list_of_issues(self, project1, monkeypatch):
        def mock_urlopen(*args, **kwargs):
            return MockIssueList()

        monkeypatch.setattr(request, "urlopen", mock_urlopen)
        assert len(project1.issues) == 3

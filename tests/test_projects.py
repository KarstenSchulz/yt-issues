"""
Test Project and Issues classes
"""
from urllib import request

import pytest

from ytissues.cli import print_as_list, print_as_table, print_projects
from ytissues.ytlib import Issue, Project


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
            {"project_id": None, "shortname": "S_NAME", "name": "NAME"},
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

    def test_verbose_as_plaintext(self, monkeypatch):
        monkeypatch.setattr(Project, "issues", ["issue1", "issue2"])
        p = Project(project_id="P_ID")
        assert p.as_plaintext(verbose=True) == "P_ID None None 2 issues"


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

    def test_eq_with_none(self):
        p1 = Project("0-1")
        p2 = None
        assert p1 != p2

    def test_project_print(self, capfd):
        p1 = Project("0-1")
        print(p1.as_plaintext())
        out, err = capfd.readouterr()
        assert out == "0-1 None None\n"

    def test_print_as_list(self, list_5_projects, capfd):
        print_as_list(list_5_projects, verbose=False)
        out, err = capfd.readouterr()
        for i in range(0, 5):
            assert list_5_projects[i].displayname in out
        assert err == ""

    def test_print_as_table(self, list_5_projects, capfd):
        print_as_table(list_5_projects, verbose=False)
        out, err = capfd.readouterr()
        for i in range(0, 5):
            assert list_5_projects[i].displayname in out
            assert "Issues" not in out
        assert err == ""

    def test_print_as_table_verbose(self, list_5_projects, monkeypatch, capfd):
        monkeypatch.setattr(Project, "issues", ["issue1", "issue2"])
        print_as_table(list_5_projects, verbose=True)
        out, err = capfd.readouterr()
        for i in range(0, 5):
            assert list_5_projects[i].displayname in out
            assert "Issues" in out
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


# noinspection PyUnusedLocal
class TestProjectDetails:
    def test_get_list_of_issues(self, project_0_1, monkeypatch, filled_issue_list):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        assert isinstance(project_0_1.issues, list)

    def test_loads_empty_list_of_issues(
        self, project_0_1, monkeypatch, empty_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", empty_issue_list)
        assert project_0_1.issues == []

    def test_loads_one_issue_list(self, monkeypatch, project_0_1, one_issue_list):
        monkeypatch.setattr(request, "urlopen", one_issue_list)
        assert len(project_0_1.issues) == 1

    def test_type_of_first_issue(self, project_0_1, monkeypatch, filled_issue_list):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        assert isinstance(project_0_1.issues[0], Issue)

    def test_loads_issue_list(self, monkeypatch, project_0_1, filled_issue_list):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        assert len(project_0_1.issues) == 3

    def test_raises_if_response_error(self, monkeypatch, project_0_1, error_response):
        monkeypatch.setattr(request, "urlopen", error_response)
        with pytest.raises(IOError):
            assert len(project_0_1.issues) == 3

    def test_print_details_as_table(
        self, project_0_1, monkeypatch, capfd, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        project_0_1.print_details(as_table=True, verbose=False)
        out, err = capfd.readouterr()
        assert "ID" in out
        assert "Comments" not in out  # only if verbose
        assert "Summary" in out
        assert "third issue" in out
        assert err == ""

    def test_print_details_as_table_verbose(
        self, project_0_1, monkeypatch, capfd, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        project_0_1.print_details(as_table=True, verbose=True)
        out, err = capfd.readouterr()
        assert "Comments" in out
        assert err == ""

    def test_print_details_as_csv(
        self, project_0_1, monkeypatch, capfd, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        project_0_1.print_details(as_table=False, verbose=False)
        out, err = capfd.readouterr()
        assert "Issue ID;Created;Last Update;Resolved;Summary" in out
        assert "Comments" not in out
        assert err == ""

    def test_print_details_as_csv_verbose(
        self, project_0_1, monkeypatch, capfd, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        project_0_1.print_details(as_table=False, verbose=True)
        out, err = capfd.readouterr()
        assert "Comments" in out
        assert "42" in out
        assert err == ""

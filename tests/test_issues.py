"""Test Issue class."""
from datetime import datetime
from urllib import request

from ytissues.ytlib import Issue, get_issue_data


# noinspection PyUnusedLocal
class TestIssueStructure:
    def test_issue_init(self):
        assert Issue(issue_id="", project_id="")

    def test_issue_has_id(self, monkeypatch, project_0_1, filled_issue_list):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        assert project_0_1.issues[0].issue_id == "2-1"
        assert project_0_1.issues[1].issue_id == "2-2"
        assert project_0_1.issues[2].issue_id == "2-3"

    def test_first_issue_is_type_issue(
        self, monkeypatch, project_0_1, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        assert isinstance(project_0_1.issues[0], Issue)

    def test_issues_have_ids(self, monkeypatch, project_0_1, filled_issue_list):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        for i in range(0, 3):
            assert project_0_1.issues[i].issue_id == f"2-{i + 1}"

    def test_get_issues_list_len_is_correct(
        self, monkeypatch, project_0_1, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        assert len(project_0_1.issues) == 3

    def test_get_issue_has_correct_data(
        self, monkeypatch, project_0_1, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        for number, issue in enumerate(project_0_1.issues, start=1):
            assert issue.issue_id == f"2-{number}"
            assert issue.id_readable == f"FIRST-{number}"
            assert issue.project_id == "0-1"

    def test_has_timestamps(self, monkeypatch, project_0_1, filled_issue_list):
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

        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        for issue in project_0_1.issues:
            assert issue.created == time_stamps[issue.id_readable]["created"]
            assert issue.updated == time_stamps[issue.id_readable]["updated"]
            assert issue.resolved == time_stamps[issue.id_readable]["resolved"]

    def test_has_summary_and_description(
        self, monkeypatch, project_0_1, filled_issue_list
    ):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        for number, issue in zip(("first", "second", "third"), project_0_1.issues):
            assert issue.description == f"Some explanations of the {number} issue."
            assert issue.summary.endswith(f"The title of the {number} issue")

    def test_has_comments_count(self, monkeypatch, project_0_1, filled_issue_list):
        monkeypatch.setattr(request, "urlopen", filled_issue_list)
        for number, issue in zip((0, 1, 42), project_0_1.issues):
            assert issue.comments_count == number


def test_issue_as_csv():
    a_summary = "An issue to test."
    issue = Issue(
        issue_id="2-1",
        project_id="FIRST-1",
        id_readable="ISSUE-2-1",
        created=datetime(2022, 1, 1, 0, 0, 0),
        updated=datetime(2022, 1, 2, 0, 0, 0),
        resolved=datetime(2022, 1, 3, 0, 0, 0),
        summary=a_summary,
        comments_count=2,
    )
    summary = issue.create_summary(a_summary)
    csv = ["2-1", "2022-01-01 00:00", "2022-01-02 00:00", "Yes", summary]
    assert csv == get_issue_data(issue, verbose=False)


def test_issue_as_csv_verbose():
    a_summary = "An issue to test."
    issue = Issue(
        issue_id="2-1",
        project_id="FIRST-1",
        id_readable="ISSUE-2-1",
        created=datetime(2022, 1, 1, 0, 0, 0),
        updated=datetime(2022, 1, 2, 0, 0, 0),
        resolved=datetime(2022, 1, 3, 0, 0, 0),
        summary=a_summary,
        comments_count=2,
    )
    summary = issue.create_summary(a_summary)
    csv = [
        "2-1",
        "ISSUE-2-1",
        "2022-01-01 00:00",
        "2022-01-02 00:00",
        "Yes",
        summary,
        "2",
    ]
    assert csv == get_issue_data(issue, verbose=True)

"""Test User API (command line interface)."""
from unittest.mock import Mock, patch

from ytissues import cli
from ytissues.cli import parse_arguments
from ytissues.ytlib import trim_filename, trim_pathname


def test_backup_command_respects_project_id():
    args = parse_arguments(["backup", "-i", "0-1", "backup_dir"])
    assert args.project_id == "0-1"
    assert args.backup_dir == "backup_dir"


@patch("ytissues.cli.Project", autospec=True)
@patch("ytissues.cli.get_project")
def test_single_project_backup(mock_get_project, mock_project):
    mock_get_project.return_value = mock_project
    args = parse_arguments(["backup", "-i", "0-1", "backup_dir"])
    cli.backup(args)
    mock_get_project.assert_called_once_with(args.project_id)
    mock_project.backup.assert_called_once_with(args.backup_dir)


@patch("ytissues.cli.Project", autospec=True)
@patch("ytissues.cli.get_projects")
def test_all_project_backup(mock_get_projects, mock_project):
    p1, p2, p3 = Mock(), Mock(), Mock()
    mock_get_projects.return_value = [p1, p2, p3]
    args = parse_arguments(["backup", "backup_dir"])
    cli.backup(args)
    mock_get_projects.assert_called_once()
    p1.backup.assert_called_once_with(args.backup_dir)
    p2.backup.assert_called_once_with(args.backup_dir)
    p3.backup.assert_called_once_with(args.backup_dir)


def test_ls_lists_projects_as_list():
    args = parse_arguments(["ls"])
    assert args.project_id is None
    assert args.table is False


def test_ls_lists_one_project_as_list():
    args = parse_arguments(["ls", "-i", "0-1"])
    assert args.project_id == "0-1"
    assert args.table is False


def test_ls_lists_projects_as_table():
    args = parse_arguments(["ls", "-t"])
    assert args.project_id is None
    assert args.table is True


def test_ls_lists_one_project_as_table():
    args = parse_arguments(["ls", "-t", "-i", "0-1"])
    assert args.project_id == "0-1"
    assert args.table is True


def test_trim_filename_function():
    for source, converted in [
        ("ABCabc", "ABCabc"),
        ("ABC   abc", "ABC abc"),
        ("A:B", "A B"),
        ("A/B", "A B"),
        ("A>B", "A B"),
        ("A<B", "A B"),
        ("A\\B", "A B"),
        ("A:/?>>B", "A ? B"),
        ("A_/_B", "A_ _B"),
    ]:
        assert trim_filename(source) == converted


def test_trim_pathname_function():
    for source, converted in [
        ("A/B", "A/B"),
        ("A:/?>>B", "A /? B"),
        ("A_/_B", "A_/_B"),
    ]:
        assert trim_pathname(source) == converted

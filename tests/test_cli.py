"""Test User API (command line interface)."""
from pathlib import Path

from ytissues.ytlib import parse_arguments, trim_filename, trim_pathname


def test_backup_command_respects_project_id():
    args = parse_arguments(["backup", "-i", "0-1", "backup_dir"])
    assert args.project_id == "0-1"
    assert args.backup_dir == "backup_dir"


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
        assert trim_filename(source) == Path(converted)


def test_trim_pathname_function():
    for source, converted in [
        ("A/B", "A/B"),
        ("A:/?>>B", "A /? B"),
        ("A_/_B", "A_/_B"),
    ]:
        assert trim_pathname(source) == Path(converted)

import argparse
import sys

from rich import box
from rich.console import Console
from rich.progress import track
from rich.table import Table

from ytissues.ytlib import Project, get_project, get_projects


def backup(args):
    """Implements backup of one Project (-i project_id) or all."""
    if args.project_id:
        project = get_project(args.project_id)
        project.backup(args.backup_dir)
    else:
        projects = get_projects()
        for project in track(projects, description="Downloading projects..."):
            project.backup(args.backup_dir)


def ls(args):
    """List all or print a concrete project on stdout."""
    if args.project_id is None:
        projects = get_projects()
        print_projects(projects, as_table=args.table, verbose=args.verbose)
    else:  # list on project with issues and number of comments and attachments
        print_project_details(args.project_id, args.table, args.verbose)


def parse_arguments(args):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        description="Use the following commands to retrieve project names or issues "
        + "from a Youtrack service.",
        metavar="COMMAND",
        required=True,
    )
    backup_parser = subparsers.add_parser(
        "backup", help="Backup all issues of all project with all attachments."
    )
    backup_parser.add_argument(
        "backup_dir",
        metavar="YT_BACKUP_DIR",
        help="The root directory to store all tickets.",
    )
    backup_parser.add_argument(
        "-i",
        "--project-id",
        metavar="PROJECT_ID",
        help="Project ID to backup (eg '0-42'). If ommited, all projects are saved.",
    )
    backup_parser.set_defaults(func=backup)
    ls_parser = subparsers.add_parser(
        "ls",
        help="List all projects as table on stdout.",
        description="If run without options, "
        "list all projects with ID, shortname and name.",
    )
    ls_parser.add_argument(
        "-t",
        "--table",
        action="store_true",
        help="Print project information in a table to stdout (not as a list).",
    )
    ls_parser.add_argument(
        "-i",
        "--project-id",
        metavar="PROJECT_ID",
        help="List the given PROJECT_ID with issues and number of comments.",
    )
    ls_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Display more information."
    )
    ls_parser.set_defaults(func=ls)
    return parser.parse_args(args)


def main():
    args = parse_arguments(sys.argv[1:])
    args.func(args)


def print_as_table(projects: list[Project], verbose):
    table = Table(
        title="List of projects",
        caption=f"{len(projects)} projects in total",
        box=box.ROUNDED,
    )
    table.add_column("ID", justify="right", no_wrap=True)
    table.add_column("Short Name", no_wrap=True)
    table.add_column("Name", no_wrap=True)
    if verbose:
        table.add_column("Issues", no_wrap=True)

    for project in track(projects, description="Getting info..."):
        if verbose:
            table.add_row(
                project.project_id,
                project.shortname,
                project.name,
                str(len(project.issues)),
            )
        else:
            table.add_row(project.project_id, project.shortname, project.name)
    console = Console()
    console.print(table)


def print_as_list(projects: list[Project], verbose):
    for project in projects:
        print(project.as_plaintext(verbose))


def print_projects(
    projects: list[Project], as_table: bool = False, verbose: bool = False
):
    if as_table:
        print_as_table(projects, verbose)
    else:
        print_as_list(projects, verbose)


def print_project_details(project_id: str, as_table: bool, verbose: bool):
    project = get_project(project_id)
    project.print_details(as_table, verbose)

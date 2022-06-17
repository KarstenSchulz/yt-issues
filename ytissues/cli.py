import argparse
import sys

from ytissues.ytlib import (
    get_project,
    get_projects,
    print_project_details,
    print_projects,
)


def backup(args):
    """Implements backup of one Project (-i project_id) or all."""
    if args.project_id:
        project = get_project(args.project_id)
        project.backup(args.backup_dir)
    else:
        for project in get_projects():
            project.backup(args.backup_dir)


def ls(args):
    """List all or print a concrete project on stdout."""
    if args.project_id is None:
        projects = get_projects(args.project_id)
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

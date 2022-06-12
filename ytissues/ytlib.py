"""
Library for retrieving issues from the youtrack service.

Get data from https://www.jetbrains.com/help/youtrack/devportal/youtrack-rest-api.html

"""
import argparse
import json
import os
from urllib import request

from rich import box
from rich.console import Console
from rich.table import Table


class Project:
    """Contains all important data on a project and methods to backup."""

    resource: str = "/api/admin/projects"

    def __init__(self, project_id: str, shortname: str = None, name: str = None):
        self.project_id = project_id or None
        self.shortname = shortname or None
        self.name = name or None
        if shortname:
            self.displayname = shortname
        elif name:
            self.displayname = name
        else:
            self.displayname = project_id
        self.issues = []

    def __str__(self) -> str:
        return self.displayname

    def __eq__(self, other):
        return self.project_id == other.project_id

    def as_plaintext(self) -> str:
        """Return one line for ls command."""
        return f"{self.project_id} {self.shortname} {self.name}"


def backup(args):
    """Implements ls sub-command and lists project names or issues"""
    raise NotImplementedError


def print_as_table(projects: list[Project]):
    table = Table(
        title="List of projects",
        caption=f"{len(projects)} projects in total",
        box=box.ROUNDED,
    )
    table.add_column("ID", justify="right", no_wrap=True)
    table.add_column("Short Name", no_wrap=True)
    table.add_column("Name", no_wrap=True)
    for project in projects:
        table.add_row(project.project_id, project.shortname, project.name)
    console = Console()
    console.print(table)


def get_request(resource: str, query: str) -> request.Request:
    """Return a Request object for the YT service.

    Args:
        resource: The api resource, for example `/api/admin/projects`
        query: The GET query string, for example `?fields=id,name,shortName'

    Returns:
        The Request object, ready to use, with headers set.

    Raises:
        KeyError, if environment variables YT_URL or YT_AUTH are missing.
        ValueError, if some of the data is malformed.
    """
    # check some data:
    yt_url = os.environ["YT_URL"]
    yt_auth = os.environ["YT_AUTH"]
    if yt_url.endswith("/"):
        raise ValueError(f"YT_URL must not end with '/': {yt_url}")
    if not resource.startswith("/"):
        raise ValueError(f"Resource must start with '/': {resource}")
    if query.startswith("?"):
        raise ValueError(f"Query must not start with '?': {query}")

    url = f"{yt_url}{resource}?{query}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {yt_auth}"}
    return request.Request(url, headers=headers)


def get_projects() -> list[Project]:
    the_request = get_request(Project.resource, "fields=id,name,shortName")
    opened_url = request.urlopen(the_request)
    if opened_url.getcode() == 200:
        data = opened_url.read()
        json_data = json.loads(data)
        projects = []
        for item in json_data:
            projects.append(
                Project(
                    project_id=item["id"],
                    shortname=item["shortName"],
                    name=item["name"],
                )
            )
        return projects
    else:
        print("Error receiving data", opened_url.getcode())
        return []


def ls(args):
    """List all projects on stdout."""
    project_list = get_projects()
    if args.plain:
        for project in project_list:
            print(project.as_plaintext())
    else:
        print_as_table(project_list)


def main():
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
        "backup-dir",
        metavar="YT_BACKUP_DIR",
        help="The root directory to store all tickets.",
    )
    backup_parser.add_argument(
        "-p",
        "--project-id",
        metavar="PROJECT_ID",
        help="Project ID to backup (eg '0-42'). If ommited, all projects are saved.",
    )
    backup_parser.set_defaults(func=backup)
    ls_parser = subparsers.add_parser(
        "ls", help="List all projects as table on stdout."
    )
    ls_parser.add_argument(
        "-p",
        "--plain",
        action="store_true",
        help="Print project information as plain lines to stdout (not as a table).",
    )
    ls_parser.set_defaults(func=ls)
    args = parser.parse_args()
    args.func(args)

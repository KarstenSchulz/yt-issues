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
    """Contains all important data on a project and methods to backup.

    Loads lazy. We hit the API only, when data for example issues is requested.

    """

    get_list: str = "/api/admin/projects"
    get_item: str = "/api/admin/projects/{project_id}"

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
        self._issues = None

    def __str__(self) -> str:
        return self.displayname

    def __eq__(self, other):
        return self.project_id == other.project_id

    def as_plaintext(self) -> str:
        """Return one line for ls command."""
        return f"{self.project_id} {self.shortname} {self.name}"

    def print(self):
        print(self.as_plaintext())


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


def print_as_list(projects: list[Project]):
    for project in projects:
        print(project.as_plaintext())


def list_projects(projects: list[Project], as_table: bool = False):
    if as_table:
        print_as_table(projects)
    else:
        print_as_list(projects)


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

    if query:
        url = f"{yt_url}{resource}?{query}"
    else:
        url = f"{yt_url}{resource}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {yt_auth}"}
    return request.Request(url, headers=headers)


def get_projects(project_id: str = None) -> list[Project]:
    if project_id is None:  # list all Projects
        the_request = get_request(Project.get_list, "fields=id,name,shortName")
    else:
        the_request = get_request(
            Project.get_item.format(project_id=project_id[0]),
            "fields=id,name,shortName",
        )
    opened_url = request.urlopen(the_request)
    if opened_url.getcode() == 200:
        data = opened_url.read()
        json_data = json.loads(data)
        if isinstance(json_data, list):
            projects = []
            for item in json_data:
                projects.append(
                    Project(
                        project_id=item["id"],
                        shortname=item["shortName"],
                        name=item["name"],
                    )
                )
        else:
            projects = [
                Project(
                    project_id=json_data["id"],
                    shortname=json_data["shortName"],
                    name=json_data["name"],
                )
            ]
        return projects
    else:
        print("Error receiving data", opened_url.getcode())
        return []


def ls(args):
    """List all or print a concrete project on stdout."""
    projects = get_projects(args.project_id)
    list_projects(projects, as_table=args.table)


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
        "--project_id",
        metavar="PROJECT_ID",
        nargs="*",
        help="List issues of the given PROJECT_IDs.",
    )
    ls_parser.set_defaults(func=ls)
    args = parser.parse_args()
    args.func(args)

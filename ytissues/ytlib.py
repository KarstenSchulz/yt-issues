"""
Library for retrieving issues from the youtrack service.

Get data from https://www.jetbrains.com/help/youtrack/devportal/youtrack-rest-api.html

"""
import argparse
import json
import os
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from urllib import request

from rich import box
from rich.console import Console
from rich.progress import track
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
        self._issues = None

    @property
    def displayname(self) -> str:
        if self.shortname:
            return self.shortname
        return self.name if self.name else self.project_id

    @property
    def issues(self):
        if self._issues is None:
            self._issues = Issue.load(self.project_id)
        return self._issues

    def __str__(self) -> str:
        return self.displayname

    def __eq__(self, other):
        return self.project_id == other.project_id

    def as_plaintext(self, verbose=False) -> str:
        """Return one line for ls command."""
        line = f"{self.project_id} {self.shortname} {self.name}"
        if verbose:
            line += f" {len(self.issues)} issues"
        return line

    def print_details(self, as_table, verbose):
        """Print Project with issues."""

        def get_issue_data() -> list[str]:
            if verbose:
                return [
                    issue.issue_id,
                    issue.id_readable,
                    issue.created.strftime("%Y-%m-%d %H:%M"),
                    issue.updated.strftime("%Y-%m-%d %H:%M"),
                    "Yes" if issue.resolved else "No",
                    issue.summary,
                    str(issue.comments_count),
                ]
            else:
                return [
                    issue.issue_id,
                    issue.created.strftime("%Y-%m-%d %H:%M"),
                    issue.updated.strftime("%Y-%m-%d %H:%M"),
                    "Yes" if issue.resolved else "No",
                    issue.summary,
                ]

        if as_table:
            table = Table(
                title=f"Project {self.displayname}",
                caption=f"{len(self.issues)} issues in total",
                box=box.ROUNDED,
            )
            table.add_column("ID", justify="right", no_wrap=True)
            if verbose:
                table.add_column("Issue-ID", justify="right", no_wrap=True)

            table.add_column("Created", justify="center", no_wrap=True)
            table.add_column("Last Update", justify="center", no_wrap=True)
            table.add_column("Resolved", justify="center", no_wrap=True)
            table.add_column("Summary", no_wrap=False)
            if verbose:
                table.add_column("Comments", no_wrap=True)
            for issue in self.issues:
                table.add_row(*get_issue_data())
            console = Console()
            console.print(table)
        else:
            print("Issue ID;Created;Last Update;Resolved;Summary;Comments")
            for issue in self.issues:
                print(";".join(get_issue_data()))

    def backup(self, backup_pathname: str):
        """Write all Project data to files in the directory 'backup_pathname'.

        Raises:

        """

        # main backup dir:
        backup_path = Path(trim_pathname(backup_pathname))
        backup_path.mkdir(parents=True, exist_ok=True)
        # the backup dir for one project:
        project_path = backup_path / trim_pathname(self.displayname)
        project_path.mkdir(parents=True, exist_ok=True)
        for issue in self.issues:
            issue.backup(project_path)


class Issue:
    """Represent an Issue in YouTrack.

    When instantiated, it loads the missing values from the YT service.
    """

    get_list: str = "/api/admin/projects/{project_id}/issues"
    get_item: str = "/api/issues/{issue_id}"
    get_comments: str = "/api/issues/{issue_id}/comments"
    get_attachments: str = "/api/issues/{issue_id}/attachments"

    fields = "id,idReadable,created,updated,resolved,summary,description,commentsCount"

    def __init__(
        self,
        issue_id: str,
        project_id: str,
        id_readable: str = None,
        created: datetime = None,
        updated: datetime = None,
        resolved: datetime = None,
        description: str = None,
        summary: str = None,
        comments_count=0,
    ):
        self.issue_id = issue_id
        self.project_id = project_id
        self.id_readable = id_readable
        self.created = created
        self.updated = updated
        self.resolved = resolved
        self.description = description
        self.summary = trim_filename(
            f"{self.created.strftime('%Y-%m-%d')} " f"{self.id_readable} - {summary}"
        )
        self.comments_count = comments_count
        self._comments = None

    @property
    def comments(self):
        if self._comments is None:
            self._comments = IssueComment.load(self.issue_id)
        return self._comments

    def backup(self, backup_path):
        """Save issue Data to backup_path.

        Args:
            backup_path: the pathlib.Path to the backup directory.
        """
        filename = self.summary + ".md"
        filepath = backup_path / Path(filename)
        if self.resolved:
            resolved_text = f"Resolved: {self.resolved.strftime('%Y-%m-%d %H:%M')}.\n"
        else:
            resolved_text = "Resolved: No.\n"
        issue_text = (
            f"# {self.summary}\n"
            f"Created: {self.created.strftime('%Y-%m-%d %H:%M')}\n"
            f"Updated: {self.updated.strftime('%Y-%m-%d %H:%M')}\n"
            f"{resolved_text}\n"
            f"{self.description}\n\n"
        )
        issue_text += textwrap.dedent(f"""{self.all_comments_as_text()}""")
        filepath.write_text(issue_text)

    def all_comments_as_text(self) -> str:
        """List all comments to save them into the backup file.

        Returns:
            A (possibly big) string with all comments of the issue.
        """
        comments = ""
        for comment in self.comments:
            comments += comment.as_text()
        return comments

    @staticmethod
    def load(project_id: str) -> list:
        the_request = get_request(
            Issue.get_list.format(project_id=project_id), f"fields={Issue.fields}"
        )
        opened_url = request.urlopen(the_request)
        if opened_url.getcode() == 200:
            data = opened_url.read()
            json_data = json.loads(data)
            if isinstance(json_data, list):
                issues = []
                for item in json_data:
                    created, updated, resolved = None, None, None
                    if item["created"] is not None:
                        created = datetime.fromtimestamp(item["created"] / 1000)
                    if item["updated"] is not None:
                        updated = datetime.fromtimestamp(item["updated"] / 1000)
                    if item["resolved"] is not None:
                        resolved = datetime.fromtimestamp(item["resolved"] / 1000)

                    issues.append(
                        Issue(
                            issue_id=item["id"],
                            project_id=project_id,
                            id_readable=item["idReadable"],
                            created=created,
                            updated=updated,
                            resolved=resolved,
                            description=item["description"],
                            summary=item["summary"],
                            comments_count=item["commentsCount"],
                        )
                    )
            else:
                try:
                    issues = [
                        Issue(
                            issue_id=json_data["id"],
                            project_id=project_id,
                        )
                    ]
                except KeyError:  # we got no project
                    issues = []
            return issues
        else:
            raise IOError(f"Error {opened_url.getcode()} receiving data")


class IssueComment:
    """Represent a Comment in an Issue in YouTrack.

    When instantiated, it loads the missing values from the YT service.
    """

    get_list: str = "/api/issues/{issue_id}/comments"
    get_item: str = "/api/issues/{issue_id}/comments/{commentID}"

    fields = "id,text,created,updated,author(name),attachments(id,name)"

    def __init__(
        self,
        comment_id: str,
        author: str = None,
        created: datetime = None,
        updated: datetime = None,
        text: str = None,
    ):
        self.comment_id = comment_id
        self.author = author
        self.created = created
        self.updated = updated
        self.text = text
        self._attachment_names = None

    @property
    def attachment_names(self):
        raise NotImplementedError

    def __str__(self):
        infoline = f"\n---\n**Kommentar von {self.author}, "
        if self.created:
            infoline += f"created: {self.created.strftime('%Y-%m-%d %H:%M')}, "
        else:
            infoline += "created: -, "
        if self.updated:
            infoline += f"updated: {self.updated.strftime('%Y-%m-%d %H:%M')}. "
        else:
            infoline += "updated: -."
        infoline += "**\n\n"
        return infoline + self.text

    def as_text(self) -> str:
        return self.__str__()

    @staticmethod
    def load(issue_id: str) -> list:
        """Return list of comments for Issue issue_id."""
        the_request = get_request(
            IssueComment.get_list.format(issue_id=issue_id),
            f"fields={IssueComment.fields}",
        )
        opened_url = request.urlopen(the_request)
        if opened_url.getcode() == 200:
            data = opened_url.read()
            json_data = json.loads(data)
            if isinstance(json_data, list):
                issue_comments = []
                for item in json_data:
                    created, updated = None, None
                    if item["created"] is not None:
                        created = datetime.fromtimestamp(item["created"] / 1000)
                    if item["updated"] is not None:
                        updated = datetime.fromtimestamp(item["updated"] / 1000)

                    issue_comments.append(
                        IssueComment(
                            comment_id=item["id"],
                            author=item["author"]["name"],
                            created=created,
                            updated=updated,
                            text=item["text"],
                        )
                    )
            else:
                try:
                    created, updated = None, None
                    if json_data["created"] is not None:
                        created = datetime.fromtimestamp(json_data["created"] / 1000)
                    if json_data["updated"] is not None:
                        updated = datetime.fromtimestamp(json_data["updated"] / 1000)
                    issue_comments = [
                        IssueComment(
                            comment_id=json_data["id"],
                            author=json_data["author"],
                            created=created,
                            updated=updated,
                            text=json_data["text"],
                        )
                    ]
                except KeyError:  # we got no project
                    issue_comments = []
            return issue_comments
        else:
            raise IOError(f"Error {opened_url.getcode()} receiving data")


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
        IOError, if server connection returns error
    """
    yt_url = os.environ["YT_URL"]
    yt_auth = os.environ["YT_AUTH"]
    # check the data:
    if resource.endswith("/"):
        raise ValueError(f"YT_URL must not end with '/': {yt_url}")
    if not resource.startswith("/"):
        raise ValueError(f"Resource must start with '/': {resource}")
    if query.startswith("?"):
        raise ValueError(f"Query must not start with '?': {query}")
    if query and not query.startswith("fields="):
        raise ValueError(f"Query must start with 'fields=': {query}")

    url = f"{yt_url}{resource}?{query}" if query else f"{yt_url}{resource}"
    headers = {"Accept": "application/json", "Authorization": f"Bearer {yt_auth}"}
    return request.Request(url, headers=headers)


def get_project(project_id: str) -> Project:
    projects = get_projects(project_id)
    if len(projects) != 1:
        raise ValueError(f"Projekt mit id {project_id} nicht gefunden!")
    return projects[0]


def get_projects(project_id: str = None) -> list[Project]:
    if project_id is None:  # list all Projects
        the_request = get_request(Project.get_list, "fields=id,name,shortName")
    else:
        the_request = get_request(
            Project.get_item.format(project_id=project_id),
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
            try:
                projects = [
                    Project(
                        project_id=json_data["id"],
                        shortname=json_data["shortName"],
                        name=json_data["name"],
                    )
                ]
            except KeyError:  # we got no project
                projects = []
        return projects
    else:
        raise IOError(f"Error {opened_url.getcode()} receiving data")


def backup(args):
    """Implements backup of one Project (-i project_id) or all."""
    if args.project_id:
        project = get_project(args.project_id)
        project.backup(args.backup_dir)
    else:
        raise NotImplementedError("No complete backup atm.")


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


def trim_pathname(pathname: str) -> str:
    """Replace critical chars in `pathname`.

    Repaces critical chars with space and squeezes spaces to one space.

    Args:
         pathname: A relative or absolute pathname to backup the project.
     Returns:
         A string with the cleaned pathname
    """
    cleaned_pathname = re.sub(r"[:\\><]", " ", pathname)
    return re.sub(" {2,}", " ", cleaned_pathname)


def trim_filename(filename: str) -> str:
    """Replace critical chars in `filename`.

    Repaces chars with space and squeezes spaces to one space.

    Args:
         filename: A filename to use to write to the filesystem. Can be the summary
            of an issue.
     Returns:
         A string with the cleaned filename (eg. removed slash ('/')
    """
    cleaned_filename = re.sub(r"[/:\\><]", " ", filename)
    return re.sub(" {2,}", " ", cleaned_filename)


def main():
    args = parse_arguments(sys.argv[1:])
    args.func(args)

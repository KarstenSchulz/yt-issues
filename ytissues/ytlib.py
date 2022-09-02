"""
Library for retrieving issues from the youtrack service.

Get data from https://www.jetbrains.com/help/youtrack/devportal/youtrack-rest-api.html

"""
import json
import os
import re
import textwrap
from datetime import datetime
from pathlib import Path
from urllib import request

from rich import box
from rich.console import Console
from rich.table import Table


class Project:
    """Contains all important data on a project and methods to backup.

    Loads lazy. We hit the API only, when data for example issues is requested.

    """

    get_list: str = "/youtrack/api/admin/projects"
    get_item: str = "/youtrack/api/admin/projects/{project_id}"

    def __init__(self, project_id: str, shortname: str = None, name: str = None):
        self.project_id = project_id
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
        if isinstance(other, Project):
            return self.project_id == other.project_id
        else:
            return False

    def as_plaintext(self, verbose=False) -> str:
        """Return one line for ls command."""
        line = f"{self.project_id} {self.shortname} {self.name}"
        if verbose:
            line += f" {len(self.issues)} issues"
        return line

    def print_details(self, as_table: bool, verbose: bool):
        """Print Project with issues."""

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
                table.add_row(*get_issue_data(issue, verbose))
            console = Console()
            console.print(table)
        else:
            if verbose:
                print("Issue ID;Created;Last Update;Resolved;Summary;Comments")
            else:
                print("Issue ID;Created;Last Update;Resolved;Summary")
            for issue in self.issues:
                print(";".join(get_issue_data(issue, verbose)))

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

    get_list: str = "/youtrack/api/admin/projects/{project_id}/issues"
    get_item: str = "/youtrack/api/issues/{issue_id}"

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
        self.summary = self.create_summary(summary)
        self.comments_count = comments_count
        self._comments = None
        self._attachments = None

    def create_summary(self, summary: str) -> str:
        """Make a meaningful summary heading from raw summary."""
        if self.created and self.id_readable and summary:
            return trim_filename(
                f"{self.created.strftime('%Y-%m-%d')} "
                f"{self.id_readable} - {summary}"
            )
        else:
            return summary

    @property
    def comments(self):
        if self._comments is None:
            self._comments = IssueComment.load(self.issue_id)
        return self._comments

    @property
    def attachments(self):
        if self._attachments is None:
            self._attachments = self.load_attachments()
        return self._attachments

    def load_attachments(self) -> list:
        the_request = get_request(
            IssueAttachment.get_list.format(issue_id=self.issue_id),
            f"fields={IssueAttachment.fields}",
        )
        opened_url = request.urlopen(the_request)
        if opened_url.getcode() == 200:
            data = opened_url.read()
            json_data = json.loads(data)
            if isinstance(json_data, list):
                issue_attachments = []
                for item in json_data:
                    issue_attachments.append(
                        IssueAttachment(
                            issue_id=self.issue_id,
                            name=item["name"],
                            size=item["size"],
                            mimetype=item["mimeType"],
                            extension=item["extension"],
                            charset=item["charset"],
                            url=item["url"],
                        )
                    )
            else:
                try:
                    issue_attachments = [
                        IssueAttachment(
                            issue_id=self.issue_id,
                            name=json_data["name"],
                            size=json_data["size"],
                            mimetype=json_data["mimeType"],
                            extension=json_data["extension"],
                            charset=json_data["charset"],
                            url=json_data["url"],
                        )
                    ]
                except KeyError:
                    issue_attachments = []
            return issue_attachments
        else:
            raise IOError(f"Error {opened_url.getcode()} receiving data")

    def backup(self, backup_path: Path):
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
            f"{self.description}\n"
        )
        issue_text += self.attachment_list()
        issue_text += "\n\n"
        issue_text += textwrap.dedent(f"""{self.all_comments_as_text()}""")
        filepath.write_text(issue_text)
        if len(self.attachments) > 0:
            yt_url = os.environ["YT_URL"]
            attachment_dir = backup_path / f"{self.summary}_attachments"
            attachment_dir.mkdir(exist_ok=True)
            for attachment in self.attachments:
                save_file = attachment_dir / attachment.name
                opened_url = request.urlopen(yt_url + attachment.url)
                save_file.write_bytes(opened_url.read())

    def attachment_list(self) -> str:
        """Return a markdown-list of attachment names or emptry string."""
        attachment_list = ""
        if len(self.attachments) > 0:
            attachment_list += f"There are {len(self.attachments)} attachments:\n"
            for item in self.attachments:
                attachment_list += f"* {item.name}\n"
        return attachment_list

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


class IssueAttachment:
    """Represents an Attachment to the issue (Name and link, not the data!)."""

    get_list = "/youtrack/api/issues/{issue_id}/attachments"
    fields = "name,size,mimeType,extension,charset,url"

    def __init__(self, issue_id, name, size, mimetype, extension, charset, url):
        self.issue_id = issue_id
        self.name = name
        self.size = size
        self.mimetype = mimetype
        self.extension = extension
        self.charset = charset
        self.url = url


class IssueComment:
    """Represent a Comment in an Issue in YouTrack.

    When instantiated, it loads the missing values from the YT service.
    """

    get_list: str = "/youtrack/api/issues/{issue_id}/comments"
    get_item: str = "/youtrack/api/issues/{issue_id}/comments/{commentID}"

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
        self.text = text or ""
        self._attachment_names = None

    @property
    def attachment_names(self):
        raise NotImplementedError

    def __str__(self):
        infoline = f"\n---\n**Comment by {self.author}, "
        if self.created:
            infoline += f"created: {self.created.strftime('%Y-%m-%d %H:%M')}, "
        else:
            infoline += "created: -, "
        if self.updated:
            infoline += f"updated: {self.updated.strftime('%Y-%m-%d %H:%M')}. "
        else:
            infoline += "updated: -"
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


def get_issue_data(issue: Issue, verbose: bool = False) -> [str]:
    """Return the fields of issue as list for printing.

    Args:
        issue: the issue to print
        verbose: print as rich.table (True) or as csv line (False)
    """

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


def get_request(resource: str, query: str) -> request.Request:
    """Return a Request object for the YT service.

    Args:
        resource: The api resource, for example `/youtrack/api/admin/projects`
        query: The GET query string, for example `fields=id,name,shortName'

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
        raise ValueError(f"Project with ID '{project_id}' not found!")
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

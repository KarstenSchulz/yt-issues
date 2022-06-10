"""Library for retrieving issues from the youtrack service."""
import argparse
import os
import sys

from rich import print


def ls(args) -> int:
    """Implements ls sub-command and lists project names or issues"""
    print(args)
    return 0


def cp(args) -> int:
    """Implements cp sub-command and copies issues to a local directory"""
    print(args)
    return 0


def get_access_information() -> (str, str):
    """Retrieve the YouTrack service url and the auth token from the environment.

    :returns a tuple of strings (URL, AUTH-TOKEN)
    :raises: KeyError, if YT_URL or YT_AUTH is not set.
    """
    try:
        yt_url = os.environ["YT_URL"]
        yt_auth = os.environ["YT_AUTH"]
    except KeyError:
        print(
            "[bold red]Make sure, the the environment variable YT_URL is set "
            "to the service url and YT_AUTH is set to a valid authorization "
            "token.[/bold red]",
            file=sys.stderr,
        )
        raise
    return yt_url, yt_auth


def main():
    yt_url, yt_auth = get_access_information()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        description="Use the following commands to retrieve project names or issues "
        + "from a Youtrack service.",
        metavar="COMMAND",
        required=True,
    )

    ls_parser = subparsers.add_parser(
        "ls",
        help="List projects or issues from a YouTrack service.",
    )
    ls_parser.add_argument(
        "-s",
        "--with-solved",
        action="store_true",
        help="If given, retrieve solved issues and closed projects, too.",
    )
    ls_parser.add_argument(
        "project",
        metavar="PROJECT",
        nargs="?",
        default=None,
        help="List the issues of PROJECT. If omitted, list project names.",
    )
    ls_parser.set_defaults(func=ls)

    cp_parser = subparsers.add_parser(
        "cp",
        help="Copy issue(s) to DESTDIR.",
        epilog="""
        Make sure, the the environment variable YT_ISSUE_ACCESS_AUTH is set to
        a valid authorization token.""",
    )
    cp_parser.add_argument(
        "src",
        metavar="SRC",
        nargs="+",
        help="SRC can be a project name (copies all issues of the project)"
        + " or an issue id.",
    )
    cp_parser.add_argument(
        "destdir", metavar="DESTDIR", help="Destination directory for the copied data."
    )
    cp_parser.set_defaults(func=cp)
    parser.set_defaults(yt_url=yt_url, yt_auth=yt_auth)
    args = parser.parse_args()
    return args.func(args)

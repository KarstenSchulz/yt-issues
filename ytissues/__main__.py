"""Main entry point."""
import argparse
import sys


def main():
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
        epilog="""
        Make sure, the the environment variable YT_URL is set to the service url and
        YT_ISSUE_ACCESS_AUTH is set to a valid authorization token.""",
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

    cp_parser = subparsers.add_parser(
        "cp",
        help="Copy issue(s) to DESTDIR.",
        epilog="""
        Make sure, the the environment variable YT_ISSUE_ACCESS_AUTH is set to
        a valid authorization token.""",
    )
    cp_parser.add_argument("id", metavar="ID", nargs="+", help="Issue id(s) to copy")
    cp_parser.add_argument(
        "destdir", metavar="DESTDIR", help="Destination directory for the issues."
    )

    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    sys.exit(main())

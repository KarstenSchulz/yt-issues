# yt-issues
Command line tool `yt` to retrieve and backup issues from a
[YouTrack](https://www.jetbrains.com/youtrack/) service.

The aim of this tool is not to create a backup to ensure availability of data.
For that, you should use the backup function of the youtrack service, see https://www.jetbrains.com/help/youtrack/incloud/Database.html#export-youtrack-database-incloud for cloud services or https://www.jetbrains.com/help/youtrack/standalone/Back-Up-the-Database.html for on premise installations.

This tool is to generate local markdown files with ticket information and comments and the attachments, so that the information can be viewed with a local markdown app or can be greped in the filesystem.
After a backup, you can use and manipulate the data with standard file-based tool and commands.
No need for a running server.

For that, text and comments of issues will be slightly reformatted and stored into markdown files.
Attachments of the issues will be stored accordingly in corresponding folders.
It is planned to convert the links to the attachments, so that they are usable in the local copy. Until then, just use your file explorer to view the attachments.

This tool can be useful for:
- To have a local archive, which is grepable.
- To have fast access to attachments without waiting for downloads (I live in germany 🙄).
- To have access to the most important data in case of service failure or outage.
- To have an offline local copy for outages of the service (planned or unplanned).
- To have a copy of the data on mobile devices without online access.
- ...

## Roadmap

### Currently in development (0.0.4)

(see version info in ytissues.VERSION)

- Attention: We switched from poetry (0.0.3) to pip / pip-tools (since 0.0.4)
- First versions of `yt ls` and `yt backup` implemented.
- next: Research für asyncio / aiohttp on the way to speed up things

### Version 0.1.0 (MVP implemented, tests needed)
- `yt ls PROJECT [PROJECT ...]` - if no PROJECT given: list all open projects, otherwise list open (or all) issues of PROJECT to stdout (ID, Title, State).
- `yt backup YT_BACKUP_DIR` - Download all issues with attachments of all project to subdirs in YT_BACKUP_DIR in a readable format, which means markdown files with attachments in their corresponding attachment directories.

If for example the issue WD-1 in the only project World Domination has a PDF file `Roadmap to World Domination.pdf` and an image `screenshot presidents pc.png` and the issue WD-2 has no attachments, the workflow and the downloaded structure of this will be:

```shell
donald$ yt backup all_issues
# Downloading issue data ...
donald$ tree all_issues/
all_issues/
└── World Domination
    ├── wd-1
    │   ├── wd-1.md
    │   └── wd-1_attachments
    │       ├── Roadmap to World Domination.pdf
    │       └── screenshot presidents pc.png
    └── wd-2
        └── wd-2.md
```
Links in the markdown files will be adjusted accordingly, so that they remain accessible.

### Version 0.2.0

- `yt cp SRC [SRC ...] DESTDIR` - download issues with comments and attachments to DESTDIR as markdown files and attachments in a sub directory. If SRC is a project name, download all issues of the project. If SRC is an issue id, download that id.

### Version 0.3.0
- `yt -q {query}` - execute the YouTrack query and retrieve results as json to stdout.

### Version 0.4.0
- `yt gt [ -l LIST | --list=LIST ] ID [ID ...]` - Add issue ID to the [MacOS GoodTask App](https://goodtaskapp.com) to the reminders standard list or to the named LIST.

## Get started

First generate a permanent token to authorize against your youtrack service as described in https://www.jetbrains.com/help/youtrack/devportal/Manage-Permanent-Token.html.

The token must be stored in the environment variable YT_AUTH when running the command `yt`.
If you use the bash shell, enter a line like `export YT_AUTH=perm:ABCD42efg...` in your startup script.

You must also set the environment variable YT_URL to the base URL of your YouTrack service as described in https://www.jetbrains.com/help/youtrack/devportal/api-url-and-endpoints.html.

You can also set the environment on the command line when calling the command like so:
```shell
YT_AUTH=perm:ABCD42efg... YT_URL=https://... yt
```

## YouTrack REST API

See the documentation at https://www.jetbrains.com/help/youtrack/devportal/api-getting-started.html

## Dependencies
- [rich](https://pypi.org/project/rich/) - *Rich is a Python library for rich text and beautiful formatting in the terminal.*

For the development:

- black
- flake8
- isort
- pre-commit
- pytest
- coverage

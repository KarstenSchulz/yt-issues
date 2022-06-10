# yt-issues
Command line tool `yt` to retrieve and export issues from a
[YouTrack](https://www.jetbrains.com/youtrack/) service.

## Roadmap

### Version 0.1.0 (MVP, in development)
- `yt backup YT_BACKUP_DIR` - Download all issues with attachments of all project to subdirs in YT_BACKUP_DIR.

### Version 0.2.0
- `yt ls [-s | --with-solved ] [PROJECT]` - if no PROJECT given: list all open projects, otherwise list open (or all) issues of PROJECT to stdout (ID, Title, State).
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

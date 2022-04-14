# yt-issues
Command line tool to retrieve and export issues from
[YouTrack](https://www.jetbrains.com/youtrack/) service.

## Roadmap

### Version 0.1.0
- `yt ls [-a | --all ] PROJECT` - list open (or all) issues of project PROJECT to stdout (ID, Title, State).
- `yt cp PROJECT OUTDIR` - download all issues of PROJECT with comments and attachments to OUTDIR as markdown files and attachments in a sub directory.

### Version 0.2.0
- `yt -q {query}` - execute the YouTrack query and retrieve results as json.

### Version 0.3.0
- `yt gt [ -l LIST | --list=LIST ] ID` - Add issue ID to the MacOS GoodTask App to the standard list or to the list LIST.

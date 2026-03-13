# yt — YouTrack CLI & Backup Tool

`yt` is a lightweight command-line tool to list projects and back up [YouTrack](https://www.jetbrains.com/youtrack/) issues as local Markdown files.

It allows you to:
- Create a **local, searchable archive** of your tickets.
- Access your data **offline** or during service outages.
- Speed up access to **attachments** without waiting for browser downloads.
- Use standard terminal tools like `grep` to find information across all issues.

## Quick Start

```bash
# Configure your YouTrack connection
export YT_URL="https://youtrack.example.com"
export YT_AUTH="perm:your-token-here"

# List all projects
$ yt ls -t

# List all issues in a specific project
$ yt ls -i "PROJ-ID"

# Back up all issues and attachments to a local directory
$ yt backup ./my_backup
```

The backup command creates an organized structure:
```text
my_backup/
└── PROJ/
    └── 2023-10-08 PROJ-1 - Task Summary/
        ├── 2023-10-08 PROJ-1 - Task Summary.md
        ├── screenshot.png
        └── document.pdf
```

## Requirements

- **Python**: 3.11 or higher
- **YouTrack Token**: A [Permanent Token](https://www.jetbrains.com/help/youtrack/devportal/Manage-Permanent-Token.html) for authentication.
- **Dependencies**: [rich](https://pypi.org/project/rich/) (installed automatically)

## Installation

Install directly from the source:

```bash
git clone https://github.com/kaschu/yt-issues.git
cd yt-issues
pip install .
```

For development, use an editable install:
```bash
pip install -e .
```

## Usage

### Environment Variables

`yt` requires two environment variables to connect to your YouTrack instance:

| Variable  | Description                           | Example                        |
|:----------|:--------------------------------------|:-------------------------------|
| `YT_URL`  | The base URL of your YouTrack service | `https://youtrack.example.com` |
| `YT_AUTH` | Your permanent API token              | `perm:ABCD123...`              |

### Commands

#### `yt ls`
List projects or issues.

- `yt ls`: List all projects.
- `-t`, `--table`: Format output as a rich table.
- `-i`, `--project-id ID`: List all issues for the project with the given ID.
- `-v`, `--verbose`: Show extra information like issue counts or comment counts.

```shell
# set environment variables:
export YT_URL="https://example-server.myjetbrains.com"
export YT_AUTH="perm:secretexample_blafasel_yadda.422373..."

# Example of a verbose project table:
❯ yt ls -t -v
Getting info... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02
                   List of projects
╭──────┬──────────────────┬──────────────────┬────────╮
│   ID │ Short Name       │ Name             │ Issues │
├──────┼──────────────────┼──────────────────┼────────┤
│ 0-01 │ NOVA             │ nova-core        │ 42     │
│ 0-02 │ ORBIT            │ orbit            │ 0      │
│ 0-03 │ SKYFORGE         │ skyforge         │ 118    │
│ 0-04 │ PHANTOM          │ phantom          │ 7      │
│ 0-05 │ ZEPHYR           │ zephyr           │ 0      │
│ 0-06 │ TITAN            │ titan-backend    │ 33     │
│ 0-07 │ LUMINOS          │ luminos          │ 0      │
│ 0-19 │ AXIOM            │ axiom-services   │ 89     │
│ 0-20 │ FROSTGATE        │ frostgate        │ 0      │
│ 0-21 │ PULSAR           │ pulsar           │ 5      │
│ 0-22 │ ZENITH           │ zenith           │ 0      │
╰──────┴──────────────────┴──────────────────┴────────╯
                 11 projects in total

# Example of an issue table for project ORBIT
❯ yt ls -t -i 0-02
                                                    Project ORBIT
╭────────┬──────────────────┬──────────────────┬──────────┬──────────────────────────────────────────────────────────╮
│     ID │     Created      │   Last Update    │ Resolved │ Summary                                                  │
├────────┼──────────────────┼──────────────────┼──────────┼──────────────────────────────────────────────────────────┤
│  2-658 │ 2022-10-09 08:48 │ 2023-04-25 07:47 │    No    │ 2022-10-09 ORBIT-2 - ORBIT - Gutschriftserzeugung        │
│        │                  │                  │          │ implementieren                                           │
│  2-660 │ 2022-10-09 08:49 │ 2023-04-25 07:47 │    No    │ 2022-10-09 ORBIT-3 - ORBIT - Einzelrechnung erstellen    │
│        │                  │                  │          │ implementieren                                           │
│  2-662 │ 2022-10-09 08:52 │ 2023-04-25 07:47 │    No    │ 2022-10-09 ORBIT-4 - ORBIT - Aufbereitung der Daten      │
│        │                  │                  │          │ refaktorieren, Tests schreiben                           │
│  2-734 │ 2022-12-04 10:12 │ 2023-07-19 16:21 │   Yes    │ 2022-12-04 ORBIT-5 - ORBIT - Ablage der Monatsrechnungen │
│        │                  │                  │          │ der Rechnungsdateien (*.pdf, *.tex, *.json)              │
│        │                  │                  │          │ automatisieren                                           │
│ 2-1331 │ 2024-07-14 16:24 │ 2024-07-14 16:24 │    No    │ 2024-07-14 ORBIT-6 - ZUGFeRD implementieren              │
╰────────┴──────────────────┴──────────────────┴──────────┴──────────────────────────────────────────────────────────╯
                                                  5 issues in total

```

#### `yt backup`
Download issues and attachments.

- `yt backup DIR`: Back up all projects to the specified directory.
- `-i`, `--project-id ID`: Back up only the specified project.

#### `yt --version`
Display the current version of the tool.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for the full text.

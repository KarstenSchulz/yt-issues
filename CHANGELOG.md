# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.6] - 2026-03-13

### Added
- Command line interface: added a version flag (`--version`).

### Changed
- Bumped version to 0.0.6.

## [0.0.5] - 2026-03-13

### Changed
- YouTrack API: updated paths (removed hardcoded `/youtrack` prefix requirement).
- YouTrack URL: improved normalization for `YT_URL` (auto-handling of leading/trailing slashes).
- Documentation: updated with more `YT_URL` configuration examples.

### Fixed
- Attachments: added timeout handling when fetching issue attachments.

## [0.0.4] - 2023-07-27

### Added
- Backup: implemented saving attachments in the same folder as the ticket to ensure local markdown links work (added 2023-08-01).
- CLI: first versions of `yt ls` and `yt backup` (re-implemented).

### Changed
- Build system: switched from Poetry (0.0.3) to pip / pip-tools.
- Performance: re-implemented core logic using `asyncio`.
- Backup structure: issues are now backed up in their own directory instead of separated folders.
- Branding: reverted tool name from `ytbackup` back to `ytissues`.

## [0.1.0] - 2022-07-30

### Added
- Initial MVP (Minimum Viable Product) implementation.
- Command `yt ls`: list projects or issues (with verbose and rich table support).
- Command `yt backup`: download all issues with comments and attachments.
- Filtering: support for YouTrack queries.
- UI: added rich terminal formatting and progress bars for downloads.

### Fixed
- Comments: fixed processing of empty comments (2022-09-02).
- Limits: implemented workaround to retrieve up to 1000 issues (2022-09-03).
- Display: fixed display bug in project details.

## [0.0.1] - 2022-04-14

### Added
- Initial project structure and library code.
- Poetry configuration for dependency management.

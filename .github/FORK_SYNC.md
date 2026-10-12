# Personal fork synchronization

This public fork follows [morluto/rea](https://github.com/morluto/rea).

- Source: upstream `main` (latest development code, not only stable releases).
- Destination: `ccrrfftt/rea`, branch `main`.
- Schedule: once daily at 05:17 UTC / 09:17 Asia/Dubai.
- Runner: GitHub Actions; no local computer needs to be running.
- Merge policy: preserve fork commits. Conflicts fail the run; no force push,
  reset, branch deletion, or automatic conflict resolution is performed.
- Scope: main-branch code only. Other branches, tags, GitHub Release records,
  release attachments, and locally installed REA versions are not synchronized.
  Official packages remain available from the upstream project.
- Credentials: the repository-scoped, short-lived `GITHUB_TOKEN` with contents
  write permission. No personal token or repository secret is required.
- Execution: only GitHub API calls; the synchronization job does not check out,
  build, or run upstream application code.

Run it manually or inspect failures at
[Actions / Sync upstream daily](https://github.com/ccrrfftt/rea/actions/workflows/sync-upstream.yml).
Future personal changes are best kept on a separate feature branch.

GitHub can delay scheduled runs. GitHub also automatically disables scheduled
workflows in public repositories after 60 days without repository activity.
If disabled, re-enable this workflow in Actions. A failed run remains visible
in Actions; email notifications depend on the account's notification settings.

This is a fork-maintenance configuration, not a new REA product release.
The upstream version, license, README, and changelog remain authoritative.

# claudetop

Terminal UI for keeping tabs on [Claude Code](https://claude.com/claude-code): running
instances and saved sessions, at a glance — token usage, context size, disk size,
model, and git branch per session.

```
┌─ running ────────────────────────────────────────────────────────────┐
│ PID   DIR                  TTY   STARTED              CMD            │
│ 8213  /home/user/api       pts/1 Wed Jul 16 09:02:11   claude         │
└─────────────────────────────────────────────────────────────────────┘
┌─ projects ─────────────────────────────────────────────────────────────┐
│ DIR                SESS  LAST ACTIVE       OUT TOK   SIZE              │
│ /home/user/api     4     2026-07-16 11:20  128,904   3.2M              │
│ /home/user/web     1     2026-07-15 18:04  9,412     410K              │
└──────────────────────────────────────────────────────────────────────┘
```

## Install

Requires Python 3.10+ and a Linux or macOS machine with `claude` on `PATH`.

**uv (recommended)**

```sh
uv tool install git+https://github.com/0xwagmi/claudetop
```

**pipx**

```sh
pipx install git+https://github.com/0xwagmi/claudetop
```

**pip**

```sh
pip install git+https://github.com/0xwagmi/claudetop
```

Any of these put a `ctop` command on your `PATH`.

## Usage

```sh
ctop
```

- Top pane lists currently running `claude` processes (pid, cwd, tty, start time, command).
- Bottom pane lists every project with saved sessions under `~/.claude/projects`,
  sorted by last activity.
- Select a project to see its sessions: message count, context tokens, total
  output tokens, size on disk, model, and git branch.

### Keybindings

| Key      | Where          | Action                  |
|----------|----------------|--------------------------|
| `r`      | projects view  | refresh                 |
| `q`      | projects view  | quit                     |
| `enter`  | projects view  | open project's sessions |
| `r`      | sessions view  | resume selected session (`claude -r <id>`) |
| `d`      | sessions view  | delete selected session (asks to confirm) |
| `q` / `esc` | sessions view | back to projects       |

## Develop

```sh
git clone https://github.com/0xwagmi/claudetop
cd claudetop
uv sync
uv run ctop
```

## License

MIT — see [LICENSE](LICENSE).

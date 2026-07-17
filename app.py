"""claudetop — TUI to see running claude instances + saved sessions, sizes, token usage."""
import subprocess

from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.screen import Screen, ModalScreen
from textual.widgets import DataTable, Footer, Header, Static
from textual.binding import Binding

import core


class ConfirmScreen(ModalScreen[bool]):
    BINDINGS = [
        Binding("y", "confirm", "yes"),
        Binding("n", "cancel", "no"),
        Binding("escape", "cancel", "no"),
    ]

    CSS = """
    ConfirmScreen { align: center middle; }
    #confirm-box {
        width: auto; height: auto; padding: 1 3;
        border: thick $error; background: $surface;
    }
    """

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield Static(f"{self.message}\n\n[y] yes    [n] no", id="confirm-box")

    def action_confirm(self):
        self.dismiss(True)

    def action_cancel(self):
        self.dismiss(False)


class RunningPane(Static):
    def compose(self) -> ComposeResult:
        yield DataTable(id="running-table")

    def on_mount(self):
        table = self.query_one("#running-table", DataTable)
        table.add_columns("PID", "DIR", "TTY", "STARTED", "CMD")
        self.refresh_data()

    @work(thread=True, exclusive=True)
    def refresh_data(self):
        data = core.running_instances()
        self.app.call_from_thread(self._populate, data)

    def _populate(self, data):
        table = self.query_one("#running-table", DataTable)
        table.clear()
        for r in data:
            table.add_row(r["pid"], r["cwd"], r["tty"], r["start"], r["cmd"], key=r["pid"])


class SessionsScreen(Screen):
    BINDINGS = [
        Binding("escape", "app.pop_screen", "back"),
        Binding("q", "app.pop_screen", "back"),
        Binding("r", "resume", "resume session"),
        Binding("d", "delete", "delete session"),
    ]

    def __init__(self, project_row: dict):
        super().__init__()
        self.project_row = project_row

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            f" {self.project_row['dir']}  —  r: resume   d: delete", id="hint"
        )
        yield DataTable(id="sessions-table")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#sessions-table", DataTable)
        table.add_columns("SESSION ID", "LAST ACTIVE", "MSGS", "CTX TOK", "OUT TOK", "SIZE", "MODEL", "BRANCH")
        table.cursor_type = "row"
        for s in self.project_row["sessions"]:
            table.add_row(
                s["session_id"],
                core.fmt_ts(s["last_ts"]),
                str(s["msgs"]),
                f"{s['ctx_tokens']:,}",
                f"{s['total_output']:,}",
                core.human_size(s["size"]),
                s["model"] or "?",
                s["git_branch"] or "?",
                key=s["session_id"],
            )
        table.focus()

    def _selected_session(self):
        table = self.query_one("#sessions-table", DataTable)
        if table.row_count == 0:
            return None
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key.value
        session_id = str(row_key)
        for s in self.project_row["sessions"]:
            if s["session_id"] == session_id:
                return s
        return None

    def action_resume(self):
        s = self._selected_session()
        if not s:
            return
        project_dir = self.project_row["dir"]
        with self.app.suspend():
            subprocess.run(["claude", "-r", s["session_id"]], cwd=project_dir)

    def action_delete(self):
        s = self._selected_session()
        if not s:
            return

        def handle(confirmed: bool):
            if not confirmed:
                return
            core.delete_session(s["path"])
            self.project_row["sessions"] = [
                x for x in self.project_row["sessions"] if x["session_id"] != s["session_id"]
            ]
            table = self.query_one("#sessions-table", DataTable)
            table.remove_row(s["session_id"])
            self.app.query_one(ProjectsPane).refresh_data()

        self.app.push_screen(
            ConfirmScreen(f"delete session {s['session_id']}\n({core.human_size(s['size'])}, {s['msgs']} msgs)?"),
            handle,
        )


class ProjectsPane(Static):
    def compose(self) -> ComposeResult:
        yield DataTable(id="projects-table")

    def on_mount(self):
        table = self.query_one("#projects-table", DataTable)
        table.add_columns("DIR", "SESS", "LAST ACTIVE", "OUT TOK", "SIZE")
        table.cursor_type = "row"
        self.refresh_data()

    @work(thread=True, exclusive=True)
    def refresh_data(self):
        rows = core.project_summary()
        self.app.call_from_thread(self._populate, rows)

    def _populate(self, rows):
        table = self.query_one("#projects-table", DataTable)
        table.clear()
        self.rows_by_key = {}
        for row in rows:
            table.add_row(
                row["dir"],
                str(row["n"]),
                core.fmt_ts(row["last_ts"]),
                f"{row['total_out']:,}",
                core.human_size(row["total_size"]),
                key=row["dir"],
            )
            self.rows_by_key[row["dir"]] = row

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        row = self.rows_by_key.get(str(event.row_key.value))
        if row:
            self.app.push_screen(SessionsScreen(row))


class ClaudetopApp(App):
    CSS = """
    #hint { padding: 1 2; color: $text-muted; }
    RunningPane { height: auto; max-height: 30%; border: solid $accent; margin-bottom: 1; }
    ProjectsPane { height: 1fr; border: solid $primary; }
    """

    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("r", "refresh", "refresh"),
    ]

    TITLE = "claudetop"

    def compose(self) -> ComposeResult:
        yield Header()
        yield RunningPane()
        yield ProjectsPane()
        yield Footer()

    def on_mount(self):
        self.query_one("#projects-table", DataTable).focus()

    def action_refresh(self):
        self.query_one(RunningPane).refresh_data()
        self.query_one(ProjectsPane).refresh_data()


def main():
    ClaudetopApp().run()


if __name__ == "__main__":
    main()

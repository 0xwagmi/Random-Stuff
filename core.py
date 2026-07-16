"""claudetop core — scan ~/.claude for running instances + saved sessions."""
import json
import os
import subprocess
from datetime import datetime

HOME = os.path.expanduser("~")
PROJ_DIR = os.path.join(HOME, ".claude", "projects")


def human_size(n: float) -> str:
    for unit in ("B", "K", "M", "G"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}T"


def decode_dir(enc_name: str) -> str:
    name = enc_name[1:] if enc_name.startswith("-") else enc_name
    return "/" + name.replace("-", "/")


def fmt_ts(ts):
    if not ts:
        return "?"
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return ts[:16]


def running_instances():
    out = []
    try:
        pids = subprocess.check_output(["pgrep", "-x", "claude"], text=True).split()
    except subprocess.CalledProcessError:
        pids = []
    for p in pids:
        try:
            cwd = os.path.realpath(f"/proc/{p}/cwd")
            tty = subprocess.check_output(["ps", "-o", "tty=", "-p", p], text=True).strip()
            start = subprocess.check_output(["ps", "-o", "lstart=", "-p", p], text=True).strip()
            cmd = subprocess.check_output(["ps", "-o", "args=", "-p", p], text=True).strip()
            out.append({"pid": p, "cwd": cwd, "tty": tty, "start": start, "cmd": cmd})
        except subprocess.CalledProcessError:
            continue
    return out


def kill_instance(pid: str, sig: str = "-TERM"):
    subprocess.run(["kill", sig, pid], check=False)


def delete_session(path: str):
    os.remove(path)


def parse_session(path: str) -> dict:
    msgs = 0
    total_output = 0
    total_input = 0
    last_usage = None
    first_ts = None
    last_ts = None
    cwd = None
    model = None
    git_branch = None
    try:
        with open(path, "r", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = d.get("timestamp")
                if ts:
                    if first_ts is None:
                        first_ts = ts
                    last_ts = ts
                if d.get("cwd"):
                    cwd = d["cwd"]
                if d.get("gitBranch"):
                    git_branch = d["gitBranch"]
                if d.get("type") == "assistant":
                    msgs += 1
                    m = d.get("message", {})
                    model = m.get("model", model)
                    usage = m.get("usage")
                    if usage:
                        last_usage = usage
                        total_output += usage.get("output_tokens", 0)
                        total_input += usage.get("input_tokens", 0)
    except OSError:
        pass

    ctx_tokens = 0
    if last_usage:
        ctx_tokens = (
            last_usage.get("input_tokens", 0)
            + last_usage.get("cache_read_input_tokens", 0)
            + last_usage.get("cache_creation_input_tokens", 0)
        )

    return {
        "msgs": msgs,
        "ctx_tokens": ctx_tokens,
        "total_output": total_output,
        "total_input": total_input,
        "first_ts": first_ts,
        "last_ts": last_ts,
        "cwd": cwd,
        "model": model,
        "git_branch": git_branch,
        "size": os.path.getsize(path),
        "path": path,
    }


def all_sessions():
    """Yield (project_dir, session_id, path) for every saved session."""
    if not os.path.isdir(PROJ_DIR):
        return
    for enc in sorted(os.listdir(PROJ_DIR)):
        enc_path = os.path.join(PROJ_DIR, enc)
        if not os.path.isdir(enc_path):
            continue
        for fn in os.listdir(enc_path):
            if fn.endswith(".jsonl"):
                yield decode_dir(enc), fn[:-6], os.path.join(enc_path, fn)


def project_summary():
    """dict: project_dir -> {sessions: [...], n, last_ts, total_out, total_size}"""
    by_dir = {}
    for pdir, sid, path in all_sessions():
        info = parse_session(path)
        info["session_id"] = sid
        by_dir.setdefault(pdir, []).append(info)

    rows = []
    for pdir, sessions in by_dir.items():
        n = len(sessions)
        last = max(sessions, key=lambda s: s["last_ts"] or "")
        total_out = sum(s["total_output"] for s in sessions)
        total_size = sum(s["size"] for s in sessions)
        rows.append(
            {
                "dir": pdir,
                "n": n,
                "last_ts": last["last_ts"],
                "total_out": total_out,
                "total_size": total_size,
                "sessions": sorted(sessions, key=lambda s: s["last_ts"] or ""),
            }
        )
    rows.sort(key=lambda r: r["last_ts"] or "")
    return rows

"""claudetop core — scan ~/.claude for running instances + saved sessions."""
import json
import os
import subprocess
from datetime import datetime

HOME = os.path.expanduser("~")
PROJ_DIR = os.path.join(HOME, ".claude", "projects")
CACHE_DIR = os.path.join(HOME, ".cache", "claudetop")
CACHE_PATH = os.path.join(CACHE_DIR, "sessions_cache.json")


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
    if not pids:
        return out

    try:
        raw = subprocess.check_output(
            ["ps", "-o", "pid=,tty=,lstart=,args=", "-p", ",".join(pids)], text=True
        )
    except subprocess.CalledProcessError:
        return out

    for line in raw.splitlines():
        # fields: pid tty <lstart: weekday mon day time year> args...
        parts = line.split(None, 6)
        if len(parts) < 7:
            continue
        pid, tty, wd, mon, day, time_ = parts[:6]
        year, _, cmd = parts[6].partition(" ")
        start = f"{wd} {mon} {day} {time_} {year}"
        cwd = os.path.realpath(f"/proc/{pid}/cwd")
        out.append({"pid": pid, "cwd": cwd, "tty": tty, "start": start, "cmd": cmd})
    return out


def kill_instance(pid: str, sig: str = "-TERM"):
    subprocess.run(["kill", sig, pid], check=False)


def delete_session(path: str):
    os.remove(path)


def _load_cache() -> dict:
    try:
        with open(CACHE_PATH, "r") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def _save_cache(cache: dict) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(cache, f)
    os.replace(tmp, CACHE_PATH)


def _empty_agg() -> dict:
    return {
        "msgs": 0,
        "ctx_tokens": 0,
        "total_output": 0,
        "total_input": 0,
        "first_ts": None,
        "last_ts": None,
        "cwd": None,
        "model": None,
        "git_branch": None,
        "offset": 0,
        "mtime": 0,
        "size": 0,
    }


def _apply_line(agg: dict, d: dict) -> None:
    ts = d.get("timestamp")
    if ts:
        if agg["first_ts"] is None:
            agg["first_ts"] = ts
        agg["last_ts"] = ts
    if d.get("cwd"):
        agg["cwd"] = d["cwd"]
    if d.get("gitBranch"):
        agg["git_branch"] = d["gitBranch"]
    if d.get("type") == "assistant":
        agg["msgs"] += 1
        m = d.get("message", {})
        agg["model"] = m.get("model", agg["model"])
        usage = m.get("usage")
        if usage:
            agg["total_output"] += usage.get("output_tokens", 0)
            agg["total_input"] += usage.get("input_tokens", 0)
            agg["ctx_tokens"] = (
                usage.get("input_tokens", 0)
                + usage.get("cache_read_input_tokens", 0)
                + usage.get("cache_creation_input_tokens", 0)
            )


def _scan_new_lines(path: str, start_offset: int):
    """Read complete lines from start_offset to EOF. Stops before a
    trailing partial line (file still being written) so offset only
    ever advances past fully-written lines."""
    lines = []
    end_offset = start_offset
    with open(path, "r", errors="ignore") as f:
        f.seek(start_offset)
        while True:
            line = f.readline()
            if not line or not line.endswith("\n"):
                break
            lines.append(line)
            end_offset = f.tell()
    return lines, end_offset


def parse_session(path: str, cache: dict) -> dict:
    """Parse a session file incrementally: reuse cached aggregate for
    bytes already seen, only read/parse lines appended since last run."""
    try:
        st = os.stat(path)
    except OSError:
        return None
    mtime, size = st.st_mtime, st.st_size

    entry = cache.get(path)
    if not (entry and entry["mtime"] == mtime and entry["size"] == size):
        if entry and entry["offset"] <= size and entry["mtime"] <= mtime:
            agg = dict(entry)
            start_offset = agg["offset"]
        else:
            agg = _empty_agg()
            start_offset = 0

        lines, end_offset = _scan_new_lines(path, start_offset)
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            _apply_line(agg, d)

        agg["offset"] = end_offset
        agg["mtime"] = mtime
        agg["size"] = size
        cache[path] = agg
        entry = agg

    return {
        "msgs": entry["msgs"],
        "ctx_tokens": entry["ctx_tokens"],
        "total_output": entry["total_output"],
        "total_input": entry["total_input"],
        "first_ts": entry["first_ts"],
        "last_ts": entry["last_ts"],
        "cwd": entry["cwd"],
        "model": entry["model"],
        "git_branch": entry["git_branch"],
        "size": size,
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
    cache = _load_cache()
    sessions_list = list(all_sessions())

    by_dir = {}
    for pdir, sid, path in sessions_list:
        info = parse_session(path, cache)
        if info is None:
            continue
        info["session_id"] = sid
        by_dir.setdefault(pdir, []).append(info)

    live_paths = {path for _, _, path in sessions_list}
    for stale in cache.keys() - live_paths:
        del cache[stale]
    _save_cache(cache)

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

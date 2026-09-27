"""Cloud sync — saves, leaderboard scores, and profile push/pull.

Enabled only when settings["online_mode"] is True (or PLAYTREE_ONLINE=1) AND
an endpoint is configured: env PLAYTREE_SYNC_URL or settings["sync_url"].
PLAYTREE_OFFLINE=1 always disables everything (tests/CI).

Every function is a safe no-op when disabled and never raises. The *_async
variants run on daemon threads so the game loop never blocks on the network.

Endpoints (JSON over HTTP):
  GET/POST /saves/<slot>    {"save_time": float, "name": str, "data": {...}}
  GET/POST /leaderboard     {"entries": {category: [{name, score, time}]}}
  POST     /profile         {"name", "achievements", "dailies", "level", "round"}
Failed POSTs are queued in ~/.playtree/cloud/queue.json and retried on flush().
"""
import json
import os
import threading
import time
import urllib.error
import urllib.request

from src.save_system import SAVE_DIR, load_game, _slot_file

CLOUD_DIR = os.path.join(SAVE_DIR, "cloud")
QUEUE_FILE = os.path.join(CLOUD_DIR, "queue.json")
LEADERBOARD_FILE = os.path.join(SAVE_DIR, "leaderboards.json")
PROFILE_FILE = os.path.join(SAVE_DIR, "profile_push.json")
TIMEOUT = 3.0
MAX_QUEUE = 20

_lock = threading.Lock()


def resolve_endpoint(settings=None):
    url = os.environ.get("PLAYTREE_SYNC_URL") or (settings or {}).get("sync_url") or ""
    return str(url).strip().rstrip("/")


def is_enabled(settings=None):
    if os.environ.get("PLAYTREE_OFFLINE"):
        return False
    if not resolve_endpoint(settings):
        return False
    if os.environ.get("PLAYTREE_ONLINE"):
        return True
    return bool((settings or {}).get("online_mode", False))


# ---------- low-level HTTP ----------
def _request(endpoint, method, path, payload=None):
    url = endpoint + path
    body = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None


# ---------- offline queue ----------
def _ensure_dir():
    try:
        os.makedirs(CLOUD_DIR, exist_ok=True)
    except Exception:
        pass


def _enqueue(method, path, payload):
    try:
        _ensure_dir()
        queue = []
        if os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "r") as f:
                queue = json.load(f)
                if not isinstance(queue, list):
                    queue = []
        queue.append({"method": method, "path": path, "payload": payload,
                      "attempts": 0, "ts": time.time()})
        with open(QUEUE_FILE, "w") as f:
            json.dump(queue[-MAX_QUEUE:], f)
    except Exception:
        pass


def flush(settings=None):
    """Retry queued operations. Returns number of ops still failing."""
    endpoint = resolve_endpoint(settings)
    if not is_enabled(settings):
        return 0
    try:
        if not os.path.exists(QUEUE_FILE):
            return 0
        with open(QUEUE_FILE, "r") as f:
            queue = json.load(f)
        if not isinstance(queue, list):
            queue = []
    except Exception:
        return 0
    remaining = []
    for op in queue:
        result = _request(endpoint, op.get("method", "POST"),
                          op.get("path", ""), op.get("payload"))
        if result is None:
            op["attempts"] = op.get("attempts", 0) + 1
            if op["attempts"] < 5:
                remaining.append(op)
    try:
        with open(QUEUE_FILE, "w") as f:
            json.dump(remaining, f)
    except Exception:
        pass
    return len(remaining)


def flush_async(settings=None):
    if not is_enabled(settings):
        return
    t = threading.Thread(target=flush, args=(settings,), daemon=True)
    t.start()


# ---------- saves ----------
def push_save(slot=0, settings=None):
    endpoint = resolve_endpoint(settings)
    if not is_enabled(settings):
        return False
    try:
        mtime = os.path.getmtime(_slot_file(slot))
    except OSError:
        return False
    data = load_game(slot)
    if not data:
        return False
    payload = {"save_time": mtime, "name": data.get("name", ""), "data": data}
    if _request(endpoint, "POST", f"/saves/{slot}", payload) is None:
        _enqueue("POST", f"/saves/{slot}", payload)
        return False
    return True


def push_save_async(slot=0, settings=None):
    if not is_enabled(settings):
        return
    t = threading.Thread(target=push_save, args=(slot, settings), daemon=True)
    t.start()


def pull_save(slot=0, settings=None):
    """Return remote save if newer than the local slot file, else None."""
    endpoint = resolve_endpoint(settings)
    if not is_enabled(settings):
        return None
    remote = _request(endpoint, "GET", f"/saves/{slot}")
    if not remote or not isinstance(remote.get("data"), dict):
        return None
    try:
        local_mtime = os.path.getmtime(_slot_file(slot))
    except OSError:
        local_mtime = 0.0
    if float(remote.get("save_time", 0)) <= local_mtime:
        return None
    return remote


def adopt_save(slot, remote):
    """Back up the local slot and replace it with the remote data."""
    try:
        path = _slot_file(slot)
        if os.path.exists(path):
            with open(path, "rb") as src, open(path + ".cloud_bak", "wb") as dst:
                dst.write(src.read())
        with open(path, "w") as f:
            json.dump(remote["data"], f, indent=2)
        return True
    except Exception:
        return False


# ---------- leaderboard ----------
def push_scores(settings=None):
    endpoint = resolve_endpoint(settings)
    if not is_enabled(settings):
        return False
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        return False
    if _request(endpoint, "POST", "/leaderboard", data) is None:
        _enqueue("POST", "/leaderboard", data)
        return False
    return True


def push_scores_async(settings=None):
    if not is_enabled(settings):
        return
    t = threading.Thread(target=push_scores, args=(settings,), daemon=True)
    t.start()


def merge_entries(local, remote):
    """Union remote into local entries: per category, per name keep max score."""
    if not isinstance(remote, dict) or not isinstance(local, dict):
        return local if isinstance(local, dict) else {"entries": {}}
    l_entries = local.get("entries", {}) if isinstance(local.get("entries", {}), dict) else {}
    out = {cat: list(entries) for cat, entries in l_entries.items()
           if isinstance(entries, list)}
    for cat, entries in (remote.get("entries") or {}).items():
        if not isinstance(entries, list):
            continue
        bucket = out.setdefault(cat, [])
        for e in entries:
            if not isinstance(e, dict) or "name" not in e or "score" not in e:
                continue
            existing = next((x for x in bucket if x.get("name") == e["name"]), None)
            if existing is None:
                bucket.append(dict(e))
            else:
                existing["score"] = max(existing.get("score", 0), e.get("score", 0))
        bucket.sort(key=lambda x: x.get("score", 0), reverse=True)
        out[cat] = bucket[:50]
    return {"entries": out}


def pull_leaderboard(settings=None):
    """Fetch remote entries and merge into the local leaderboard file."""
    endpoint = resolve_endpoint(settings)
    if not is_enabled(settings):
        return False
    remote = _request(endpoint, "GET", "/leaderboard")
    if not remote:
        return False
    try:
        local = {}
        if os.path.exists(LEADERBOARD_FILE):
            with open(LEADERBOARD_FILE, "r") as f:
                local = json.load(f)
        merged = merge_entries(local, remote)
        os.makedirs(SAVE_DIR, exist_ok=True)
        with open(LEADERBOARD_FILE, "w") as f:
            json.dump(merged, f, indent=2)
        return True
    except Exception:
        return False


def pull_leaderboard_async(settings=None):
    if not is_enabled(settings):
        return
    t = threading.Thread(target=pull_leaderboard, args=(settings,), daemon=True)
    t.start()


# ---------- profile ----------
def push_profile(profile, settings=None):
    endpoint = resolve_endpoint(settings)
    if not is_enabled(settings):
        return False
    if _request(endpoint, "POST", "/profile", profile) is None:
        _enqueue("POST", "/profile", profile)
        return False
    return True


def push_profile_async(profile, settings=None):
    if not is_enabled(settings):
        return
    t = threading.Thread(target=push_profile, args=(profile, settings), daemon=True)
    t.start()

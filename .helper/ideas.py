#!/usr/bin/env python3
"""Suggestions box plumbing for the cloud helper (see .helper/HELPER.md). Run from the repository root.

  python3 .helper/ideas.py fetch                    # new ideas since the last run, one JSON object per line
  python3 .helper/ideas.py reply ID STATUS "TEXT"   # STATUS: added | later | declined   (writes replies.json)
  python3 .helper/ideas.py done                     # mark everything fetched as handled
  python3 .helper/ideas.py paused                   # "yes" if a grown-up paused the helper (.helper/PAUSED exists)
"""
import json, sys, time, urllib.request, pathlib, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOPIC = (ROOT / ".helper/topic.txt").read_text().strip()
STATE = ROOT / ".helper/state.json"
REPLIES = ROOT / "replies.json"


def load_state():
    try:
        st = json.loads(STATE.read_text())
    except Exception:
        st = {}
    st.setdefault("since", 0); st.setdefault("seen_upto", 0); st.setdefault("handled", [])
    if not st["since"]:
        st["since"] = int(time.time()) - 12 * 3600  # ntfy keeps messages about 12 hours
    return st


def fetch():
    st = load_state()
    raw = urllib.request.urlopen(f"https://ntfy.sh/{TOPIC}/json?poll=1&since={st['since']}", timeout=20).read().decode()
    newest = st["since"]
    for line in raw.splitlines():
        m = json.loads(line)
        if m.get("event") != "message":
            continue
        newest = max(newest, m["time"])
        try:
            idea = json.loads(m["message"])
        except Exception:
            continue
        iid, text = str(idea.get("id", ""))[:20], str(idea.get("text", ""))[:300]
        if iid and iid not in st["handled"]:
            print(json.dumps({"id": iid, "text": text}))
    st["seen_upto"] = newest
    STATE.write_text(json.dumps(st))


def reply(iid, status, text):
    assert status in ("added", "later", "declined"), "status must be added, later or declined"
    data = json.loads(REPLIES.read_text()) if REPLIES.exists() else {"replies": {}}
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")
    data.setdefault("replies", {})[iid] = {"status": status, "reply": text[:200], "at": now}
    data["updated"] = now
    REPLIES.write_text(json.dumps(data, indent=1))
    st = load_state()
    st["handled"] = (st["handled"] + [iid])[-500:]
    STATE.write_text(json.dumps(st))


def done():
    st = load_state()
    st["since"] = max(st["since"], st["seen_upto"])
    STATE.write_text(json.dumps(st))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "fetch": fetch()
    elif cmd == "reply": reply(sys.argv[2], sys.argv[3], sys.argv[4])
    elif cmd == "done": done()
    elif cmd == "paused": print("yes" if (ROOT / ".helper/PAUSED").exists() else "no")
    else: print(__doc__)

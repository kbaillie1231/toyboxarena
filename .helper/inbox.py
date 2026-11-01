#!/usr/bin/env python3
"""Run by the free GitHub Action every few minutes (.github/workflows/ideas-inbox.yml).
Looks at the suggestions relay for ideas the helper hasn't handled yet. If there are NEW ones, it rewrites
.helper/inbox.json; the Action then commits it, and that push wakes the Claude helper routine.
No AI runs here, so checking costs nothing."""
import json, pathlib, urllib.request, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOPIC = (ROOT / ".helper/topic.txt").read_text().strip()
INBOX = ROOT / ".helper/inbox.json"
try:
    st = json.loads((ROOT / ".helper/state.json").read_text())
except Exception:
    st = {}
since = st.get("since") or int(time.time()) - 12 * 3600
handled = set(st.get("handled", []))
raw = urllib.request.urlopen(f"https://ntfy.sh/{TOPIC}/json?poll=1&since={since}", timeout=20).read().decode()
ids = []
for line in raw.splitlines():
    m = json.loads(line)
    if m.get("event") != "message":
        continue
    try:
        iid = str(json.loads(m["message"]).get("id", ""))[:20]
    except Exception:
        continue
    if iid and iid not in handled and iid not in ids:
        ids.append(iid)
try:
    old = set(json.loads(INBOX.read_text()).get("waiting", []))
except Exception:
    old = set()
if set(ids) - old:  # only brand-new ideas wake the helper (no commit otherwise)
    INBOX.write_text(json.dumps({"waiting": ids, "at": int(time.time())}))
    print(f"{len(set(ids) - old)} new idea(s): waking the helper")
else:
    print("no new ideas")

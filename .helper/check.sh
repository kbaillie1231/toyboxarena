#!/bin/sh
# Safety check before publishing: every inline <script> in index.html must parse, and the JSON files must be valid.
# Uses Node (cloud) or JavaScriptCore (Mac). Exit 0 = OK.
cd "$(dirname "$0")/.." || exit 1
TMP=$(mktemp -d)
python3 - "$TMP" <<'PY'
import re, sys, pathlib
html = pathlib.Path("index.html").read_text()
blocks = re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S)
for i, b in enumerate(blocks):
    pathlib.Path(sys.argv[1], f"s{i}.js").write_text(b)
print(f"{len(blocks)} inline scripts")
PY
FAIL=0
JSC=/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc
for f in "$TMP"/*.js; do
  if command -v node >/dev/null 2>&1; then
    node --check "$f" 2>"$TMP/err" || { echo "SYNTAX ERROR in $(basename "$f"):"; head -5 "$TMP/err"; FAIL=1; }
  elif [ -x "$JSC" ]; then
    OUT=$("$JSC" -e "try { checkSyntax('$f'); } catch (e) { print('SYNTAX ERROR: ' + e); }"); [ -n "$OUT" ] && { echo "$OUT"; FAIL=1; }
  else
    echo "No JavaScript checker found (need node)"; FAIL=1
  fi
done
for j in manifest.json replies.json .helper/state.json; do
  python3 -c "import json; json.load(open('$j'))" 2>/dev/null || { echo "BAD JSON: $j"; FAIL=1; }
done
rm -rf "$TMP"
[ $FAIL = 0 ] && echo "check: OK"
exit $FAIL

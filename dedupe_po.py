"""Remove duplicate messages from a .po file (keeps the FIRST one).
Works even when entries are glued together without a blank line.
Usage (Windows cmd, project root, .venv active):
    python dedupe_po.py locale\\fa\\LC_MESSAGES\\django.po
A backup django.po.bak is saved first."""
import re
import shutil
import sys


def parse(lines):
    """Split into entries. An entry = its comment lines + msgctxt/msgid/msgstr lines."""
    entries, cur, state = [], None, "start"
    for line in lines:
        s = line.rstrip("\n")
        is_comment = s.startswith("#")
        starts_new = s.startswith("msgctxt ") or (
            s.startswith("msgid ") and state != "ctxt")
        if cur is None:
            cur = {"lines": [], "ctx": [], "id": [], "obsolete": False}
            state = "start"
        # a comment or a new msgctxt/msgid after msgstr = next entry begins
        if state == "str" and (is_comment or starts_new) and cur["id"] is not None:
            entries.append(cur)
            cur = {"lines": [], "ctx": [], "id": [], "obsolete": False}
            state = "start"
        cur["lines"].append(line)
        if s.startswith("#~"):
            cur["obsolete"] = True
            continue
        if is_comment:
            continue
        if s.startswith("msgctxt "):
            state = "ctxt"
        elif s.startswith("msgid_plural "):
            state = "plural"
        elif s.startswith("msgid "):
            state = "id"
        elif s.startswith("msgstr"):
            state = "str"
        if s.startswith('"') or state in ("ctxt", "id") and "\"" in s:
            m = re.search(r'"(.*)"\s*$', s)
            if m and state == "ctxt":
                cur["ctx"].append(m.group(1))
            elif m and state == "id":
                cur["id"].append(m.group(1))
    if cur and cur["lines"]:
        entries.append(cur)
    return entries


def main(path):
    shutil.copyfile(path, path + ".bak")
    with open(path, encoding="utf-8", newline="") as f:
        lines = f.read().replace("\r\n", "\n").splitlines(True)
    seen, out, removed = set(), [], []
    for e in parse(lines):
        body = "".join(e["lines"])
        if e["obsolete"] or not any(l.startswith("msgid ") for l in e["lines"]):
            out.append(body.rstrip("\n") + "\n")
            continue
        key = ("".join(e["ctx"]), "".join(e["id"]))
        if key in seen:
            removed.append(key[1])
            continue
        seen.add(key)
        out.append(body.rstrip("\n") + "\n")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out))
    print("removed %d duplicates:" % len(removed))
    for m in removed:
        print("  -", m[:70])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])

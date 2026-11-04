"""Repairs a Django .po file and (optionally) adds translations.

    python merge_po.py locale\\fa\\LC_MESSAGES\\django.po                (repair only)
    python merge_po.py locale\\fa\\LC_MESSAGES\\django.po po_add.txt     (repair + add new translations)

It fixes:  duplicate msgids (keeps the one that has a translation, the last filled one wins),
           entries with TWO msgstr lines (the last one wins), stray text/comments pasted between entries,
           fuzzy flags (removed, so translations are used).
A backup  django.po.bak  is written first.
"""
import re
import shutil
import sys


def unq(line):
    m = re.search(r'"(.*)"\s*$', line)
    v = m.group(1) if m else ""
    # a stray quote inside the text would break msgfmt: escape it
    return re.sub(r'(?<!\\)"', r'\\"', v)


def parse(text):
    """Line based parser: every  msgid "..."  line starts a new entry, blank lines do not matter."""
    entries, cur, pending = [], None, []
    state = None
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.rstrip()
        if line.startswith("msgid_plural "):
            cur["plural_id"] = unq(line)
            state = "pid"
        elif line.startswith("msgid "):
            cur = {"ctx": None, "id": unq(line), "plural_id": None, "str": "", "plural": {
            }, "refs": [], "flags": []}
            for c in pending:
                if c.startswith("#:") or c.startswith("#."):
                    cur["refs"].append(c)
            pending = []
            entries.append(cur)
            state = "id"
        elif line.startswith("msgctxt "):
            pending_ctx = unq(line)
            cur = None
            pending.append("CTX:" + pending_ctx)
            state = None
        elif line.startswith("msgstr["):
            n = int(re.match(r"msgstr\[(\d+)\]", line).group(1))
            cur["plural"][n] = unq(line)
            state = ("pl", n)
        elif line.startswith("msgstr"):
            cur["str"] = unq(line)
            state = "str"       # a second msgstr line replaces the first
        elif line.startswith('"') and cur is not None:
            v = unq(line)
            if state == "id":
                cur["id"] += v
            elif state == "pid":
                cur["plural_id"] += v
            elif state == "str":
                cur["str"] += v
            elif isinstance(state, tuple):
                cur["plural"][state[1]] += v
        elif line.startswith("#"):
            if line.startswith("#~"):
                continue
            pending.append(line)
            state = None if not line.startswith('"') else state
        # anything else (stray text) is ignored
    # contexts
    return entries


def attach_ctx(text, entries):
    """re-read msgctxt: simple second pass, in order"""
    ctxs, last = [], None
    for raw in text.split("\n"):
        if raw.startswith("msgctxt "):
            last = unq(raw)
        elif raw.startswith("msgid ") and not raw.startswith("msgid_plural"):
            ctxs.append(last)
            last = None
    for e, c in zip(entries, ctxs):
        e["ctx"] = c


def esc(s):
    return s  # values are kept exactly as they were written (already escaped)


def read_add(path):
    text = open(path, encoding="utf-8-sig").read()
    return re.findall(r'^msgid "((?:[^"\\]|\\.)*)"\s*\nmsgstr "((?:[^"\\]|\\.)*)"', text, flags=re.M)


def main():
    po = sys.argv[1]
    raw = open(po, encoding="utf-8-sig").read()
    shutil.copyfile(po, po + ".bak")
    entries = parse(raw)
    attach_ctx(raw, entries)

    header = None
    best, order = {}, []
    for e in entries:
        if e["id"] == "" and e["ctx"] is None:
            header = e if header is None else header
            if header is e:
                continue
        k = (e["ctx"], e["id"])
        filled = bool(e["str"]) or any(e["plural"].values())
        if k not in best:
            order.append(k)
            best[k] = e
        else:
            old = best[k]
            if filled or not (old["str"] or any(old["plural"].values())):
                e["refs"] = old["refs"] or e["refs"]
                best[k] = e

    added = 0
    if len(sys.argv) > 2:
        for mid, mstr in read_add(sys.argv[2]):
            k = (None, mid)
            if k not in best:
                order.append(k)
                added += 1
                best[k] = {"ctx": None, "id": mid, "plural_id": None,
                           "str": mstr, "plural": {}, "refs": [], "flags": []}
            elif best[k]["plural_id"] is None:
                best[k]["str"] = mstr

    hdr = 'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"'
    if header:
        hdr = 'msgid ""\nmsgstr "%s"' % header["str"] if False else None
    # keep the original header lines exactly
    m = re.search(
        r'^msgid ""\s*\nmsgstr ""\s*\n((?:"[^\n]*"\s*\n)+)', raw, flags=re.M)
    hdr = 'msgid ""\nmsgstr ""\n' + \
        (m.group(1).rstrip("\n") if m else '"Content-Type: text/plain; charset=UTF-8\\n"')
    out = [hdr]
    for k in order:
        e = best[k]
        lines = list(e["refs"])
        if e["ctx"] is not None:
            lines.append('msgctxt "%s"' % e["ctx"])
        lines.append('msgid "%s"' % e["id"])
        if e["plural_id"] is not None:
            lines.append('msgid_plural "%s"' % e["plural_id"])
            for n in sorted(e["plural"]):
                lines.append('msgstr[%d] "%s"' % (n, e["plural"][n]))
        else:
            lines.append('msgstr "%s"' % e["str"])
        out.append("\n".join(lines))
    open(po, "w", encoding="utf-8", newline="\n").write("\n\n".join(out) + "\n")
    print("entries: %d   new: %d   (backup: %s.bak)" % (len(order), added, po))


main()

#!/usr/bin/env python3
# md_snapshot.py
# Grab the last 26 lines from a log, split into two sets of 13,
# format Markdown and copy to clipboard (fallback prints to stdout).

import argparse
import os
import shutil
from datetime import datetime, timezone

def now_sigil():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def tail_lines(path, n):
    """Efficiently read last n lines of file."""
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            filesize = f.tell()
            blocksize = 4096
            data = b""
            while filesize > 0 and data.count(b"\n") <= n:
                read_size = min(blocksize, filesize)
                f.seek(filesize - read_size, os.SEEK_SET)
                chunk = f.read(read_size)
                data = chunk + data
                filesize -= read_size
            lines = data.splitlines()[-n:]
            return [ln.decode("utf-8", errors="replace") for ln in lines]
    except FileNotFoundError:
        return []
    except Exception as e:
        print("tail error:", e)
        return []

def build_md(logpath, set1, set2):
    sig = now_sigil()
    header = f"# RFI-IRFOS Snapshot\n\n**Snapshot Sigil:** `{sig}`\n**Source log:** `{logpath}`\n\n"
    body = "```text\n# SET ⟨older 13⟩\n" + ("\n".join(set1) if set1 else "(no lines)") + "\n\n# SET ⟨latest 13⟩\n" + ("\n".join(set2) if set2 else "(no lines)") + "\n```\n"
    footer = f"\n*Copied: {sig}*\n"
    return header + body + footer

def copy_to_clipboard(text):
    # Try python module pyperclip first
    try:
        import pyperclip
        pyperclip.copy(text)
        return True
    except Exception:
        pass
    # Try wl-copy (Wayland)
    if shutil.which("wl-copy"):
        try:
            p = os.popen("wl-copy", "w")
            p.write(text)
            p.close()
            return True
        except Exception:
            pass
    # Try xclip (X11)
    if shutil.which("xclip"):
        try:
            p = os.popen("xclip -selection clipboard", "w")
            p.write(text)
            p.close()
            return True
        except Exception:
            pass
    # Try xsel
    if shutil.which("xsel"):
        try:
            p = os.popen("xsel --clipboard --input", "w")
            p.write(text)
            p.close()
            return True
        except Exception:
            pass
    return False

def main():
    p = argparse.ArgumentParser(description="Grab 2x13 lines from log and copy MD to clipboard")
    p.add_argument("--log", "-l", default=os.path.expanduser("~/Desktop/session.log"), help="path to log file")
    p.add_argument("--n", "-n", type=int, default=13, help="lines per set (default 13)")
    p.add_argument("--print-only", action="store_true", help="only print MD, do not copy")
    args = p.parse_args()

    total = args.n * 2
    lines = tail_lines(args.log, total)
    # if fewer lines than requested, pad or duplicate
    if len(lines) < total:
        # try reading all available and left-pad with empty placeholders
        pad = ["(no line)"] * (total - len(lines))
        lines = pad + lines

    # split: older first, newest last
    set1 = lines[:args.n]   # older 13
    set2 = lines[args.n:]   # newest 13
    md = build_md(args.log, set1, set2)

    if args.print_only:
        print(md)
        return

    did = copy_to_clipboard(md)
    if did:
        print("[md_snapshot] Markdown copied to clipboard. Drop it anywhere (CTRL+V).")
    else:
        print("[md_snapshot] Clipboard unavailable — printing to stdout below:\n")
        print(md)

if __name__ == "__main__":
    main()


#!/usr/bin/env python3
"""
Ternary Handshake Protocol (THP) — plug-and-play Python executable

Purpose
  - Establish a minimal, cryptographically signed "handshake" between two agents or between an agent and a repo state.
  - Encode a ternary intent/state: -1=reject, 0=tend/observe, +1=act/affirm.
  - Emit a durable, human-readable hyperlink for continuity.

Why this file works well in a repo root
  - Single-file, zero third-party deps.
  - Can run locally or inside CI (GitHub Actions). 
  - Emits JSON and Markdown so humans and machines both get value.

Usage
  - CLI: `python ternary_handshake.py --repo rfi-irfos/ternlang --branch main --state +1 --who "simeon, albert" --why "session start"`
  - Import: `from ternary_handshake import handshake; doc = handshake(...)`

Security
  - Optional HMAC signing with THP_SECRET env var. If unset, the handshake is unsigned but still hashed for integrity.

Outputs
  - JSON document to stdout
  - Optional `HANDSHAKE.md` append with a one-line Markdown link

License: MIT
"""
from __future__ import annotations

import argparse
import dataclasses as dc
import datetime as dt
import hashlib
import hmac
import json
import os
import socket
import sys
from typing import Literal, Optional

Ternary = Literal[-1, 0, 1]

EMOJI = {
    -1: "🟜",
     0: "🟫",
     1: "⬛",
}

@dc.dataclass
class HandshakeDoc:
    version: str
    repo: str
    branch: str
    commit: Optional[str]
    who: list[str]
    why: str
    state: Ternary
    stamp_z: str
    host: str
    session_id: Optional[str]
    hyperlink: str
    signature: Optional[str]
    digest: str

    def to_json(self) -> str:
        return json.dumps(dc.asdict(self), ensure_ascii=False, sort_keys=True)

    def to_markdown(self) -> str:
        flag = EMOJI.get(self.state, "🟫")
        title = f"{flag} handshake @{self.branch} {self.stamp_z}"
        return (
            f"- {title} → [{self.repo}]({self.hyperlink})\n"
            f"  - reason: {self.why}\n"
            f"  - by: {', '.join(self.who)}"
        )


def _now_z() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _infer_repo(default: str = "") -> str:
    gh = os.getenv("GITHUB_REPOSITORY")
    if gh:
        return gh
    return default


def _infer_branch(default: str = "main") -> str:
    gh_ref = os.getenv("GITHUB_REF_NAME") or os.getenv("GITHUB_REF")
    if gh_ref:
        return gh_ref.split("/")[-1]
    return default


def _infer_commit() -> Optional[str]:
    return os.getenv("GITHUB_SHA")


def _hyperlink(repo: str, branch: str) -> str:
    return f"https://github.com/{repo}/tree/{branch}"


def _digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _signature(payload: bytes, key: Optional[bytes]) -> Optional[str]:
    if not key:
        return None
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def handshake(
    repo: str,
    branch: str = "main",
    state: Ternary = 0,
    who: Optional[list[str]] = None,
    why: str = "",
    session_id: Optional[str] = None,
    commit: Optional[str] = None,
) -> HandshakeDoc:
    who = who or []
    stamp = _now_z()
    host = socket.gethostname()
    commit = commit or _infer_commit()
    link = _hyperlink(repo, branch)

    payload = json.dumps(
        {
            "version": "thp/1.0",
            "repo": repo,
            "branch": branch,
            "commit": commit,
            "who": who,
            "why": why,
            "state": state,
            "stamp_z": stamp,
            "host": host,
            "session_id": session_id,
            "hyperlink": link,
        },
        separators=(",", ":"),
        sort_keys=True,
        ensure_ascii=False,
    ).encode("utf-8")

    digest = _digest(payload)
    key = os.getenv("THP_SECRET").encode("utf-8") if os.getenv("THP_SECRET") else None
    signature = _signature(payload, key)

    return HandshakeDoc(
        version="thp/1.0",
        repo=repo,
        branch=branch,
        commit=commit,
        who=who,
        why=why,
        state=state,
        stamp_z=stamp,
        host=host,
        session_id=session_id,
        hyperlink=link,
        signature=signature,
        digest=digest,
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ternary Handshake Protocol (THP)")
    p.add_argument("--repo", default=_infer_repo(), help="owner/name; defaults to $GITHUB_REPOSITORY if set")
    p.add_argument("--branch", default=_infer_branch(), help="branch name; defaults to $GITHUB_REF_NAME or main")
    p.add_argument("--state", default="0", choices=["-1", "0", "+1"], help="-1 reject, 0 tend, +1 affirm")
    p.add_argument("--who", default="", help="comma-separated operator ids")
    p.add_argument("--why", default="", help="short reason string")
    p.add_argument("--session", default=os.getenv("THP_SESSION_ID", ""), help="session correlation id")
    p.add_argument("--md", action="store_true", help="also append one-line markdown to HANDSHAKE.md in repo root")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if not args.repo:
        print("error: --repo is required if $GITHUB_REPOSITORY is not set", file=sys.stderr)
        return 2

    who = [w.strip() for w in args.who.split(",") if w.strip()] if args.who else []
    state_map = {"-1": -1, "0": 0, "+1": 1}
    doc = handshake(
        repo=args.repo,
        branch=args.branch,
        state=state_map[args.state],
        who=who,
        why=args.why,
        session_id=args.session or None,
    )

    print(doc.to_json())

    if args.md:
        line = doc.to_markdown()
        try:
            with open("HANDSHAKE.md", "a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except Exception as e:
            print(f"warn: failed to write HANDSHAKE.md: {e}", file=sys.stderr)

    if doc.state == -1:
        return 10
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

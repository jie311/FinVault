"""Privacy and secret scanning helpers for the anonymous release."""

from __future__ import annotations

import re
import base64
from dataclasses import dataclass


@dataclass(frozen=True)
class ScanIssue:
    """One privacy or secret scanning issue."""

    kind: str
    line: int
    excerpt: str


PATTERNS: dict[str, re.Pattern[str]] = {
    "email_address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "mainland_id_number": re.compile(r"\b\d{17}[0-9Xx]\b"),
    "mainland_phone_number": re.compile(r"\b1[3-9]\d{9}\b"),
    "openai_key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._-]{20,}\b", re.I),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "api_key_assignment": re.compile(r"(?i)\b(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"\s]{8,}"),
}

BASE64_TOKEN = re.compile(r"(?<![A-Za-z0-9+/=])(?:[A-Za-z0-9+/]{40,}={0,2})(?![A-Za-z0-9+/=])")


def scan_text(text: str, max_issues: int = 20) -> list[ScanIssue]:
    """Return common privacy, secret, and non-ASCII issues in text."""
    issues: list[ScanIssue] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in PATTERNS.items():
            match = pattern.search(line)
            if match:
                excerpt = line[max(match.start() - 30, 0) : match.end() + 30]
                issues.append(ScanIssue(kind=kind, line=line_no, excerpt=excerpt))
                if len(issues) >= max_issues:
                    return issues
        for token in BASE64_TOKEN.findall(line):
            decoded = _decode_printable_base64(token)
            if decoded is None:
                continue
            for kind, pattern in PATTERNS.items():
                match = pattern.search(decoded)
                if match:
                    excerpt = decoded[max(match.start() - 30, 0) : match.end() + 30]
                    issues.append(ScanIssue(kind=f"base64_{kind}", line=line_no, excerpt=excerpt))
                    if len(issues) >= max_issues:
                        return issues
    return issues


def _decode_printable_base64(token: str) -> str | None:
    try:
        padded = token + "=" * ((4 - len(token) % 4) % 4)
        raw = base64.b64decode(padded, validate=True)
        decoded = raw.decode("utf-8")
    except Exception:
        return None
    if not decoded:
        return None
    printable = sum(1 for ch in decoded if ch == "\n" or ch == "\t" or 32 <= ord(ch) <= 126)
    if printable / max(len(decoded), 1) < 0.9:
        return None
    return decoded

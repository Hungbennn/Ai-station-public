import os
from datetime import datetime, timezone
from pathlib import Path


def tram_home() -> Path:
    p = Path(os.environ.get("TRAM_HOME") or Path.home() / ".tram")
    p.mkdir(parents=True, exist_ok=True)
    return p


def goc_repo() -> Path:
    return Path(os.environ.get("TRAM_REPO") or Path(__file__).resolve().parents[1])


def doc_luc(s: str) -> datetime:
    d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d.astimezone(timezone.utc)


def bay_gio() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

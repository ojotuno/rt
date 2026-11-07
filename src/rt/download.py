"""Download a file over HTTP(S)."""

from __future__ import annotations

import os
import posixpath
import urllib.error
import urllib.parse
import urllib.request

from . import log
from .errors import RtError

CHUNK = 64 * 1024


def filename_for(url: str, content_disposition_name: str | None) -> str:
    name = content_disposition_name or posixpath.basename(urllib.parse.urlparse(url).path)
    name = os.path.basename(name.replace("\\", "/")).strip()
    return name if name not in ("", ".", "..") else "download"


def download(url: str, dest_dir: str) -> str:
    """Download url into dest_dir. Returns the saved file path."""
    log.info(f"Downloading {url}")
    request = urllib.request.Request(url, headers={"User-Agent": "rt"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            name = filename_for(response.geturl(), response.headers.get_filename())
            path = os.path.join(dest_dir, name)
            with open(path, "wb") as out:
                while chunk := response.read(CHUNK):
                    out.write(chunk)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise RtError(f"download failed: {url}: {exc}") from exc
    log.info(f"Saved {name} ({os.path.getsize(path)} bytes)")
    return path

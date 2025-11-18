import os
import re
import shutil
import tempfile
import math
import logging
import subprocess
import zipfile
from urllib.parse import urlparse, unquote
from typing import Dict, Tuple, Optional

from app.core.config import settings

from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Regex patterns for summary lines we want to extract
# Example lines:
# ; total filament cost = 4502.55
# ; estimated printing time (normal mode) = 2h 52m 11s
# ; total toolchanges = 7
COST_RE = re.compile(r";\s*total filament cost\s*=\s*([\d.]+)", re.I)
EST_TIME_RE = re.compile(r";\s*estimated printing time(?:\s*\([^)]+\))?\s*=\s*([0-9hms\s:]+)", re.I)
TOOL_CHANGE_RE = re.compile(r";\s*total toolchanges\s*=\s*(\d+)", re.I)


def _parse_time_to_seconds(timestr: str) -> Optional[float]:
    """Parse a time string like '1h 23m', '83m', '1:23:45', '2h 52m 11s' and return
    the total time in hours as a float. Returns None if parsing fails.
    Note: function name kept for compatibility but returns hours (float).
    """
    if not timestr:
        return None
    timestr = timestr.strip()

    total_seconds = 0

    # colon formats like 1:23:45 or 23:45
    if ":" in timestr:
        parts = [p for p in timestr.split(":")]
        try:
            parts = [int(p) for p in parts]
        except ValueError:
            return None
        if len(parts) == 3:
            h, m, s = parts
        elif len(parts) == 2:
            h = 0
            m, s = parts
        else:
            return None
        total_seconds = h * 3600 + m * 60 + s
        return total_seconds / 3600.0

    # textual like '1h 23m 10s' or '2h 52m'
    hours = re.search(r"(\d+)\s*h", timestr)
    mins = re.search(r"(\d+)\s*m", timestr)
    secs = re.search(r"(\d+)\s*s", timestr)
    if hours:
        total_seconds += int(hours.group(1)) * 3600
    if mins:
        total_seconds += int(mins.group(1)) * 60
    if secs:
        total_seconds += int(secs.group(1))

    if total_seconds > 0:
        return total_seconds / 3600.0

    # final numeric minutes fallback like '83m'
    m = re.match(r"^(\d+)\s*m$", timestr)
    if m:
        return int(m.group(1)) * 60 / 3600.0

    return None


def parse_gcode_metrics(gcode_text: str) -> Dict:
    """Extract three summary metrics from gcode text:

    - cost: float (from '; total filament cost = <float>')
    - time: float hours (from '; estimated printing time ... = <string>' converted to hours)
    - tool_changes: int (from '; total toolchanges = <int>')

    Returns a dict: {"cost": float|None, "time": float|None, "tool_changes": int}
    """
    metrics: Dict = {}

    # cost
    cm = COST_RE.search(gcode_text)
    cost = float(cm.group(1)) if cm and cm.group(1) else None

    # estimated time (convert to hours float)
    tm = EST_TIME_RE.search(gcode_text)
    time_hours = None
    if tm and tm.group(1):
        time_hours = _parse_time_to_seconds(tm.group(1))

    # tool changes
    tmch = TOOL_CHANGE_RE.search(gcode_text)
    tool_changes = int(tmch.group(1)) if tmch and tmch.group(1) else 0

    metrics.update({
        "cost": float(round(cost, 3)) if cost is not None else None,
        "time": round(time_hours, 3) if time_hours is not None else None,
        "tool_changes": int(tool_changes),
    })

    return metrics


def _gdrive_direct_url(file_url: str) -> str | None:
    """
    If the url is a Google Drive share link, return a direct-download URL (uc?export=download&id=...).
    Otherwise, return None.
    Supports:
      - https://drive.google.com/file/d/FILEID/view?usp=sharing
      - https://drive.google.com/open?id=FILEID
      - https://drive.google.com/uc?id=FILEID&export=download
    """
    parsed = urlparse(file_url)
    if parsed.netloc.endswith("drive.google.com"):
        # /file/d/FILEID/...
        m = re.search(r"/file/d/([^/]+)", parsed.path)
        if m:
            file_id = m.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        # /open?id=FILEID or ?id=FILEID
        q = parsed.query
        m = re.search(r"id=([^&]+)", q)
        if m:
            file_id = m.group(1)
            return f"https://drive.google.com/uc?export=download&id={file_id}"
    return None

def download_3mf(file_url: str) -> str:
    """
    Download a .3mf from an HTTP(S) URL or s3:// URL to a temporary file.
    Returns local filepath (string). Raises HTTPException on invalid input/failure.
    Validation strategy: stream-download with size limit, then verify file is a ZIP
    containing [Content_Types].xml (typical for OPC/3MF).
    """
    # Lazy import requests (like original) to keep optional deps
    try:
        import requests  # type: ignore
    except Exception:
        requests = None

    max_mb = float(os.environ.get("MAX_UPLOAD_MB", "200"))
    tmp_dir = os.environ.get("TMP_DIR", tempfile.gettempdir())
    parsed = urlparse(file_url)

    # -- s3:// handling (keep previous behavior) --
    if parsed.scheme == "s3":
        try:
            import boto3  # type: ignore
        except Exception:
            logger.error("boto3 not available to handle s3:// URLs; please provide a presigned HTTPS URL or install boto3")
            raise HTTPException(status_code=400, detail="boto3 not installed; cannot handle s3:// URLs. Provide a presigned HTTPS URL or install boto3 on the server.")
        try:
            s3 = boto3.client("s3")
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
            fd, tmp_path = tempfile.mkstemp(suffix=".3mf", dir=tmp_dir)
            os.close(fd)
            with open(tmp_path, "wb") as f:
                s3.download_fileobj(bucket, key, f)
            size_mb = os.path.getsize(tmp_path) / (1024 * 1024)
            if size_mb > max_mb:
                os.remove(tmp_path)
                raise HTTPException(status_code=400, detail="File exceeds maximum allowed size")
            # Validate structure (zip + [Content_Types].xml)
            if not zipfile.is_zipfile(tmp_path):
                os.remove(tmp_path)
                raise HTTPException(status_code=400, detail="Downloaded file is not a valid 3MF (not a ZIP container)")
            with zipfile.ZipFile(tmp_path, "r") as z:
                if "[Content_Types].xml" not in z.namelist():
                    os.remove(tmp_path)
                    raise HTTPException(status_code=400, detail="Downloaded file is not a valid 3MF (missing [Content_Types].xml)")
            return tmp_path
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Failed to download from s3: %s", e)
            raise HTTPException(status_code=400, detail=f"Failed to download s3 object: {e}")

    # -- If Google Drive shared link, transform to direct download --
    gdrive_direct = _gdrive_direct_url(file_url)
    if gdrive_direct:
        file_url = gdrive_direct
        parsed = urlparse(file_url)

    # -- HTTP(S) streaming download --
    if requests is None:
        # Fallback: require requests for http downloads to simplify streaming logic
        logger.error("requests is required for HTTP downloads but is not installed")
        raise HTTPException(status_code=500, detail="Server misconfiguration: 'requests' library required to download HTTP URLs")

    try:
        resp = requests.get(file_url, stream=True, timeout=30, allow_redirects=True)
    except Exception as e:
        logger.exception("Failed to GET file URL: %s", e)
        raise HTTPException(status_code=400, detail=f"Failed to download file: {e}")

    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to download file: status {resp.status_code}")

    # create temp file
    fd, tmp_path = tempfile.mkstemp(suffix=".3mf", dir=tmp_dir)
    os.close(fd)

    size = 0
    try:
        with open(tmp_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    size += len(chunk)
                    if (size / (1024 * 1024)) > max_mb:
                        f.close()
                        os.remove(tmp_path)
                        raise HTTPException(status_code=400, detail="File exceeds maximum allowed size")
        # after fully written, validate ZIP + OPC structure
        if not zipfile.is_zipfile(tmp_path):
            os.remove(tmp_path)
            raise HTTPException(status_code=400, detail="Downloaded file is not a valid 3MF (not a ZIP container)")

        try:
            with zipfile.ZipFile(tmp_path, "r") as z:
                namelist = z.namelist()
                if "[Content_Types].xml" not in namelist:
                    os.remove(tmp_path)
                    raise HTTPException(status_code=400, detail="Downloaded file is not a valid 3MF (missing [Content_Types].xml)")
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error inspecting downloaded zip file: %s", e)
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise HTTPException(status_code=400, detail=f"Failed to validate downloaded file: {e}")

        return tmp_path

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error writing downloaded file: %s", e)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=400, detail=f"Failed to save downloaded file: {e}")


def run_prusaslicer_and_parse_metrics(model_3mf_path: str) -> Dict:
    """Run PrusaSlicer CLI to export G-code for the given 3MF and parse metrics.

    Returns a metrics dict.
    Raises HTTPException on failures/timeouts.
    """
    # Prefer config values from Settings so .env entries loaded by app.core.config
    prusa_bin = settings.PRUSA_SLICER_BIN
    if not prusa_bin:
        raise HTTPException(status_code=500, detail="PRUSA_SLICER_BIN not configured")

    profile = settings.SLICER_PROFILE_PATH
    timeout = int(settings.SLICE_TIMEOUT_SEC or 300)
    tmp_dir = settings.TMP_DIR or tempfile.gettempdir()

    base_name = os.path.splitext(os.path.basename(model_3mf_path))[0]
    gcode_path = os.path.join(tmp_dir, f"{base_name}.gcode")

    cmd = [prusa_bin]
    if profile:
        cmd += ["--load", profile]
    cmd += ["--export-gcode", "--merge", "-o", gcode_path, model_3mf_path]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        # attempt to kill and cleanup
        logger.exception("PrusaSlicer timed out after %s seconds", timeout)
        raise HTTPException(status_code=504, detail="Slicing timed out")
    except Exception as e:
        logger.exception("Failed to start PrusaSlicer: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to run slicer: {e}")

    # log limited stdout/stderr
    out = (proc.stdout or "")[:4000]
    err = (proc.stderr or "")[:4000]
    if proc.returncode != 0:
        logger.error("PrusaSlicer failed (%s). stdout=%s stderr=%s", proc.returncode, out, err)
        raise HTTPException(status_code=500, detail=f"Slicer failed: {err[:300]}")

    # ensure gcode exists
    if not os.path.exists(gcode_path):
        logger.error("Expected gcode not found at %s", gcode_path)
        raise HTTPException(status_code=500, detail="Slicer did not produce gcode")

    # read gcode (limit read size to avoid huge files)
    text = ""
    try:
        with open(gcode_path, "r", errors="ignore") as f:
            # read up to first 50MB
            text = f.read(50 * 1024 * 1024)
    except Exception as e:
        logger.exception("Failed reading gcode: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to read gcode: {e}")

    # parse metrics
    metrics = parse_gcode_metrics(text)
    metrics["slicer_profile"] = os.path.basename(profile) if profile else None
    metrics["raw_gcode_path"] = gcode_path

    return metrics
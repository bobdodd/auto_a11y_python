"""
MP4/M4A media duration extraction utility.

Extracts video/audio duration from MP4 files by parsing the ISO Base Media
File Format (ISO 14496-12) atom structure. Uses only Python standard library
-- no external dependencies like ffmpeg or ffprobe.

Parses the moov -> mvhd atom to read timescale and duration fields.
"""

import struct
import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def get_mp4_duration(file_path: str) -> Optional[str]:
    """
    Extract duration from an MP4/M4A file and return as HH:MM:SS string.

    Args:
        file_path: Path to the MP4/M4A file.

    Returns:
        Duration string in HH:MM:SS format, or None if parsing fails.
    """
    seconds = get_mp4_duration_seconds(file_path)
    if seconds is None:
        return None
    return _seconds_to_hhmmss(seconds)


def get_mp4_duration_seconds(file_path: str) -> Optional[float]:
    """
    Extract duration from an MP4/M4A file in seconds.

    Args:
        file_path: Path to the MP4/M4A file.

    Returns:
        Duration in seconds as a float, or None if parsing fails.
    """
    if not file_path:
        return None

    # Skip URL paths — we can only read local files
    if '://' in file_path:
        logger.info(f"Cannot extract duration from URL: {file_path}")
        return None

    if not os.path.isfile(file_path):
        logger.warning(f"Media file not found: {file_path}")
        return None

    try:
        with open(file_path, 'rb') as f:
            file_size = f.seek(0, 2)
            f.seek(0)

            if file_size < 8:
                logger.debug(f"File too small to be MP4: {file_path}")
                return None

            # Find moov atom at top level
            result = _find_atom(f, b'moov', file_size)
            if result is None:
                logger.debug(f"No moov atom found in: {file_path}")
                return None

            moov_offset, moov_size = result

            # Find mvhd atom inside moov
            f.seek(moov_offset)
            result = _find_atom(f, b'mvhd', moov_offset + moov_size)
            if result is None:
                logger.warning(f"No mvhd atom found inside moov in: {file_path}")
                return None

            mvhd_offset, mvhd_size = result
            f.seek(mvhd_offset)
            return _parse_mvhd(f, mvhd_size)

    except PermissionError:
        logger.warning(f"Permission denied reading media file: {file_path}")
        return None
    except OSError as e:
        logger.warning(f"OS error reading media file '{file_path}': {e}")
        return None
    except Exception as e:
        logger.warning(f"Unexpected error extracting MP4 duration from '{file_path}': {e}")
        return None


def _find_atom(f, target_type: bytes, search_end: int) -> Optional[Tuple[int, int]]:
    """
    Scan atoms sequentially to find one matching target_type.

    Args:
        f: Open file in binary read mode, positioned at start of atom sequence.
        target_type: 4-byte atom type to search for (e.g. b'moov').
        search_end: File offset beyond which to stop searching.

    Returns:
        (payload_offset, payload_size) if found, else None.
    """
    while f.tell() < search_end:
        atom_start = f.tell()
        header = f.read(8)
        if len(header) < 8:
            return None

        size = struct.unpack('>I', header[:4])[0]
        atom_type = header[4:8]
        header_size = 8

        if size == 1:
            # Extended size
            ext = f.read(8)
            if len(ext) < 8:
                return None
            size = struct.unpack('>Q', ext)[0]
            header_size = 16
        elif size == 0:
            # Atom extends to end of search region
            size = search_end - atom_start

        if size < header_size:
            return None

        payload_offset = atom_start + header_size
        payload_size = size - header_size

        if atom_type == target_type:
            return (payload_offset, payload_size)

        # Skip to next atom
        next_atom = atom_start + size
        if next_atom <= f.tell():
            return None
        f.seek(next_atom)

    return None


def _parse_mvhd(f, payload_size: int) -> Optional[float]:
    """
    Parse mvhd atom payload to extract duration in seconds.

    Handles version 0 (32-bit fields) and version 1 (64-bit fields).

    Args:
        f: File positioned at start of mvhd payload.
        payload_size: Size of the mvhd payload in bytes.

    Returns:
        Duration in seconds, or None on parse error.
    """
    if payload_size < 4:
        return None

    version_flags = f.read(4)
    if len(version_flags) < 4:
        return None

    version = version_flags[0]

    if version == 0:
        # 4+4+4+4 = 16 bytes: creation_time, modification_time, timescale, duration
        data = f.read(16)
        if len(data) < 16:
            return None
        _, _, timescale, duration = struct.unpack('>IIII', data)
    elif version == 1:
        # 8+8+4+8 = 28 bytes
        data = f.read(28)
        if len(data) < 28:
            return None
        _, _, timescale, duration = struct.unpack('>QQIQ', data)
    else:
        logger.warning(f"Unknown mvhd version: {version}")
        return None

    if timescale == 0:
        logger.warning("mvhd timescale is 0, cannot compute duration")
        return None

    return duration / timescale


def _seconds_to_hhmmss(total_seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS format.

    Args:
        total_seconds: Duration in seconds.

    Returns:
        Formatted string like "01:23:45".
    """
    total = int(round(total_seconds))
    hours = total // 3600
    minutes = (total % 3600) // 60
    seconds = total % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

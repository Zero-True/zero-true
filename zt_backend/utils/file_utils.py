import zipfile
import mimetypes
import os
from typing import Dict, Optional, Tuple
from fastapi import HTTPException
from pathlib import Path
import aiofiles


def initialize_mime_types():
    """Initialize and customize MIME types."""
    mimetypes.init()

    custom_mime_types: Dict[str, str] = {
        '.md': 'text/markdown',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.7z': 'application/x-7z-compressed',
        '.rar': 'application/vnd.rar',
        '.webp': 'image/webp',
        # Add more custom MIME types here as needed
    }

    for ext, mime_type in custom_mime_types.items():
        mimetypes.add_type(mime_type, ext)

def get_mime_type(filename: str) -> str:
    """Determine the MIME type of a file based on its filename."""
    initialize_mime_types()
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def validate_path(path: Path, filename: str):
    """Validate the path and raise appropriate exceptions if invalid."""
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Path not found: {filename}")

async def create_zip_file(folder_path: Path, temp_zip_path: str):
    """Create a zip file from a folder."""
    with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=str(folder_path))
                zipf.write(file_path, arcname)

async def parse_range_header(range_header: Optional[str], file_size: int) -> Tuple[int, int]:
    """Parse Range header and return start and end bytes."""
    if not range_header:
        return 0, file_size - 1

    try:
        range_str = range_header.replace('bytes=', '')
        start_str, end_str = range_str.split('-')
        start = int(start_str)
        end = int(end_str) if end_str else file_size - 1
        return start, min(end, file_size - 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid range header")

async def stream_file_range(file_path: str, start: int, end: int, chunk_size: int = 8192):
    """Stream file content for the specified byte range."""
    async with aiofiles.open(file_path, mode='rb') as file:
        await file.seek(start)
        bytes_remaining = end - start + 1

        while bytes_remaining > 0:
            chunk_size = min(chunk_size, bytes_remaining)
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            yield chunk
            bytes_remaining -= len(chunk)

def get_file_type(name):
    extension = name.split(".")[-1]
    if extension in ["html", "js", "json", "md", "pdf", "png", "txt", "xls"]:
        return extension
    return None


def list_dir(path):
    items = []
    for item in path.iterdir():
        if item.is_dir():
            items.append(
                {
                    "title": item.name,
                    "file": "folder",
                    "id": item.as_posix(),
                    "children": [],
                }
            )
        else:
            file_type = get_file_type(item.name)
            if file_type:
                items.append(
                    {"title": item.name, "file": file_type, "id": item.as_posix()}
                )
            else:
                items.append(
                    {"title": item.name, "file": "file", "id": item.as_posix()}
                )
    return items
import zipfile
import mimetypes
import os
from typing import Dict, Optional, Tuple
from fastapi import HTTPException
from pathlib import Path
import aiofiles
import os
from pathlib import Path
from typing import Dict, Set, AsyncGenerator
from fastapi import HTTPException
from dataclasses import dataclass
from collections import deque
import asyncio

@dataclass
class UploadRequest:
    """Track status of each file upload"""
    file_name: str
    chunks_received: int
    total_chunks: int
    is_processing: bool = False

class UploadQueue:
    def __init__(self):
        self.pending_uploads = deque()
        self.active_uploads: Set[str] = set()
        self.upload_semaphore = asyncio.Semaphore(5)
        self.queue_lock = asyncio.Lock()
        self.upload_requests: Dict[str, UploadRequest] = {}
        self.chunk_status: Dict[str, Dict[int, bool]] = {}

    async def add_to_queue(self, file_name: str, total_chunks: int) -> bool:
        async with self.queue_lock:
            if (len(self.pending_uploads) + len(self.active_uploads)) >= 100:
                return False

            if file_name not in self.upload_requests:
                self.upload_requests[file_name] = UploadRequest(
                    file_name=file_name,
                    chunks_received=0,
                    total_chunks=total_chunks
                )
                self.pending_uploads.append(file_name)
            return True

    async def process_chunk(self, file_name: str, chunk_index: int, chunk_data: bytes, base_path: str) -> Dict:
        if file_name not in self.upload_requests:
            raise HTTPException(status_code=400, detail="Upload not registered")

        base_dir = Path(base_path)
        base_dir.mkdir(parents=True, exist_ok=True)

        if not self.upload_requests[file_name].is_processing:
            await self.upload_semaphore.acquire()
            async with self.queue_lock:
                if file_name in self.pending_uploads:
                    self.pending_uploads.remove(file_name)
                self.active_uploads.add(file_name)
                self.upload_requests[file_name].is_processing = True
        
        try:
            temp_dir = base_dir / f"{Path(file_name).parent}" / f"{Path(file_name).name}_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)

            chunk_path = temp_dir / f"{Path(file_name).name}_chunk_{chunk_index}"
            with open(chunk_path, "wb") as f:
                f.write(chunk_data)

            if file_name not in self.chunk_status:
                self.chunk_status[file_name] = {}
            self.chunk_status[file_name][chunk_index] = True
            self.upload_requests[file_name].chunks_received += 1

            if self.upload_requests[file_name].chunks_received == self.upload_requests[file_name].total_chunks:
                return await self.finalize_upload(file_name, base_path)

            return {
                "status": "chunk_received",
                "chunk_index": chunk_index,
                "queued_files": len(self.pending_uploads),
                "active_uploads": len(self.active_uploads),
                "progress": f"{self.upload_requests[file_name].chunks_received}/{self.upload_requests[file_name].total_chunks} chunks"
            }

        except Exception as e:
            await self.cleanup_failed_upload(file_name, temp_dir)
            raise HTTPException(status_code=500, detail=f"Chunk processing failed: {str(e)}")

    async def finalize_upload(self, file_name: str, base_path: str) -> Dict:
        base_dir = Path(base_path)
        temp_dir = base_dir / f"{Path(file_name).parent}" / f"{Path(file_name).name}_temp"
        final_path = base_dir / file_name

        try:
            final_path.parent.mkdir(parents=True, exist_ok=True)
            with open(final_path.with_suffix('.temp'), 'wb') as final_file:
                for i in range(self.upload_requests[file_name].total_chunks):
                    chunk_path = temp_dir / f"{Path(file_name).name}_chunk_{i}"
                    if not chunk_path.exists():
                        raise FileNotFoundError(f"Missing chunk file: {chunk_path}")
                    with open(chunk_path, "rb") as chunk_file:
                        final_file.write(chunk_file.read())

            temp_final_path = final_path.with_suffix('.temp')
            temp_final_path.rename(final_path)

            await self.cleanup_successful_upload(file_name, temp_dir)

            return {
                "status": "complete",
                "filename": file_name,
                "path": str(final_path)
            }

        except Exception as e:
            await self.cleanup_failed_upload(file_name, temp_dir)
            raise HTTPException(status_code=500, detail=f"Failed to finalize upload: {str(e)}")

    async def cleanup_successful_upload(self, file_name: str, temp_dir: Path):
        await self._cleanup_upload(file_name, temp_dir)
        self.upload_semaphore.release()

    async def cleanup_failed_upload(self, file_name: str, temp_dir: Path):
        await self._cleanup_upload(file_name, temp_dir)
        self.upload_semaphore.release()

    async def _cleanup_upload(self, file_name: str, temp_dir: Path):
        async with self.queue_lock:
            if file_name in self.upload_requests:
                del self.upload_requests[file_name]
            if file_name in self.chunk_status:
                del self.chunk_status[file_name]
            if file_name in self.active_uploads:
                self.active_uploads.remove(file_name)

            if temp_dir.exists():
                for chunk in temp_dir.glob("*_chunk_*"):
                    try:
                        os.remove(chunk)
                    except:
                        pass
                try:
                    temp_dir.rmdir()
                except:
                    pass

upload_queue = UploadQueue()


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
    
async def stream_file_range(file_path: str, start: int, end: int, chunk_size: int) -> AsyncGenerator[bytes, None]:
    with open(file_path, 'rb') as file:
        file.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk_size = min(chunk_size, remaining)
            data = file.read(chunk_size)
            if not data:
                break
            remaining -= len(data)
            yield data

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
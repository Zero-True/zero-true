import zipfile
import mimetypes
import os
from typing import Dict, Optional, Tuple
from fastapi import HTTPException
from pathlib import Path
import aiofiles
import os
from pathlib import Path
from typing import Dict, Set
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

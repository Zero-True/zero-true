import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import HTTPException, BackgroundTasks

# Semaphore to control concurrent uploads
upload_semaphore = asyncio.Semaphore(5)
# Locks to ensure each file is written in isolation
upload_locks = {}
# Queue for managing excess requests
upload_queue = asyncio.Queue()
# Global lock for upload_locks dictionary access
locks_dict_lock = asyncio.Lock()

@asynccontextmanager
async def get_file_lock(file_name):
    """Safely get or create a lock for a file"""
    async with locks_dict_lock:
        if file_name not in upload_locks:
            upload_locks[file_name] = asyncio.Lock()
        lock = upload_locks[file_name]
    
    async with lock:
        try:
            yield lock
        finally:
            pass

async def process_upload(background_tasks: BackgroundTasks, file, chunk_index, total_chunks, path, file_name):
    async with upload_semaphore:
        temp_dir = Path(path) / f"{file_name}_temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        chunk_path = temp_dir / f"{file_name}_chunk_{chunk_index}"
        
        # Get file lock safely
        async with get_file_lock(file_name):  # Removed the await here
            try:
                # Write chunk data with exclusive access
                chunk_data = await file.read()
                with open(chunk_path, "wb") as buffer:
                    buffer.write(chunk_data)
                
                # Check if all chunks are present
                expected_chunks = {temp_dir / f"{file_name}_chunk_{i}" 
                                for i in range(total_chunks)}
                existing_chunks = set(temp_dir.glob(f"{file_name}_chunk_*"))
                
                # If this is the last chunk and all chunks are present
                if existing_chunks == expected_chunks:
                    final_path = Path(path) / file_name
                    
                    # Write final file atomically using temporary file
                    temp_final = final_path.with_suffix('.temp')
                    with open(temp_final, "wb") as final_file:
                        for i in range(total_chunks):
                            chunk_file = temp_dir / f"{file_name}_chunk_{i}"
                            with open(chunk_file, "rb") as cf:
                                final_file.write(cf.read())
                    
                    # Atomic rename
                    os.rename(temp_final, final_path)
                    
                    # Clean up chunks
                    for chunk_file in existing_chunks:
                        os.remove(chunk_file)
                    temp_dir.rmdir()
                    
                    background_tasks.add_task(clean_upload_locks, file_name)
                    return {"filename": file_name, "path": str(final_path)}
                    
            except Exception as e:
                # Clean up on error
                if temp_dir.exists():
                    for chunk in temp_dir.glob(f"{file_name}_chunk_*"):
                        try:
                            os.remove(chunk)
                        except:
                            pass
                    try:
                        temp_dir.rmdir()
                    except:
                        pass
                raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

async def clean_upload_locks(file_name):
    async with locks_dict_lock:
        if file_name in upload_locks:
            del upload_locks[file_name]
import os
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from StorageBackends.StorageBackendInterface import StorageBackendInterface

class LocalStorageBackend(StorageBackendInterface):
    def list_files(self, local_path: str):
        return [str(p) for p in Path(local_path).rglob("*") if p.is_file()]

    def upload_file(self, local_path: str, remote_path: str):
        os.makedirs(os.path.dirname(remote_path), exist_ok=True)
        with open(local_path, 'rb') as src, open(remote_path, 'wb') as dst:
            dst.write(src.read())

    def download_file(self, remote_path: str, local_path: str):
        self.upload_file(remote_path, local_path)  # same logic reversed

    def delete_file(self, remote_path: str):
        os.remove(remote_path)

    def get_file_metadata(self, remote_path: str):
        stat = os.stat(remote_path)
        return {
            "name": os.path.basename(remote_path),
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime)
        }

    def get_file_hash(self, file_path: str):
        BLOCK_SIZE = 4 * 1024 * 1024
        sha256 = hashlib.sha256
        chunk_hashes = []

        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(BLOCK_SIZE)
                if not chunk:
                    break
                chunk_hash = sha256(chunk).digest()
                chunk_hashes.append(chunk_hash)

        final_hash = sha256(b''.join(chunk_hashes)).hexdigest()
        return final_hash
    
    
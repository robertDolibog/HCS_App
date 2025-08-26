import dropbox
from dropbox.files import WriteMode
import os
from dotenv import load_dotenv
from StorageBackends.StorageBackendInterface import StorageBackendInterface

load_dotenv()

class DropboxStorageBackend(StorageBackendInterface):
    def __init__(self, access_token: str):
        self.dbx = dropbox.Dropbox(access_token)

    def list_files(self, path=""):
        result = self.dbx.files_list_folder(path)
        # Return full paths instead of just names
        return [entry.path_lower for entry in result.entries if isinstance(entry, dropbox.files.FileMetadata)]

    def upload_file(self, local_path: str, remote_path: str):
        with open(local_path, "rb") as f:
            self.dbx.files_upload(f.read(), remote_path, mode=WriteMode("overwrite"))

    def download_file(self, remote_path: str, local_path: str):
        metadata, res = self.dbx.files_download(remote_path)
        with open(local_path, "wb") as f:
            f.write(res.content)

    def delete_file(self, remote_path: str):
        self.dbx.files_delete_v2(remote_path)

    def get_file_metadata(self, remote_path: str):
        metadata = self.dbx.files_get_metadata(remote_path)
        return {
            "name": metadata.name,
            "size": getattr(metadata, 'size', None),
            "modified": getattr(metadata, 'client_modified', None)
        }

    def get_file_hash(self, remote_path: str):
        metadata = self.dbx.files_get_metadata(remote_path)
        return getattr(metadata, "content_hash", None)

    def close(self):
        pass  
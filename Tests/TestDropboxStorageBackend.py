import os
from StorageBackends.DropboxStorageBackend import DropboxStorageBackend

access_token = os.getenv("DROPBOX_ACCESS_TOKEN")  # or hardcode for testing
backend = DropboxStorageBackend(access_token)

print("📂 Files in root:")
print(backend.list_files("/HCS"))
print("🔐 Content hash:", backend.get_file_hash("test.txt"))

#backend.upload_file("local_file.txt", "/upload_test.txt")
#backend.download_file("/upload_test.txt", "downloaded_copy.txt")
#backend.delete_file("/upload_test.txt")
#

backend.close()

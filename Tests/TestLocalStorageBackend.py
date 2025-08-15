import os
from pathlib import Path
from LocalStorageBackend import LocalStorageBackend  # replace with your actual import

# === Setup ===
backend = LocalStorageBackend()

base_dir = "HCS"
original_file = os.path.join(base_dir, "test.txt")
upload_target = os.path.join(base_dir, "upload_copy.txt")
download_target = os.path.join(base_dir, "download_copy.txt")
delete_target = os.path.join(base_dir, "to_delete.txt")

# === Ensure /HCS/test.txt exists ===
if not os.path.exists(original_file):
    with open(original_file, "w") as f:
        f.write("Hello from HCS!")

print("📂 Listing files:")
print(backend.list_files(base_dir))  # should include /HCS/test.txt

#print("\n⬆️ Uploading to:", upload_target)
#backend.upload_file(original_file, upload_target)
#print("✅ Uploaded:", os.path.exists(upload_target))
#
#print("\n⬇️ Downloading to:", download_target)
#backend.download_file(upload_target, download_target)
#print("✅ Downloaded:", os.path.exists(download_target))
#
#print("\n📄 File contents after download:")
#with open(download_target, "r") as f:
#    print(f.read())
#
print("\n📊 Metadata for /HCS/test.txt:")
meta = backend.get_file_metadata(original_file)
print(meta)
#
print("\n🔐 Hash of /HCS/test.txt:")
print(backend.get_file_hash(original_file))

#print("\n🗑️ Deleting copy at", delete_target)
#backend.upload_file(original_file, delete_target)
#backend.delete_file(delete_target)
#print("✅ Deleted:", not os.path.exists(delete_target))

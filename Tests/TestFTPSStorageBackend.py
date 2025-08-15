import os
from FTPSStorageBackend import FTPSStorageBackend
from dotenv import load_dotenv

load_dotenv()

host = "homeserver.myfritz.link"
port = 47334  # SFTP port from your setup
user = os.getenv("FTP_USER")
password = os.getenv("FTP_PASSWORD")

print("User:", user)
print("Password:", "SET" if password else "MISSING")

backend = FTPSStorageBackend(host, user, password, port)

print("📂 Listing files:")
print(backend.list_files("/"))

print("\n🔐 Hash of /test.txt:")
print(backend.get_file_hash("/test.txt"))
#
#upload_path = "/upload_test.txt"
#local_file = "upload_test.txt"
#with open(local_file, "w") as f:
#    f.write("This is a test for SFTP upload.")
#
#print("\n⬆️ Uploading to:", upload_path)
#backend.upload_file(local_file, upload_path)
#
#download_path = "downloaded_test.txt"
#print("\n⬇️ Downloading to:", download_path)
#backend.download_file(upload_path, download_path)
#
#with open(download_path, "r") as f:
#    print("\n📄 Downloaded content:")
#    print(f.read())
#
#print("\n🗑️ Deleting uploaded file...")
#backend.delete_file(upload_path)
#
backend.close()
#
#os.remove(local_file)
#os.remove(download_path)
#
import os
from StorageBackends.LocalStorageBackend import LocalStorageBackend 
from StorageBackends.FTPSStorageBackend import FTPSStorageBackend
from StorageBackends.DropboxStorageBackend import DropboxStorageBackend
from dotenv import load_dotenv

load_dotenv()

#setup local
backendLocal = LocalStorageBackend()



# setup NAS
host = "homeserver.myfritz.link"
port = 47334  # SFTP port from your setup
user = os.getenv("FTP_USER")
password = os.getenv("FTP_PASSWORD")




backendNAS = FTPSStorageBackend(host, user, password, port)

#setup Dropbox


access_token = os.getenv("DROPBOX_ACCESS_TOKEN")  # or hardcode for testing
backendDropbox = DropboxStorageBackend(access_token)

base_dir = "HCS"
file_extension = "/test.txt"
original_file = base_dir + file_extension

print (backendLocal.list_files(base_dir))
print (backendLocal.get_file_metadata(original_file))
localHash = backendLocal.get_file_hash(original_file)
nasHash = backendNAS.get_file_hash(file_extension)
dropboxHash = backendDropbox.get_file_hash(file_extension)

print("local hash: " , localHash)

print("NAS hash: " , nasHash)

print("Dropbox hash: " , dropboxHash)
if localHash == nasHash == dropboxHash:
    print ("Backup Nr. 2")
#Compare files across backends
for file in backendLocal.list_files(base_dir):
    print("Local file:", file)
    if file in backendNAS.list_files("/"):
        print("NAS file:", file)
    if file in backendDropbox.list_files(""):
        print("Dropbox file:", file)
print (backendDropbox.get_file_metadata(file_extension))
print (backendLocal.get_file_metadata(original_file))
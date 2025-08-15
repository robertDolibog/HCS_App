from ftplib import FTP_TLS
import io
import hashlib
from StorageBackends.StorageBackendInterface import StorageBackendInterface

class FTPSStorageBackend(StorageBackendInterface):
    def __init__(self, host, user, password, port):
        self.ftp = FTP_TLS()
        self.ftp.connect(host, port)
        self.ftp.login(user, password)
        self.ftp.prot_p()  # Switch to secure data connection (TLS protection)

    def list_files(self, path="."):
        return self.ftp.nlst(path)

    def upload_file(self, local_path, remote_path):
        with open(local_path, "rb") as f:
            self.ftp.storbinary(f"STOR " + remote_path, f)

    def download_file(self, remote_path, local_path):
        with open(local_path, "wb") as f:
            self.ftp.retrbinary(f"RETR " + remote_path, f.write)

    def delete_file(self, remote_path):
        self.ftp.delete(remote_path)

    def get_file_metadata(self, remote_path):
        # Not directly supported unless MLSD is available
        return {
            'name': remote_path.split('/')[-1],
            'size': self.ftp.size(remote_path),
            'modified': self.ftp.sendcmd(f"MDTM {remote_path}")[4:].strip()
        }

    
    def get_file_hash(self, remote_path):
        BLOCK_SIZE = 4 * 1024 * 1024
        sha256 = hashlib.sha256
        chunk_hashes = []

        buf = io.BytesIO()
        self.ftp.retrbinary(f"RETR {remote_path}", buf.write)
        buf.seek(0)

        while True:
            chunk = buf.read(BLOCK_SIZE)
            if not chunk:
                break
            chunk_hash = sha256(chunk).digest()
            chunk_hashes.append(chunk_hash)

        final_hash = sha256(b''.join(chunk_hashes)).hexdigest()
        return final_hash

    def close(self):
        self.ftp.quit()

import os, uuid, hashlib
from datetime import datetime

from StorageBackends.LocalStorageBackend import LocalStorageBackend
from StorageBackends.DropboxStorageBackend import DropboxStorageBackend
from StorageBackends.FTPSStorageBackend import FTPSStorageBackend

from Services.comparison_service import ComparisonService
from Services.classification_service import ClassificationService
from repositories.file_repository import FileRepository
from repositories.file_location_repository import FileLocationRepository
import os

class SyncService:
    def __init__(self, base_folder='HCS'):
        # initialize all storage backends
        self.backends = [
            LocalStorageBackend(),
            DropboxStorageBackend(os.getenv('DROPBOX_ACCESS_TOKEN','')),
            FTPSStorageBackend(
                os.getenv('FTPS_HOST',''),
                os.getenv('FTPS_USER',''),
                os.getenv('FTPS_PASSWORD',''),
                int(os.getenv('FTPS_PORT','21'))
            )
        ]
        
        self.base_folder = base_folder
        self.comparison = ComparisonService()
        self.classifier = ClassificationService()
        self.file_repo = FileRepository
        self.location_repo = FileLocationRepository

    def _collect_entries(self):
        entries = []
        for backend in self.backends:
            name = type(backend).__name__
            try:
                if name == 'DropboxStorageBackend':
                    paths = backend.list_files("/" + self.base_folder)
                else:
                    paths = backend.list_files(self.base_folder)
            except:
                paths = []
            for path in paths:
                meta = backend.get_file_metadata(path) or {}
                size = meta.get('size', 0)
                modified = meta.get('modified') or datetime.now()
                try:
                    file_hash = backend.get_file_hash(path)
                except:
                    file_hash = hashlib.sha256(path.encode()).hexdigest()
                entries.append({
                    'file_hash': file_hash,
                    'path': path,
                    'name': os.path.basename(path),
                    'size': size,
                    'last_modified': modified,
                    'backend': name
                })
        return entries

    def run(self):
        entries = self._collect_entries()
        groups = self.comparison.group_by_hash(entries)
        backups = self.comparison.compute_backup_counts(groups)

        # wipe & reinsert
        self.file_repo.delete_all()
        self.location_repo.delete_all()

        for file_hash, items in groups.items():
            # stable UUID from hash
            file_id = str(uuid.uuid5(uuid.NAMESPACE_OID, file_hash))
            rep = items[0]
            sens = self.classifier.classify(rep['path'])
            file = self.file_repo.get_or_create(
                file_id,
                name=rep['name'],
                path=rep['path'],
                size=rep['size'],
                last_modified=rep['last_modified'],
                sensitivity=sens,
                backup_count=backups[file_hash],
                updated_at=datetime.now()
            )
            for it in items:
                self.location_repo.add(file_id, it['backend'])

        self.file_repo.commit()
        return len(entries)

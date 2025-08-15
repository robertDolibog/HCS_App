from abc import ABC, abstractmethod


class StorageBackendInterface(ABC):
    @abstractmethod
    def list_files(self, path: str):
        pass

    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str):
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: str):
        pass

    @abstractmethod
    def delete_file(self, remote_path: str):
        pass

    @abstractmethod
    def get_file_metadata(self, remote_path: str):
        pass

    @abstractmethod
    def get_file_hash(self, file_path: str):
        pass

    
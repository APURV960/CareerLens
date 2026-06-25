from abc import ABC, abstractmethod
import os

class StorageProvider(ABC):
    """
    Abstract Base Class defining the file operations interface.
    All business logic must go through this layer rather than direct file system requests.
    """
    @abstractmethod
    def save(self, file_bytes: bytes, key: str) -> str:
        """Saves file bytes and returns a string storage locator key."""
        pass

    @abstractmethod
    def get(self, key: str) -> bytes:
        """Retrieves file bytes corresponding to the storage key."""
        pass

class LocalStorageProvider(StorageProvider):
    """
    Local file storage driver. Saves files on the local filesystem relative to a base directory.
    """
    def __init__(self, base_dir: str = "storage"):
        self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)

    def save(self, file_bytes: bytes, key: str) -> str:
        full_path = os.path.join(self.base_dir, key)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "wb") as f:
            f.write(file_bytes)
        return key  # Return relative locator key

    def get(self, key: str) -> bytes:
        full_path = os.path.join(self.base_dir, key)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File not found in storage: {key}")
        with open(full_path, "rb") as f:
            return f.read()

class S3StorageProvider(StorageProvider):
    """
    AWS S3 Cloud Storage driver. Kept ready for deployment configurations.
    """
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        # self.s3 = boto3.client('s3') # Intended for production swap

    def save(self, file_bytes: bytes, key: str) -> str:
        # self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=file_bytes)
        # return key
        raise NotImplementedError("Cloud AWS S3 Provider is pre-configured but not active in MVP.")

    def get(self, key: str) -> bytes:
        # response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        # return response['Body'].read()
        raise NotImplementedError("Cloud AWS S3 Provider is pre-configured but not active in MVP.")

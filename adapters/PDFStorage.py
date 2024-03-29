import io
from abc import ABC, abstractmethod

import boto3

from config import EnvConfig


class PDFStorageInterface(ABC):
    @abstractmethod
    def download_pdf(self, user_id: str, name: str) -> io.BytesIO:
        pass

    @abstractmethod
    def upload_pdf(self, user_id: str, name: str, pdf: io.BytesIO) -> str:
        pass


class PDFStorageMock(PDFStorageInterface):
    def download_pdf(self, user_id: str, name: str) -> io.BytesIO:
        return io.BytesIO(b"mock")

    def upload_pdf(self, user_id: str, name: str, pdf: io.BytesIO) -> str:
        return "reference to storage"


class PDFStorage(PDFStorageInterface):
    def __init__(self, config: EnvConfig):
        self._aws_access_key_id = config.AWS_ACCESS_KEY
        self._aws_secret_access_key = config.AWS_SECRET_KEY
        self._region = "eu-central-1"
        self._bucket_name = "spacey-pdf-storage"

        self._bucket = boto3.resource(
            "s3",
            aws_access_key_id=self._aws_access_key_id,
            aws_secret_access_key=self._aws_secret_access_key,
            region_name=self._region,
        ).Bucket(self._bucket_name)

    def download_pdf(self, user_id: str, name: str) -> io.BytesIO:
        pdf = io.BytesIO()
        self._bucket.download_fileobj(f"{user_id}/{name}", pdf)
        pdf.seek(0)

        return pdf

    def upload_pdf(self, user_id: str, name: str, pdf: io.BytesIO) -> str:
        self._bucket.upload_fileobj(pdf, f"{user_id}/{name}")
        return f"https://{self._bucket_name}.s3.{self._region}.amazonaws.com/{user_id}/{name}"

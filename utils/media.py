from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

from .singleton import Singleton


class MediaStorage(S3Boto3Storage, metaclass=Singleton):
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME

import os
import logging

from typing import Optional, BinaryIO, Dict, Any
import aioboto3
from botocore.config import Config

from utils.error import AWSError


class S3Client:
    """
    인스턴스 기반 S3 클라이언트
    - lifespan에서 initialize()로 초기화
    - app.state에 보관 → Depends()로 주입
    """

    def __init__(self):
        self._session = None
        self._config = None

    async def initialize(self):
        if self._session is not None:
            return
        self._config = Config(
            region_name=os.getenv('AWS_REGION', 'ap-northeast-2'),
            retries={
                'max_attempts': 3,
                'mode': 'standard'
            },
            connect_timeout=5,
            read_timeout=5
        )
        self._session = aioboto3.Session(
            region_name=os.getenv('AWS_REGION', 'ap-northeast-2')
        )
        logging.info("✅ on s3 Client")

    async def get_client(self):
        if self._session is None:
            await self.initialize()
        return self._session.client('s3', config=self._config)

    async def close(self):
        if self._session:
            self._session = None
            self._config = None
        logging.info("🔴 off s3 Client")

    async def upload_file(
        self,
        file_data: BinaryIO | str,
        bucket: str,
        key: str,
        content_type: Optional[str] = None,
        extra_args: Optional[Dict[str, Any]] = None
    ):
        try:
            args = extra_args or {}
            if content_type:
                args['ContentType'] = content_type

            async with await self.get_client() as s3:
                response = await s3.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=file_data,
                    **args
                )
                return {
                    "bucket": bucket,
                    "key": key,
                    "etag": response.get("ETag", "").strip('"'),
                    "version_id": response.get("VersionId")
                }
        except Exception as e:
            logging.error(f"[S3Client.upload_file] 🔴 Failed to upload file to S3: {e}")
            raise AWSError(e)

    async def download_file(self, bucket: str, key: str) -> bytes:
        try:
            async with await self.get_client() as s3:
                response = await s3.get_object(Bucket=bucket, Key=key)
                async with response['Body'] as stream:
                    data = await stream.read()
                return data
        except Exception as e:
            logging.error(f"[S3Client.download_file] 🔴 Failed to download file from S3: {e}")
            raise AWSError(e)

    async def delete_file(self, bucket: str, key: str):
        try:
            async with await self.get_client() as s3:
                await s3.delete_object(
                    Bucket=bucket,
                    Key=key
                )
                return {"message": "파일이 성공적으로 삭제되었습니다."}
        except Exception as e:
            logging.error(f"[S3Client.delete_file] 🔴 Failed to delete file from S3: {e}")
            raise AWSError(e)

    async def get_presigned_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        operation: str = 'get_object'
    ):
        try:
            async with await self.get_client() as s3:
                url = await s3.generate_presigned_url(
                    ClientMethod=operation,
                    Params={
                        'Bucket': bucket,
                        'Key': key
                    },
                    ExpiresIn=expiration
                )
                return {"url": url, "expires_in": expiration}
        except Exception as e:
            logging.error(f"[S3Client.get_presigned_url] 🔴 Failed to generate presigned URL: {e}")
            raise AWSError(e)

    async def list_files(self, bucket: str, prefix: str = "", max_keys: int = 1000):
        try:
            result = []
            async with await self.get_client() as s3:
                paginator = s3.get_paginator('list_objects_v2')
                async for page in paginator.paginate(Bucket=bucket, Prefix=prefix, MaxKeys=max_keys):
                    if 'Contents' in page:
                        for obj in page['Contents']:
                            result.append({
                                "key": obj['Key'],
                                "size": obj['Size'],
                                "last_modified": obj['LastModified'].isoformat(),
                                "etag": obj['ETag'].strip('"')
                            })
            return result
        except Exception as e:
            logging.error(f"[S3Client.list_files] 🔴 Failed to list files from S3: {e}")
            raise AWSError(e)

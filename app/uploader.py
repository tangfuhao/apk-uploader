"""OSS uploader module for APK files."""

import oss2
from pathlib import Path
from typing import Optional
import tempfile
import os


class OSSUploader:
    """APK uploader to Aliyun OSS."""
    
    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str,
        bucket_name: str,
        region: str,
        prefix: str = "apk"
    ):
        """
        Initialize OSS uploader.
        
        Args:
            access_key_id: Aliyun OSS access key ID
            access_key_secret: Aliyun OSS access key secret
            endpoint: OSS endpoint URL
            bucket_name: OSS bucket name
            region: OSS region
            prefix: Upload path prefix
        """
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.endpoint = endpoint
        self.bucket_name = bucket_name
        self.region = region
        self.prefix = prefix
        self._bucket = None
    
    @property
    def bucket(self):
        """Get or create OSS bucket connection."""
        if self._bucket is None:
            auth = oss2.Auth(self.access_key_id, self.access_key_secret)
            self._bucket = oss2.Bucket(
                auth, 
                self.endpoint, 
                self.bucket_name, 
                region=self.region
            )
        return self._bucket
    
    async def upload_file(
        self, 
        file_content: bytes, 
        filename: str,
        custom_name: Optional[str] = None
    ) -> dict:
        """
        Upload file to OSS.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            custom_name: Optional custom name for the uploaded file
            
        Returns:
            dict: Upload result containing URL and metadata
            
        Raises:
            ValueError: If the file is not an APK
            Exception: If upload fails
        """
        # Validate file extension
        if not filename.lower().endswith('.apk'):
            raise ValueError(f"File must be an APK file, got: {filename}")
        
        # Determine object name
        if custom_name:
            # Ensure custom name doesn't have .apk extension
            custom_name = custom_name.replace('.apk', '')
            object_name = f"{self.prefix}/{custom_name}.apk"
        else:
            object_name = f"{self.prefix}/{filename}"
        
        # Calculate file size
        file_size = len(file_content)
        file_size_mb = file_size / (1024 * 1024)
        
        try:
            # Upload the file
            result = self.bucket.put_object(
                object_name, 
                file_content,
                headers={'Content-Type': 'application/vnd.android.package-archive'}
            )
            
            if result.status != 200:
                raise Exception(f"Upload failed with status: {result.status}")
            
            # Construct the public URL
            oss_url = f"https://download.macaron.chat/{object_name}"
            
            # Construct console URL
            # console_url = (
            #     f"https://oss.console.aliyun.com/bucket/"
            #     f"{self.region}/{self.bucket_name}/object?path={self.prefix}%2F"
            # )
            
            return {
                "success": True,
                "url": oss_url,
                "object_name": object_name,
                "bucket": self.bucket_name,
                "size_mb": round(file_size_mb, 2)
                # "console_url": console_url
            }
            
        except Exception as e:
            raise Exception(f"Failed to upload APK: {str(e)}")


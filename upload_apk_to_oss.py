#!/usr/bin/env python3
"""
Upload APK files to Aliyun OSS.

Usage:
    python upload_apk_to_oss.py <apk_file_path> --access-key-id <id> --access-key-secret <secret>

Example:
    python upload_apk_to_oss.py myapp.apk --access-key-id LTAI5xxx --access-key-secret G9xhxxx
    python upload_apk_to_oss.py myapp.apk -k LTAI5xxx -s G9xhxxx
    python upload_apk_to_oss.py myapp.apk -k LTAI5xxx -s G9xhxxx --name myapp_v1.0
"""

import os
import sys
import oss2
import argparse
from pathlib import Path
from datetime import datetime


class ApkUploader:
    """APK uploader to Aliyun OSS."""
    
    def __init__(
        self,
        access_key_id: str,
        access_key_secret: str,
        endpoint: str = "https://oss-ap-southeast-1.aliyuncs.com",
        bucket_name: str = "macaron-system",
        region: str = "ap-southeast-1",
        prefix: str = "apk"
    ):
        """
        Initialize APK uploader.
        
        Args:
            access_key_id: Aliyun OSS access key ID
            access_key_secret: Aliyun OSS access key secret
            endpoint: OSS endpoint URL
            bucket_name: OSS bucket name
            region: OSS region
            prefix: Upload path prefix (default: apk)
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
            self._bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name, region=self.region)
        return self._bucket
    
    def upload_apk(self, file_path: str, custom_name: str = None) -> str:
        """
        Upload APK file to OSS.
        
        Args:
            file_path: Path to the local APK file
            custom_name: Optional custom name for the uploaded file (without extension)
            
        Returns:
            str: OSS URL of the uploaded file
            
        Raises:
            FileNotFoundError: If the APK file doesn't exist
            ValueError: If the file is not an APK
            Exception: If upload fails
        """
        # Validate file
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() != '.apk':
            raise ValueError(f"File must be an APK file, got: {file_path.suffix}")
        
        # Get file info
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        # Determine object name
        if custom_name:
            object_name = f"{self.prefix}/{custom_name}.apk"
        else:
            # Use original filename
            object_name = f"{self.prefix}/{file_path.name}"
        
        print(f"📦 Uploading APK file...")
        print(f"   File: {file_path.name}")
        print(f"   Size: {file_size_mb:.2f} MB")
        print(f"   Target: {object_name}")
        print(f"   Bucket: {self.bucket_name}")
        print()
        
        # Upload with progress
        try:
            with open(file_path, 'rb') as f:
                # Upload the file
                result = self.bucket.put_object(object_name, f, 
                    headers={'Content-Type': 'application/vnd.android.package-archive'})
            
            if result.status != 200:
                raise Exception(f"Upload failed with status: {result.status}")
            
            # Construct the public URL
            oss_url = f"https://{self.bucket_name}.{self.endpoint.replace('https://', '')}/{object_name}"
            
            print("✅ Upload successful!")
            print(f"   URL: {oss_url}")
            print()
            print(f"📋 OSS Console URL:")
            print(f"   https://oss.console.aliyun.com/bucket/{self.region}/{self.bucket_name}/object?path={self.prefix}%2F")
            
            return oss_url
            
        except Exception as e:
            raise Exception(f"Failed to upload APK: {str(e)}")


def main():
    """Main function to handle command-line upload."""
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description='Upload APK files to Aliyun OSS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage with credentials
  %(prog)s myapp.apk -k LTAI5xxx -s G9xhxxx
  
  # With custom name
  %(prog)s myapp.apk -k LTAI5xxx -s G9xhxxx --name myapp_v1.0
  
  # Using environment variables (fallback)
  export OSS_ACCESS_KEY_ID='LTAI5xxx'
  export OSS_ACCESS_KEY_SECRET='G9xhxxx'
  %(prog)s myapp.apk
        """
    )
    
    # Positional arguments
    parser.add_argument(
        'apk_file',
        help='Path to the APK file to upload'
    )
    
    # Optional arguments
    parser.add_argument(
        '-k', '--access-key-id',
        dest='access_key_id',
        help='Aliyun OSS Access Key ID (required if not set in environment)'
    )
    
    parser.add_argument(
        '-s', '--access-key-secret',
        dest='access_key_secret',
        help='Aliyun OSS Access Key Secret (required if not set in environment)'
    )
    
    parser.add_argument(
        '-n', '--name',
        dest='custom_name',
        help='Custom name for the uploaded file (without .apk extension)'
    )
    
    parser.add_argument(
        '-b', '--bucket',
        dest='bucket_name',
        default='macaron-system',
        help='OSS bucket name (default: macaron-system)'
    )
    
    parser.add_argument(
        '-p', '--prefix',
        dest='prefix',
        default='apk',
        help='Upload path prefix (default: apk)'
    )
    
    parser.add_argument(
        '-e', '--endpoint',
        dest='endpoint',
        default='https://oss-ap-southeast-1.aliyuncs.com',
        help='OSS endpoint URL (default: https://oss-ap-southeast-1.aliyuncs.com)'
    )
    
    parser.add_argument(
        '-r', '--region',
        dest='region',
        default='ap-southeast-1',
        help='OSS region (default: ap-southeast-1)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get credentials: command-line args take precedence over environment variables
    access_key_id = args.access_key_id or os.environ.get("OSS_ACCESS_KEY_ID")
    access_key_secret = args.access_key_secret or os.environ.get("OSS_ACCESS_KEY_SECRET")
    
    # Validate credentials
    if not access_key_id or not access_key_secret:
        print("❌ Error: OSS credentials not provided")
        print()
        print("Please provide credentials using one of these methods:")
        print()
        print("1. Command-line arguments (recommended):")
        print(f"   python {sys.argv[0]} myapp.apk -k YOUR_KEY_ID -s YOUR_KEY_SECRET")
        print()
        print("2. Environment variables:")
        print("   export OSS_ACCESS_KEY_ID='YOUR_KEY_ID'")
        print("   export OSS_ACCESS_KEY_SECRET='YOUR_KEY_SECRET'")
        print()
        sys.exit(1)
    
    try:
        # Create uploader
        uploader = ApkUploader(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=args.endpoint,
            bucket_name=args.bucket_name,
            region=args.region,
            prefix=args.prefix
        )
        
        # Upload the APK
        oss_url = uploader.upload_apk(args.apk_file, args.custom_name)
        
        print("✨ Done!")
        sys.exit(0)
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


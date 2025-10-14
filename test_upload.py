#!/usr/bin/env python3
"""
測試腳本：用於測試 APK 上傳 API

用法:
    python test_upload.py <apk_file_path> [--api-url http://localhost:8000] [--name custom_name]

示例:
    # 測試本地 API
    python test_upload.py myapp.apk
    
    # 使用自定義名稱
    python test_upload.py myapp.apk --name myapp_v1.0
    
    # 測試遠程 API
    python test_upload.py myapp.apk --api-url https://your-app.railway.app
"""

import requests
import argparse
import sys
from pathlib import Path


def test_upload(apk_path: str, api_url: str = "http://localhost:8000", custom_name: str = None):
    """測試上傳 APK 文件到 API"""
    
    # 檢查文件是否存在
    apk_file = Path(apk_path)
    if not apk_file.exists():
        print(f"❌ 錯誤：文件不存在 - {apk_path}")
        return False
    
    if not apk_file.suffix.lower() == '.apk':
        print(f"❌ 錯誤：文件必須是 APK 格式 - {apk_path}")
        return False
    
    # 準備上傳
    upload_url = f"{api_url.rstrip('/')}/upload"
    file_size_mb = apk_file.stat().st_size / (1024 * 1024)
    
    print(f"📦 準備上傳 APK 文件...")
    print(f"   文件: {apk_file.name}")
    print(f"   大小: {file_size_mb:.2f} MB")
    print(f"   API: {upload_url}")
    print()
    
    try:
        # 打開文件並上傳
        with open(apk_file, 'rb') as f:
            files = {'file': (apk_file.name, f, 'application/vnd.android.package-archive')}
            data = {}
            
            if custom_name:
                data['custom_name'] = custom_name
                print(f"   自定義名稱: {custom_name}")
                print()
            
            print("⏳ 上傳中...")
            response = requests.post(upload_url, files=files, data=data)
        
        # 處理響應
        if response.status_code == 200:
            result = response.json()
            print("✅ 上傳成功！")
            print()
            print("📋 結果:")
            print(f"   URL: {result['data']['url']}")
            print(f"   對象名: {result['data']['object_name']}")
            print(f"   存儲桶: {result['data']['bucket']}")
            print(f"   大小: {result['data']['size_mb']} MB")
            print()
            print(f"🌐 OSS 控制台:")
            print(f"   {result['data']['console_url']}")
            return True
        else:
            print(f"❌ 上傳失敗 (HTTP {response.status_code})")
            try:
                error_data = response.json()
                print(f"   錯誤: {error_data.get('detail', '未知錯誤')}")
            except:
                print(f"   響應: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ 連接錯誤：無法連接到 API ({upload_url})")
        print("   請確保 API 服務正在運行")
        return False
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_health(api_url: str = "http://localhost:8000"):
    """測試 API 健康狀態"""
    try:
        health_url = f"{api_url.rstrip('/')}/health"
        response = requests.get(health_url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 健康檢查通過")
            print(f"   狀態: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"⚠️  API 健康檢查返回異常狀態碼: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ 無法連接到 API: {api_url}")
        return False
    except Exception as e:
        print(f"❌ 健康檢查失敗: {str(e)}")
        return False


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='測試 APK 上傳 API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 測試本地 API
  %(prog)s myapp.apk
  
  # 使用自定義名稱
  %(prog)s myapp.apk --name myapp_v1.0
  
  # 測試遠程 API
  %(prog)s myapp.apk --api-url https://your-app.railway.app
  
  # 僅健康檢查
  %(prog)s --health-check
        """
    )
    
    parser.add_argument(
        'apk_file',
        nargs='?',
        help='APK 文件路徑'
    )
    
    parser.add_argument(
        '--api-url',
        default='http://localhost:8000',
        help='API 基礎 URL (默認: http://localhost:8000)'
    )
    
    parser.add_argument(
        '--name',
        dest='custom_name',
        help='自定義文件名（不含 .apk 後綴）'
    )
    
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='僅執行健康檢查'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("APK 上傳 API 測試工具")
    print("=" * 60)
    print()
    
    # 如果指定健康檢查
    if args.health_check:
        success = test_health(args.api_url)
        sys.exit(0 if success else 1)
    
    # 檢查是否提供了文件
    if not args.apk_file:
        print("❌ 錯誤：請提供 APK 文件路徑")
        print()
        parser.print_help()
        sys.exit(1)
    
    # 先進行健康檢查
    print("🏥 執行 API 健康檢查...")
    if not test_health(args.api_url):
        print()
        print("⚠️  API 可能未運行或無法訪問")
        print("   繼續嘗試上傳...")
        print()
    else:
        print()
    
    # 執行上傳測試
    success = test_upload(args.apk_file, args.api_url, args.custom_name)
    
    print()
    print("=" * 60)
    if success:
        print("✨ 測試完成！")
        sys.exit(0)
    else:
        print("❌ 測試失敗")
        sys.exit(1)


if __name__ == "__main__":
    main()


# APK Uploader API

一個基於 FastAPI 的 APK 文件上傳服務，將 APK 文件上傳到阿里雲 OSS 對象存儲。

## 功能特點

- 🚀 FastAPI 構建的高性能 API
- ☁️ 自動上傳到阿里雲 OSS
- 🔒 從環境變量讀取憑證，安全可靠
- 📦 支持自定義文件名
- ✅ 文件大小和類型驗證
- 📝 完整的 API 文檔（Swagger UI）
- 🌐 CORS 支持
- 🏥 健康檢查端點

## 快速開始

### 本地開發

1. **克隆項目並安裝依賴**

```bash
# 安裝 Python 依賴
pip install -r requirements.txt
```

2. **配置環境變量**

複製 `.env.example` 為 `.env` 並填入您的憑證：

```bash
cp .env.example .env
```

編輯 `.env` 文件：

```env
OSS_ACCESS_KEY_ID=your_access_key_id
OSS_ACCESS_KEY_SECRET=your_access_key_secret
OSS_BUCKET_NAME=your_bucket_name
```

3. **運行應用**

```bash
# 開發模式（自動重載）
python -m app.main

# 或使用 uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. **訪問 API**

- API 文檔：http://localhost:8000/docs
- ReDoc 文檔：http://localhost:8000/redoc
- 健康檢查：http://localhost:8000/health

## API 使用

### 上傳 APK 文件

**端點：** `POST /upload`

**參數：**
- `file`: APK 文件（必需）
- `custom_name`: 自定義文件名（可選，不需要 .apk 後綴）

**使用 curl：**

```bash
# 基本上傳
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/app.apk"

# 使用自定義名稱
curl -X POST "http://localhost:8000/upload" \
  -F "file=@/path/to/your/app.apk" \
  -F "custom_name=myapp_v1.0"
```

**使用 Python：**

```python
import requests

url = "http://localhost:8000/upload"
files = {"file": open("myapp.apk", "rb")}
data = {"custom_name": "myapp_v1.0"}  # 可選

response = requests.post(url, files=files, data=data)
print(response.json())
```

**響應示例：**

```json
{
  "success": true,
  "message": "APK uploaded successfully",
  "data": {
    "success": true,
    "url": "https://your-bucket.oss-ap-southeast-1.aliyuncs.com/apk/myapp_v1.0.apk",
    "object_name": "apk/myapp_v1.0.apk",
    "bucket": "your-bucket",
    "size_mb": 25.5,
    "console_url": "https://oss.console.aliyun.com/bucket/..."
  }
}
```

## 部署到 Railway

### 方法 1：使用 Railway CLI

1. **安裝 Railway CLI**

```bash
npm install -g @railway/cli
```

2. **登錄並初始化**

```bash
railway login
railway init
```

3. **設置環境變量**

```bash
railway variables set OSS_ACCESS_KEY_ID=your_access_key_id
railway variables set OSS_ACCESS_KEY_SECRET=your_access_key_secret
railway variables set OSS_BUCKET_NAME=your_bucket_name
railway variables set OSS_ENDPOINT=https://oss-ap-southeast-1.aliyuncs.com
railway variables set OSS_REGION=ap-southeast-1
```

4. **部署**

```bash
railway up
```

### 方法 2：使用 GitHub 集成

1. 將代碼推送到 GitHub
2. 在 Railway 儀表板中連接您的 GitHub 倉庫
3. 在 Railway 項目設置中添加環境變量
4. Railway 會自動部署

### 必需的環境變量

在 Railway 中設置以下環境變量：

| 變量名 | 描述 | 必需 |
|--------|------|------|
| `OSS_ACCESS_KEY_ID` | 阿里雲 OSS Access Key ID | ✅ |
| `OSS_ACCESS_KEY_SECRET` | 阿里雲 OSS Access Key Secret | ✅ |
| `OSS_BUCKET_NAME` | OSS 存儲桶名稱 | ✅ |
| `OSS_ENDPOINT` | OSS 端點 URL | ⚪ |
| `OSS_REGION` | OSS 區域 | ⚪ |
| `OSS_PREFIX` | 上傳路徑前綴 | ⚪ |
| `MAX_UPLOAD_SIZE` | 最大上傳大小（字節） | ⚪ |

## 項目結構

```
apk-uploader/
├── app/
│   ├── __init__.py          # 應用初始化
│   ├── main.py              # FastAPI 主應用
│   ├── config.py            # 配置管理
│   └── uploader.py          # OSS 上傳邏輯
├── upload_apk_to_oss.py     # 原始腳本（參考）
├── requirements.txt         # Python 依賴
├── .env.example             # 環境變量示例
├── .gitignore              # Git 忽略文件
├── railway.toml            # Railway 配置
├── Procfile                # 進程文件
└── README.md               # 項目文檔
```

## 配置說明

### OSS 配置

默認配置適用於東南亞（新加坡）區域：

- **端點：** `https://oss-ap-southeast-1.aliyuncs.com`
- **區域：** `ap-southeast-1`
- **存儲桶：** `macaron-system`
- **前綴：** `apk`

您可以通過環境變量修改這些配置。

### 上傳限制

- **默認最大文件大小：** 200MB
- **允許的文件類型：** 僅 .apk 文件

可以通過 `MAX_UPLOAD_SIZE` 環境變量調整大小限制。

## 開發

### 運行測試

```bash
# TODO: 添加測試
pytest
```

### 代碼格式化

```bash
# 使用 black
black app/

# 使用 ruff
ruff check app/
```

## 故障排除

### 憑證錯誤

如果遇到憑證相關錯誤，請確保：
1. 環境變量已正確設置
2. Access Key 有正確的 OSS 權限
3. 存儲桶名稱正確

### 上傳失敗

如果上傳失敗，檢查：
1. 文件大小是否超過限制
2. 文件是否為有效的 APK 文件
3. OSS 存儲桶是否存在且可訪問
4. 網絡連接是否正常

### Railway 部署問題

如果在 Railway 上部署遇到問題：
1. 檢查所有必需的環境變量是否已設置
2. 查看 Railway 構建日誌
3. 確保 `requirements.txt` 包含所有依賴

## 安全建議

1. **永遠不要提交 `.env` 文件到版本控制**
2. **使用 Railway Secrets 或環境變量存儲敏感信息**
3. **定期輪換 Access Key**
4. **配置適當的 CORS 策略**
5. **在生產環境中使用 HTTPS**
6. **考慮添加 API 認證（如 JWT）**

## 許可證

MIT License

## 支持

如有問題或建議，請提出 Issue。


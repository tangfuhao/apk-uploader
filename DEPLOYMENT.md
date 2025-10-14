# Railway 部署指南

本文檔提供詳細的 Railway 部署步驟和故障排除指南。

## 🚀 快速部署

### 方式 1: 使用 Railway CLI（推薦）

1. **安裝 Railway CLI**

```bash
npm install -g @railway/cli
# 或使用 brew (macOS)
brew install railway
```

2. **登錄 Railway**

```bash
railway login
```

3. **初始化項目**

```bash
cd /path/to/apk-uploader
railway init
```

選擇：
- 創建新項目或選擇現有項目
- 項目名稱：`apk-uploader`（或您喜歡的名稱）

4. **設置環境變量**

```bash
# 必需的環境變量
railway variables set OSS_ACCESS_KEY_ID=your_key_id_here
railway variables set OSS_ACCESS_KEY_SECRET=your_key_secret_here
railway variables set OSS_BUCKET_NAME=your_bucket_name

# 可選的環境變量（如果需要修改默認值）
railway variables set OSS_ENDPOINT=https://oss-ap-southeast-1.aliyuncs.com
railway variables set OSS_REGION=ap-southeast-1
railway variables set OSS_PREFIX=apk
railway variables set MAX_UPLOAD_SIZE=209715200
```

5. **部署**

```bash
railway up
```

6. **生成公共域名**

```bash
railway domain
```

或在 Railway Dashboard 中手動添加域名。

### 方式 2: 使用 GitHub 集成

1. **推送代碼到 GitHub**

```bash
git init
git add .
git commit -m "Initial commit: APK uploader API"
git branch -M main
git remote add origin https://github.com/yourusername/apk-uploader.git
git push -u origin main
```

2. **在 Railway 上創建項目**

- 訪問 [railway.app](https://railway.app)
- 點擊 "New Project"
- 選擇 "Deploy from GitHub repo"
- 授權並選擇您的倉庫

3. **配置環境變量**

在 Railway Dashboard 中：
- 進入項目設置
- 點擊 "Variables" 標籤
- 添加所有必需的環境變量（見下方清單）

4. **部署**

Railway 會自動檢測並部署您的應用。

## 📋 環境變量清單

### 必需變量

| 變量名 | 描述 | 示例 |
|--------|------|------|
| `OSS_ACCESS_KEY_ID` | 阿里雲 Access Key ID | `LTAI5tXXXXXXXXXXXXXX` |
| `OSS_ACCESS_KEY_SECRET` | 阿里雲 Access Key Secret | `G9xhXXXXXXXXXXXXXXXX` |
| `OSS_BUCKET_NAME` | OSS 存儲桶名稱 | `macaron-system` |

### 可選變量

| 變量名 | 描述 | 默認值 |
|--------|------|--------|
| `OSS_ENDPOINT` | OSS 端點 URL | `https://oss-ap-southeast-1.aliyuncs.com` |
| `OSS_REGION` | OSS 區域 | `ap-southeast-1` |
| `OSS_PREFIX` | 上傳路徑前綴 | `apk` |
| `MAX_UPLOAD_SIZE` | 最大上傳大小（字節） | `209715200` (200MB) |
| `DEBUG` | 調試模式 | `false` |

## ✅ 部署檢查清單

完成以下檢查以確保部署成功：

- [ ] Railway CLI 已安裝並登錄
- [ ] 項目已在 Railway 上初始化
- [ ] 所有必需的環境變量已設置
- [ ] OSS 存儲桶已創建並可訪問
- [ ] Access Key 具有正確的 OSS 權限
- [ ] 代碼已推送到 GitHub（如果使用 GitHub 集成）
- [ ] 部署成功且服務正在運行
- [ ] 公共域名已配置
- [ ] API 健康檢查通過
- [ ] 測試上傳成功

## 🔍 驗證部署

### 1. 檢查服務狀態

在 Railway Dashboard 中檢查：
- 部署狀態：應該顯示為 "Active"
- 日誌：查看是否有錯誤信息

### 2. 測試健康檢查端點

```bash
curl https://your-app.railway.app/health
```

應該返回：
```json
{
  "status": "healthy",
  "service": "apk-uploader"
}
```

### 3. 測試根端點

```bash
curl https://your-app.railway.app/
```

應該返回 API 信息。

### 4. 查看 API 文檔

訪問：`https://your-app.railway.app/docs`

您應該能看到 Swagger UI 文檔。

### 5. 測試上傳功能

使用測試腳本：

```bash
python test_upload.py myapp.apk --api-url https://your-app.railway.app
```

## 🐛 故障排除

### 問題 1：部署失敗

**症狀：** 部署過程中出現錯誤

**解決方案：**
1. 檢查 Railway 部署日誌
2. 確保 `requirements.txt` 正確
3. 檢查 Python 版本（`runtime.txt`）
4. 確保 `railway.toml` 配置正確

### 問題 2：服務啟動失敗

**症狀：** 部署成功但服務無法啟動

**解決方案：**
1. 檢查環境變量是否都已設置
2. 查看 Railway 日誌中的錯誤信息
3. 確保 `OSS_ACCESS_KEY_ID` 和 `OSS_ACCESS_KEY_SECRET` 已設置

### 問題 3：上傳失敗

**症狀：** API 運行但上傳失敗

**解決方案：**
1. 檢查 OSS 憑證是否正確
2. 確認存儲桶名稱正確
3. 驗證 Access Key 是否有 PutObject 權限
4. 檢查網絡連接
5. 查看應用日誌

### 問題 4：504 Gateway Timeout

**症狀：** 上傳大文件時超時

**解決方案：**
1. 增加 `MAX_UPLOAD_SIZE` 限制（如果適用）
2. Railway 有默認的請求超時限制
3. 考慮使用分塊上傳（需要修改代碼）

### 問題 5：環境變量未生效

**症狀：** 設置了環境變量但應用似乎沒有讀取

**解決方案：**
1. 重新部署應用以應用新的環境變量
2. 使用 Railway CLI 驗證變量：
   ```bash
   railway variables
   ```
3. 檢查變量名稱是否正確（區分大小寫）

## 📊 監控和日誌

### 查看日誌

**使用 Railway CLI：**

```bash
railway logs
```

**使用 Railway Dashboard：**
- 進入項目
- 點擊 "Deployments" 標籤
- 選擇最新部署
- 查看日誌

### 監控指標

在 Railway Dashboard 中，您可以監控：
- CPU 使用率
- 內存使用率
- 網絡流量
- 請求數量

## 🔒 安全最佳實踐

1. **永遠不要在代碼中硬編碼憑證**
   - 始終使用環境變量

2. **限制 Access Key 權限**
   - 僅授予必要的 OSS 權限
   - 使用 RAM 用戶而非主帳號

3. **定期輪換密鑰**
   - 定期更新 Access Key
   - 在 Railway 中更新環境變量

4. **配置 CORS**
   - 在生產環境中限制 CORS 來源
   - 修改 `app/main.py` 中的 CORS 設置

5. **啟用 HTTPS**
   - Railway 默認提供 HTTPS
   - 確保使用 HTTPS URL

6. **添加認證**
   - 考慮添加 API 密鑰或 JWT 認證
   - 保護上傳端點

## 🔄 更新部署

### 使用 Railway CLI

```bash
git add .
git commit -m "Update: ..."
railway up
```

### 使用 GitHub

```bash
git add .
git commit -m "Update: ..."
git push
```

Railway 會自動檢測並重新部署。

## 📞 獲取幫助

- **Railway 文檔：** https://docs.railway.app
- **Railway Discord：** https://discord.gg/railway
- **阿里雲 OSS 文檔：** https://help.aliyun.com/product/31815.html

## 💡 提示和技巧

1. **使用環境分組**
   - 為開發、測試和生產環境創建不同的 Railway 項目

2. **設置通知**
   - 在 Railway 中配置部署通知

3. **使用私有網絡**
   - 如果有其他服務，考慮使用 Railway 的私有網絡功能

4. **備份環境變量**
   - 導出並安全存儲您的環境變量配置

5. **監控成本**
   - 注意 Railway 的使用限制
   - OSS 的流量和存儲成本


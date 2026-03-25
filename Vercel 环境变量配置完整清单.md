# 🔐 Vercel 环境变量配置完整清单

## 📋 必需配置的环境变量

### 1. Flask 核心配置 ⭐⭐⭐

| 变量名 | 用途 | 建议值 | 必需 |
|--------|------|--------|------|
| `FLASK_ENV` | Flask 运行环境 | `production` | ✅ 必需 |
| `SECRET_KEY` | Flask 会话加密密钥 | `goin_immersive_mvp_2026_secure_random_key_2026` | ✅ 必需 |

**配置说明**：
- `FLASK_ENV=production` - 告诉应用这是生产环境
- `SECRET_KEY` - 用于加密 session 和 cookie，必须足够复杂

**如何生成 SECRET_KEY**：
```python
# Python 生成随机密钥
import secrets
print(secrets.token_hex(32))
# 输出示例：a8f3k29dj3k4l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

---

### 2. 高德地图 API ⭐⭐⭐

| 变量名 | 用途 | 默认值 | 必需 |
|--------|------|--------|------|
| `GAODE_KEY` | 高德地图 Web 服务 API | `2274b3d46339f95092d68b83150ead7f` | ✅ 必需 |
| `GAODE_API_SECRET` | 高德地图安全密钥 | `` (空) | ⚠️ 可选 |

**获取方式**：
1. 访问 https://lbs.amap.com/
2. 注册/登录账号
3. 进入控制台 → 应用管理 → 我的应用
4. 创建新应用，添加 Key
5. 选择"Web 服务"类型

**配置说明**：
- 用于地点搜索、地理编码等功能
- 代码中已有默认值，但建议配置自己的 Key

---

### 3. 火山引擎（豆包 AI）⭐⭐⭐

| 变量名 | 用途 | 默认值 | 必需 |
|--------|------|--------|------|
| `VOLCENGINE_API_KEY` | 火山引擎 API Key | `de012cdc-ddcb-4695-a362-a67e26d5dcda` | ✅ 必需 |
| `VOLCENGINE_API_SECRET` | 火山引擎 API Secret | `` (空) | ⚠️ 可选 |
| `DOUBAO_API_KEY` | 豆包大模型 API Key | `de012cdc-ddcb-4695-a362-a67e26d5dcda` | ✅ 必需 |

**获取方式**：
1. 访问 https://www.volcengine.com/
2. 注册/登录账号
3. 进入控制台 → 访问控制 → API Key 管理
4. 创建 Access Key

**配置说明**：
- 用于 AI 文案生成、内容合成等功能
- 代码中已有默认值，但建议配置自己的 Key

---

### 4. 阿里云百炼（通义千问/万相）⭐⭐⭐

| 变量名 | 用途 | 默认值 | 必需 |
|--------|------|--------|------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | `sk-2274b3d46339f95092d68b83150ead7f` | ✅ 必需 |
| `WANXIANG_API_KEY` | 通义万相（AI 绘画） | `sk-2274b3d46339f95092d68b83150ead7f` | ⚠️ 可选 |
| `QWEN_API_KEY` | 通义千问（文案生成） | `sk-2274b3d46339f95092d68b83150ead7f` | ⚠️ 可选 |
| `QWEN_VL_API_KEY` | 通义千问 VL（多模态） | `sk-2274b3d46339f95092d68b83150ead7f` | ⚠️ 可选 |

**获取方式**：
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录账号
3. 开通服务（通义千问、通义万相）
4. 进入控制台 → API Key 管理

**配置说明**：
- 用于 AI 内容生成、图像处理等功能
- 代码中已有默认值，但建议配置自己的 Key

---

### 5. 云数据库配置（可选）⭐

| 变量名 | 用途 | 示例值 | 必需 |
|--------|------|--------|------|
| `DATABASE_URL` | 云数据库连接字符串 | `postgresql://user:pass@host:5432/db` | ⚠️ 可选 |

**使用场景**：
- 如果使用内存数据库（演示）：**不需要配置**
- 如果使用云数据库（生产持久化）：**必须配置**

**推荐云数据库**：

#### A. Supabase（PostgreSQL）
```
DATABASE_URL=postgresql://postgres:password@xxx.supabase.co:5432/postgres
```
- 免费额度：500MB
- 网址：https://supabase.com

#### B. PlanetScale（MySQL）
```
DATABASE_URL=mysql://user:pass@xxx.planetscale.com/dbname
```
- 免费额度：5GB
- 网址：https://planetscale.com

#### C. 火山引擎 RDS
```
DATABASE_URL=mysql://user:pass@xxx.rds.volces.com:3306/dbname
```
- 付费服务
- 网址：https://www.volcengine.com

---

### 6. 调试配置（可选）

| 变量名 | 用途 | 建议值 | 必需 |
|--------|------|--------|------|
| `DEBUG` | 调试模式 | `False` | ⚠️ 可选 |

**配置说明**：
- 生产环境必须设置为 `False`
- 开发环境可设置为 `True`

---

## 🎯 最小化配置（快速开始）

如果只想快速部署并测试，**最少只需配置 3 个环境变量**：

```bash
# 1. Flask 核心配置
FLASK_ENV=production
SECRET_KEY=goin_immersive_mvp_2026_secure_random_key_2026

# 2. 高德地图 API（使用默认值或自己的）
GAODE_KEY=2274b3d46339f95092d68b83150ead7f
```

**说明**：
- 火山引擎和阿里云的 API 在代码中已有默认值
- 可以先使用默认值进行测试
- 正式使用前建议替换为自己的 API Key

---

## 🚀 生产环境推荐配置（完整）

### 环境变量清单

```bash
# Flask 核心
FLASK_ENV=production
SECRET_KEY=goin_immersive_mvp_2026_$(python -c "import secrets; print(secrets.token_hex(16))")

# 高德地图
GAODE_KEY=your_actual_amap_key_here
GAODE_API_SECRET=your_amap_secret_here

# 火山引擎
VOLCENGINE_API_KEY=your_actual_volcengine_key_here
VOLCENGINE_API_SECRET=your_volcengine_secret_here
DOUBAO_API_KEY=your_actual_doubao_key_here

# 阿里云百炼
DASHSCOPE_API_KEY=your_actual_dashscope_key_here
WANXIANG_API_KEY=your_actual_wanxiang_key_here
QWEN_API_KEY=your_actual_qwen_key_here
QWEN_VL_API_KEY=your_actual_qwen_vl_key_here

# 云数据库（如果需要持久化）
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 调试
DEBUG=False
```

---

## 📝 Vercel 配置步骤

### 方法 A：通过 Vercel 控制台（推荐）

#### 第 1 步：打开 Vercel 控制台

访问：https://vercel.com/dashboard

#### 第 2 步：进入项目设置

1. 找到 "goin" 项目
2. 点击 "Settings"
3. 点击 "Environment Variables"

#### 第 3 步：添加环境变量

点击 "Add New"，逐个添加以下变量：

**必需变量**：
```
Name: FLASK_ENV
Value: production
Environment: Production ✅

Name: SECRET_KEY
Value: goin_immersive_mvp_2026_secure_random_key_2026
Environment: Production ✅

Name: GAODE_KEY
Value: 2274b3d46339f95092d68b83150ead7f
Environment: Production ✅
```

**可选变量**：
```
Name: VOLCENGINE_API_KEY
Value: de012cdc-ddcb-4695-a362-a67e26d5dcda
Environment: Production ✅

Name: DASHSCOPE_API_KEY
Value: sk-2274b3d46339f95092d68b83150ead7f
Environment: Production ✅
```

#### 第 4 步：保存并重新部署

1. 点击 "Save" 保存所有变量
2. 点击 "Redeploy" 重新部署
3. 等待 2-5 分钟部署完成

---

### 方法 B：使用 Vercel CLI

#### 安装 Vercel CLI

```bash
npm install -g vercel
```

#### 登录 Vercel

```bash
vercel login
```

#### 配置环境变量

```bash
# 进入项目目录
cd "c:\Users\hn\Desktop\桌面的东西\GOIN2"

# 添加环境变量
vercel env add FLASK_ENV production
vercel env add SECRET_KEY production
vercel env add GAODE_KEY production
vercel env add VOLCENGINE_API_KEY production
vercel env add DASHSCOPE_API_KEY production
```

#### 重新部署

```bash
vercel --prod
```

---

### 方法 C：批量导入（最快）

#### 第 1 步：创建 .env 文件

在项目根目录创建 `.env` 文件：

```bash
# .env
FLASK_ENV=production
SECRET_KEY=goin_immersive_mvp_2026_secure_random_key_2026
GAODE_KEY=2274b3d46339f95092d68b83150ead7f
VOLCENGINE_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda
DASHSCOPE_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
```

#### 第 2 步：使用 Vercel CLI 导入

```bash
vercel env pull .env
```

**注意**：
- ⚠️ `.env` 文件包含敏感信息，**不要提交到 Git**
- ✅ `.gitignore` 已包含 `.env`，会自动忽略

---

## ✅ 验证配置

### 检查环境变量是否生效

访问 Vercel 控制台 → Deployments → 最新部署 → Logs

查看日志输出：
```
🔧 生产环境：使用 SQLite = /tmp/goin.db
🔧 开始初始化数据库...
✅ 数据库表创建成功
✅ 数据库初始化成功
```

### 测试 API 调用

访问部署的 URL：
```
https://goin-git-master-drearylll.vercel.app
```

如果一切正常，应该能正常访问和使用。

---

## 🔒 安全建议

### ✅ 最佳实践

1. **使用强密钥**
   ```bash
   # 生成随机密钥
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **不要将 API Key 提交到 Git**
   ```bash
   # .gitignore 必须包含：
   .env
   .env.local
   ```

3. **限制 API Key 权限**
   - 高德地图：设置 IP 白名单
   - 火山引擎：设置 Referer 白名单
   - 阿里云：设置 Referer 白名单

4. **定期更换 API Key**
   - 建议每 3-6 个月更换一次
   - 发现泄露立即更换

5. **不同环境使用不同的 Key**
   - 开发环境：使用测试 Key
   - 生产环境：使用正式 Key

### ❌ 避免的错误

1. **将 API Key 硬编码在代码中**
   - 虽然代码中有默认值，但建议通过环境变量配置

2. **在公开场合分享 API Key**
   - 不要上传到 GitHub、Gist 等公开平台
   - 不要在论坛、博客中暴露

3. **多个项目共用一个 Key**
   - 每个项目使用独立的 Key
   - 便于管理和监控

---

## 📊 API Key 使用监控

### 高德地图

访问：https://lbs.amap.com/console/show/usage

查看：
- 每日调用量
- 月度使用趋势
- 配额使用情况

### 火山引擎

访问：https://console.volcengine.com/ark

查看：
- API 调用次数
- Token 使用量
- 费用统计

### 阿里云百炼

访问：https://dashscope.console.aliyun.com/usage

查看：
- Token 使用量
- 调用次数
- 费用明细

---

## 🆘 故障排查

### 问题 1：环境变量未生效

**现象**：
```
使用默认 API Key...
```

**解决方案**：
1. 检查环境变量名称是否正确
2. 确认已添加到 "Production" 环境
3. 重新部署：Deployments → Redeploy
4. 清除缓存：勾选 "Clear Cache and Redeploy"

### 问题 2：API Key 无效

**现象**：
```
Error: Invalid API Key
```

**解决方案**：
1. 检查 API Key 是否正确
2. 确认 API Key 已激活
3. 查看 API 控制台是否有余额
4. 检查 IP 白名单设置

### 问题 3：数据库连接失败

**现象**：
```
Error: Cannot connect to database
```

**解决方案**：
1. 检查 `DATABASE_URL` 格式
2. 确认云数据库已创建并运行
3. 检查数据库白名单
4. 使用内存数据库测试

---

## 📋 快速复制清单

### 最小化配置（复制粘贴）

```bash
FLASK_ENV=production
SECRET_KEY=goin_immersive_mvp_2026_secure_random_key_2026
GAODE_KEY=2274b3d46339f95092d68b83150ead7f
```

### 完整配置（复制粘贴）

```bash
# Flask 核心
FLASK_ENV=production
SECRET_KEY=goin_immersive_mvp_2026_secure_random_key_2026

# 高德地图
GAODE_KEY=2274b3d46339f95092d68b83150ead7f
GAODE_API_SECRET=

# 火山引擎
VOLCENGINE_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda
VOLCENGINE_API_SECRET=
DOUBAO_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda

# 阿里云百炼
DASHSCOPE_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
WANXIANG_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
QWEN_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
QWEN_VL_API_KEY=sk-2274b3d46339f95092d68b83150ead7f

# 云数据库（可选）
DATABASE_URL=

# 调试
DEBUG=False
```

---

## 🎯 总结

### 必需配置（最少 3 个）

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
GAODE_KEY=your-amap-key-here
```

### 推荐配置（完整 10 个）

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
GAODE_KEY=your-amap-key-here
GAODE_API_SECRET=your-amap-secret
VOLCENGINE_API_KEY=your-volcengine-key
VOLCENGINE_API_SECRET=your-volcengine-secret
DOUBAO_API_KEY=your-doubao-key
DASHSCOPE_API_KEY=your-dashscope-key
WANXIANG_API_KEY=your-wanxiang-key
QWEN_API_KEY=your-qwen-key
```

### 可选配置

```bash
DATABASE_URL=your-cloud-database-url
DEBUG=False
```

---

**文档创建时间**: 2026-03-25 14:45  
**适用版本**: Vercel Serverless 部署  
**状态**: ✅ 可直接使用  
**最后更新**: 2026-03-25 14:45

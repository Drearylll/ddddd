# 🔐 Vercel 环境变量配置清单

## 必需配置的环境变量

### 1. Flask 核心配置

| 变量名 | 用途 | 示例值 | 必需 |
|--------|------|--------|------|
| `FLASK_ENV` | Flask 运行环境 | `production` | ✅ 必需 |
| `SECRET_KEY` | Flask 会话加密密钥 | `your-secret-key-here` | ✅ 必需 |
| `DEBUG` | 调试模式 | `False` | ⚠️ 建议 |

**设置方法**：
```bash
# Vercel 控制台 → Settings → Environment Variables
FLASK_ENV=production
SECRET_KEY=goin_immersive_mvp_2026_production_key
DEBUG=False
```

---

### 2. 火山引擎 API（豆包 AI）

| 变量名 | 用途 | 获取方式 | 必需 |
|--------|------|----------|------|
| `VOLCENGINE_API_KEY` | 火山引擎 API Key | 火山引擎控制台 | ✅ 必需 |
| `VOLCENGINE_API_SECRET` | 火山引擎 API Secret | 火山引擎控制台 | ⚠️ 可选 |
| `DOUBAO_API_KEY` | 豆包大模型 API Key | 火山引擎控制台 | ✅ 必需 |

**获取方式**：
1. 访问 https://www.volcengine.com/
2. 登录并创建 Access Key
3. 进入控制台 → 访问控制 → API Key 管理

**设置示例**：
```bash
VOLCENGINE_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda
VOLCENGINE_API_SECRET=your-secret-here
DOUBAO_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda
```

---

### 3. 阿里云百炼 API（通义千问/万相）

| 变量名 | 用途 | 获取方式 | 必需 |
|--------|------|----------|------|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | 阿里云控制台 | ✅ 必需 |
| `WANXIANG_API_KEY` | 通义万相（AI 绘画） | 阿里云控制台 | ⚠️ 可选 |
| `QWEN_API_KEY` | 通义千问（文案生成） | 阿里云控制台 | ⚠️ 可选 |
| `QWEN_VL_API_KEY` | 通义千问 VL（多模态） | 阿里云控制台 | ⚠️ 可选 |

**获取方式**：
1. 访问 https://dashscope.console.aliyun.com/
2. 开通服务并创建 API Key
3. 进入控制台 → API Key 管理

**设置示例**：
```bash
DASHSCOPE_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
WANXIANG_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
QWEN_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
```

---

### 4. 高德地图 API（地点搜索）

| 变量名 | 用途 | 获取方式 | 必需 |
|--------|------|----------|------|
| `AMAP_KEY` | 高德地图 API Key | 高德开放平台 | ✅ 必需 |
| `AMAP_SECRET` | 高德地图 Secret | 高德开放平台 | ⚠️ 可选 |

**获取方式**：
1. 访问 https://lbs.amap.com/
2. 注册并创建应用
3. 进入控制台 → Key 管理

**设置示例**：
```bash
AMAP_KEY=your-amap-key-here
AMAP_SECRET=your-amap-secret-here
```

---

### 5. 云数据库配置（可选）

| 变量名 | 用途 | 示例值 | 必需 |
|--------|------|--------|------|
| `DATABASE_URL` | 云数据库连接字符串 | `postgresql://user:pass@host:5432/db` | ⚠️ 可选 |

**使用场景**：
- 如果使用内存数据库（演示）：**不需要配置**
- 如果使用云数据库（生产）：**必须配置**

**云数据库推荐**：

#### A. Supabase（PostgreSQL）
```bash
DATABASE_URL=postgresql://postgres:password@xxx.supabase.co:5432/postgres
```

#### B. PlanetScale（MySQL）
```bash
DATABASE_URL=mysql://user:pass@xxx.planetscale.com/dbname
```

#### C. 火山引擎 RDS
```bash
DATABASE_URL=mysql://user:pass@xxx.rds.volces.com:3306/dbname
```

---

## 环境变量优先级说明

### 代码中已内置默认值

**火山引擎**：
```python
VOLCENGINE_API_KEY = os.getenv("VOLCENGINE_API_KEY", "de012cdc-ddcb-4695-a362-a67e26d5dcda")
```

**阿里云百炼**：
```python
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-2274b3d46339f95092d68b83150ead7f")
```

**说明**：
- 如果环境变量存在 → 使用环境变量
- 如果环境变量不存在 → 使用硬编码默认值

**建议**：
- 生产环境：**必须配置环境变量**
- 演示用途：可以使用默认值

---

## Vercel 配置步骤

### 第 1 步：打开 Vercel 控制台

访问：https://vercel.com/dashboard

### 第 2 步：进入项目设置

1. 找到 "goin" 项目
2. 点击 "Settings"
3. 点击 "Environment Variables"

### 第 3 步：添加环境变量

点击 "Add New"：

**必填变量**：
```
Name: FLASK_ENV
Value: production
Environment: Production ✅

Name: SECRET_KEY
Value: goin_immersive_mvp_2026_production_key
Environment: Production ✅

Name: VOLCENGINE_API_KEY
Value: de012cdc-ddcb-4695-a362-a67e26d5dcda
Environment: Production ✅

Name: DASHSCOPE_API_KEY
Value: sk-2274b3d46339f95092d68b83150ead7f
Environment: Production ✅

Name: AMAP_KEY
Value: your-amap-key-here
Environment: Production ✅
```

### 第 4 步：重新部署

配置完成后，点击 "Redeploy" 使环境变量生效。

---

## 环境变量验证

### 本地测试

创建 `.env` 文件：
```bash
FLASK_ENV=development
SECRET_KEY=local_test_key
VOLCENGINE_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda
DASHSCOPE_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
AMAP_KEY=your-amap-key-here
```

运行应用：
```bash
python app.py
```

### Vercel 验证

查看日志：
```bash
# Vercel 控制台 → Deployments → 最新部署 → Logs
# 应该看到：
🔧 Vercel 环境：使用数据库模式 = :memory:
```

---

## 安全建议

### ✅ 最佳实践

1. **生产环境必须配置环境变量**
   - 不要依赖硬编码的默认值
   - 定期更换 API Key

2. **使用强密钥**
   ```bash
   # 生成随机密钥
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

3. **限制 API Key 权限**
   - 火山引擎：设置 IP 白名单
   - 阿里云：设置 Referer 白名单

4. **监控 API 使用量**
   - 火山引擎控制台 → 用量统计
   - 阿里云控制台 → 用量查询

### ❌ 避免的错误

1. **将 API Key 提交到 Git**
   ```bash
   # .gitignore 必须包含：
   .env
   .env.local
   ```

2. **使用弱密钥**
   ```bash
   # 不好的例子：
   SECRET_KEY=123456
   SECRET_KEY=admin
   
   # 好的例子：
   SECRET_KEY=goin_immersive_mvp_2026_a8f3k29dj3k4l2m3n4o5p6
   ```

3. **共享 API Key**
   - 每个项目使用独立的 Key
   - 不同环境（开发/生产）使用不同的 Key

---

## 故障排查

### 问题 1：API Key 无效

**错误信息**：
```
Error: Invalid API Key
```

**解决方案**：
1. 检查环境变量名称是否正确
2. 确认 API Key 是否已激活
3. 查看 API 控制台是否有余额
4. 检查 IP 白名单设置

### 问题 2：环境变量未生效

**错误信息**：
```
Using default API key...
```

**解决方案**：
1. Vercel 控制台 → Settings → Environment Variables
2. 确认变量已添加到 "Production" 环境
3. 点击 "Redeploy" 重新部署

### 问题 3：数据库连接失败

**错误信息**：
```
Error: Cannot connect to database
```

**解决方案**：
1. 检查 `DATABASE_URL` 格式是否正确
2. 确认云数据库已创建并运行
3. 检查数据库白名单设置
4. 使用内存数据库测试：`DATABASE_PATH=:memory:`

---

## 环境变量清单总结

### 必需配置（最少配置）

```bash
# Flask 核心
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# AI 服务（至少配置一个）
VOLCENGINE_API_KEY=your-volcengine-key
DASHSCOPE_API_KEY=your-dashscope-key

# 地图服务
AMAP_KEY=your-amap-key
```

### 可选配置

```bash
# 云数据库（如果需要持久化）
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# 调试
DEBUG=False
```

---

**文档创建时间**: 2026-03-20 14:00  
**适用版本**: Vercel Serverless 部署  
**状态**: ✅ 可直接使用

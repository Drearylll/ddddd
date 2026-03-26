# API 配置说明

## ✅ 当前可用配置

### 火山引擎豆包 API
- **API Key**: `de012cdc-ddcb-4695-a362-a67e26d5dcda`
- **状态**: ✅ 已测试通过，有免费额度
- **模型**: `doubao-seed-2-0-pro-260215`
- **Base URL**: `https://ark.cn-beijing.volces.com/api/v3/responses`

### 阿里云百炼 API
- **API Key**: `sk-2274b3d46339f95092d68b83150ead7f` (示例)
- **状态**: ⚠️ 需要替换为正确的 Key
- **Base URL**: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- **模型**: `qwen-plus`

---

## 🔧 如何获取阿里云 API Key

### 步骤 1: 登录阿里云控制台

访问：https://dashscope.console.aliyun.com

### 步骤 2: 开通百炼服务

1. 进入"百炼"控制台
2. 点击"开通服务"
3. 完成实名认证（必需）

### 步骤 3: 创建 API Key

1. 进入"API-KEY 管理"
2. 点击"创建新的 API-KEY"
3. 复制生成的 Key（格式：`sk-xxxxxxxxxxxxxxxx`）

### 步骤 4: 领取免费额度

1. 进入"费用中心"
2. 找到"免费试用"
3. 领取通义千问免费额度（新用户通常有）

### 步骤 5: 更新配置文件

编辑 `.env.local` 文件：
```bash
QWEN_API_KEY=sk-你的正确 API_Key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

---

## 📊 API 对比

| 服务商 | 免费额度 | 价格 | 智能度 | 推荐指数 |
|--------|----------|------|--------|----------|
| **火山引擎豆包** | ✅ 有 | ¥0.008/千 tokens | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **阿里云通义** | ✅ 有 | ¥0.008/千 tokens | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 💡 建议

### 方案 A: 继续使用火山引擎豆包（推荐）

**理由**:
- ✅ API Key 已验证有效
- ✅ 已测试通过
- ✅ 有免费额度
- ✅ 智能度高

**操作**:
```bash
# 直接使用当前版本即可
python app.py
```

### 方案 B: 切换到阿里云通义

**前提**: 需要先获取正确的 API Key

**步骤**:
1. 前往阿里云百炼控制台
2. 创建 API Key
3. 领取免费额度
4. 更新 `.env.local` 配置
5. 测试：`python test_qwen_api.py`

---

## 🚀 当前可用功能

无论使用哪个 API，以下功能都已就绪：

1. ✅ **Go 聊天功能** - AI 朋友对话
2. ✅ **意图识别** - 自动识别用户意图
3. ✅ **数据库保存** - 记录用户对话和意图
4. ✅ **Mock fallback** - API 不可用时自动降级

---

**更新时间**: 2026-03-20  
**更新者**: AI 协作者

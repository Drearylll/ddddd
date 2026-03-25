# 🔧 Vercel 环境变量配置指南

## 问题诊断

网站显示 **500 INTERNAL_SERVER_ERROR**，原因是 **Vercel 缺少必要的环境变量配置**。

## 解决方案

### 方法一：在 Vercel 后台配置环境变量（推荐）

#### 步骤：

1. **打开 Vercel 控制台**
   - 访问：https://vercel.com
   - 登录你的账号

2. **进入项目设置**
   - 找到你的项目 `goin`
   - 点击 "Settings" 标签

3. **添加环境变量**
   - 点击左侧菜单 "Environment Variables"
   - 点击 "Add Environment Variable" 按钮

4. **添加以下环境变量**：

   | 变量名 | 值 | 环境 |
   |--------|-----|------|
   | `DASHSCOPE_API_KEY` | `sk-2274b3d46339f95092d68b83150ead7f` | Production, Preview, Development |
   | `GAODE_KEY` | `2274b3d46339f95092d68b83150ead7f` | Production, Preview, Development |
   | `VOLCENGINE_API_KEY` | `de012cdc-ddcb-4695-a362-a67e26d5dcda` | Production, Preview, Development（可选） |

5. **重新部署**
   - 添加完环境变量后，点击 "Deploy" 重新部署
   - 或者推送新的代码触发自动部署

---

### 方法二：使用 Vercel CLI（高级）

如果你安装了 Vercel CLI：

```bash
# 安装 Vercel CLI
npm install -g vercel

# 登录 Vercel
vercel login

# 进入项目目录
cd "c:\Users\hn\Desktop\桌面的东西\GOIN2"

# 添加环境变量
vercel env add DASHSCOPE_API_KEY sk-2274b3d46339f95092d68b83150ead7f
vercel env add GAODE_KEY 2274b3d46339f95092d68b83150ead7f
vercel env add VOLCENGINE_API_KEY de012cdc-ddcb-4695-a362-a67e26d5dcda

# 重新部署
vercel --prod
```

---

## 本地开发（可选）

如果你想在本地测试环境变量：

1. **复制示例文件**
   ```bash
   cp .env.example .env
   ```

2. **编辑 .env 文件**
   ```
   DASHSCOPE_API_KEY=sk-2274b3d46339f95092d68b83150ead7f
   GAODE_KEY=2274b3d46339f95092d68b83150ead7f
   VOLCENGINE_API_KEY=de012cdc-ddcb-4695-a362-a67e26d5dcda
   ```

3. **运行本地服务器**
   ```bash
   python app.py
   ```

4. **访问** http://localhost:5000

---

## 验证部署

配置完成后：

1. **等待 Vercel 部署完成**（约 1-2 分钟）
2. **访问网站**：https://你的项目域名.vercel.app
3. **检查是否正常加载**

---

## API 密钥说明

### 阿里云百炼 API Key
- **用途**：AI 文案生成、AI 绘画
- **获取方式**：https://dashscope.console.aliyun.com/

### 高德地图 API Key
- **用途**：地理位置服务、周边搜索
- **获取方式**：https://lbs.amap.com/

### 火山引擎 API Key（可选）
- **用途**：备用 AI 服务
- **获取方式**：https://console.volcengine.com/

---

## 常见问题

### Q1: 环境变量配置后还是 500 错误？
A: 请检查：
- 环境变量名称是否正确（区分大小写）
- 环境变量值是否正确（没有多余空格）
- 是否选择了正确的环境（Production/Preview/Development）
- 重新部署是否成功

### Q2: 如何查看 Vercel 部署日志？
A: 
1. 进入 Vercel 项目
2. 点击 "Deployments" 标签
3. 点击最新的部署
4. 查看 "Build Logs" 和 "Function Logs"

### Q3: 本地运行正常，Vercel 部署失败？
A: 这是环境变量问题。本地使用硬编码的 API Key，Vercel 需要使用环境变量。

---

## 下一步

配置完环境变量后，网站应该可以正常访问了。

如果还有问题，请查看 Vercel 部署日志，或者联系我获取帮助。

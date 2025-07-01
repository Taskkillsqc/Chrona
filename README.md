# Chrona

Chrona 是一个基于 LLM 的智能日程提醒助手。

## 🆕 v3.0 新功能亮点

- 🤖 **LLM 多提供商支持**: 支持 Gemini、DeepSeek、OpenAI、自定义 API 端点和本地模型
- 🏠 **本地模型支持**: 支持 GGUF 格式的本地 LLM 模型（Qwen、LLaMA、Gemma 等）⚠️ 实验性功能
- 🔧 **灵活的模型配置**: 用户可自定义 API URL、模型名称和请求参数
- ⚡ **统一的 LLM 接口**: 通过统一接口调用不同的 LLM 提供商
- 🎛️ **高级参数控制**: 支持温度、最大令牌数、top-p 等参数调整
- 🔗 **自定义 API 支持**: 兼容任何 OpenAI 格式的 API 端点
- � **创建事件API**: 通过REST API远程创建日程事件，支持指定提供商和日历
- �🔄 **向后兼容**: 完全兼容 v2.x 配置文件

## 🆕 v2.0 功能特性

- 💗 **心跳包监控**: 支持向 Uptime Kuma、Healthchecks.io 等监控服务发送状态更新
- 🌐 **完整REST API**: 提供丰富的HTTP接口，支持远程监控和控制
- 🌍 **CORS跨域支持**: 支持前端Web应用跨域访问，可配置允许的源和方法
- 📊 **实时状态监控**: 通过API实时查看程序运行状态、统计信息和心跳包状态
- 🔧 **远程操作**: 支持通过API远程触发事件获取、提醒检查等操作
- 📚 **自动API文档**: 内置Swagger UI和ReDoc文档，开箱即用
- 🧪 **测试工具**: 提供完整的功能测试脚本，确保部署正确

## ✨ 功能特性

- 🔄 **自动同步**: 每 10 分钟通过 CalDAV 获取接下来 1 小时的日程
- 🗂️ **多 CalDAV 支持**: 同时支持多个日历提供商（iCloud、Google、Outlook 等）
- 🤖 **AI 分析**: 使用在线 API 或本地模型智能分析日程重要性和提醒需求
- 🏠 **本地 LLM 支持**: 支持 GGUF 格式模型，完全离线运行，保护隐私（⚠️ 实验性功能，格式错误率较高）
- 💾 **数据存储**: 本地 SQLite 数据库存储分析结果
- 📱 **智能通知**: 通过 Webhook 发送个性化提醒通知，支持 Gotify、Slack、通用和完全自定义格式
- 🐳 **容器化部署**: 支持 Docker 和 docker-compose 部署
- 🔧 **灵活配置**: 支持多种 AI 模型和 CalDAV 服务
- 🗂️ **多日历支持**: 自动识别和显示事件来源日历名称（如 iCloud 小日历）
- 💗 **心跳包监控**: 定期向 Uptime Kuma 等监控服务发送状态更新
- 🌐 **REST API**: 完整的 API 接口支持远程监控和控制
- 🌍 **CORS 跨域**: 支持前端Web应用访问，灵活的跨域配置
- 📊 **实时状态**: 自动生成 API 文档，支持实时查看程序状态

## 🚀 快速开始

### 🔧 环境要求

- Python 3.7+
- Docker (可选，用于容器化部署)
- CalDAV 账户 (如 iCloud、Google Calendar 等)
- AI API 密钥 (Gemini 或 DeepSeek)
- Webhook 通知服务 (如 Gotify)

### 本地运行

1. **克隆项目**
   ```bash
   git clone https://github.com/Taskkillsqc/Chrona.git
   cd Chrona
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置设置**
   
   复制并编辑配置文件：
   ```bash
   cp config.yaml.example config.yaml
   ```
   
   **⚠️ LLM 选择建议**：
   - 🌟 **推荐**：使用云端 LLM（Gemini/DeepSeek）获得最佳稳定性和准确性
   - ⚡ **实验性**：本地 LLM 虽然免费但可能产生格式错误，影响提醒功能
   
   编辑 `config.yaml`：
   ```yaml
   # LLM 配置 (V3.0 新格式)
   # 选择一种配置方式：
   
   # 在线 API 配置（推荐）
   llm:
     provider: "gemini"  # gemini, deepseek, openai, custom
     api_key: "your-api-key-here"
     parameters:
       temperature: 0.7
       max_tokens: 1000
   
   # 或者本地 LLM 配置 🆕
   # ⚠️ 重要提醒：本地模型可能生成不规范的JSON格式，导致部分事件无法正确分析和提醒
   # 建议：生产环境优先使用云端LLM（Gemini/DeepSeek等）以确保稳定性
   # llm:
   #   provider: "local"
   #   local:
   #     enabled: true
   #     model_path: "./models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
   #     n_ctx: 4096
   #     n_threads: 4
   #   parameters:
   #     temperature: 0.3  # 降低温度提高输出稳定性
   #     max_tokens: 500   # 限制输出长度减少格式错误
   #     top_p: 0.8        # 减少随机性
   
   # CalDAV 配置
   # 单个供应商（向后兼容）
   caldav:
     url: "https://caldav.icloud.com"
     username: "your-icloud@example.com"
     password: "your-app-specific-password"
   
   # 或者多供应商配置 🆕
   # caldav:
   #   providers:
   #     icloud:
   #       url: "https://caldav.icloud.com"
   #       username: "your-icloud@icloud.com"
   #       password: "your-icloud-app-password"
   #     google:
   #       url: "https://apidata.googleusercontent.com/caldav/v2/your-email@gmail.com/events"
   #       username: "your-email@gmail.com"
   #       password: "your-google-app-password"
   
   # 数据库配置
   database: "./data/agent.db"
   
   # Webhook 通知配置
   webhook_url: "https://your.webhook.endpoint"
   webhook_type: "gotify"  # gotify, slack, generic, or custom
   
   # 心跳包配置（可选）
   heartbeat:
     enabled: true
     url: "https://uptime-kuma.example.com/api/push/xxxxx"
     interval: 60
   
   # API服务配置（可选）
   api:
     enabled: true
     host: "0.0.0.0"
     port: 8000
     # CORS跨域配置（前端Web应用必需）
     cors:
       enabled: true
       allow_origins: ["*"]  # 开发环境，生产环境建议指定具体域名
       allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
       allow_headers: ["*"]
       allow_credentials: false
   ```

4. **运行程序**
   ```bash
   python agent.py
   ```
   
   启动时会显示功能状态：
   ```
   🔧 功能状态:
   💗 心跳包: 已启用 (间隔: 60秒)
   🌐 API服务: 已启用
      地址: http://0.0.0.0:8000
      文档: http://0.0.0.0:8000/docs
   ```

5. **验证安装**
   ```bash
   # 运行完整性检查
   python check.py
   ```
   
   这将检查：
   - ✅ 所有必要文件是否存在
   - ✅ Python 依赖是否已安装
   - ✅ 配置文件是否正确
   - ✅ Webhook 推送功能是否正常（支持 Gotify、Slack、通用、自定义格式）
   - ✅ 心跳包功能是否可用
   - ✅ API 功能是否正常

### 🏠 本地 LLM 快速入门 🆕

**⚠️ 重要提醒**: 本地模型为实验性功能，建议仅用于测试环境。

**已知限制**：
- 📉 约 30-50% 概率生成错误 JSON 格式
- ⚠️ 可能导致事件分析失败和提醒缺失
- 🎯 生产环境推荐使用云端 LLM（Gemini/DeepSeek）

如果您仍希望使用本地模型实现完全离线运行，可以按以下步骤快速配置：

1. **自动下载和配置本地模型（推荐）**
   ```bash
   # 运行自动配置脚本
   python download_model.py
   ```
   
   这将自动：
   - 📦 下载推荐的 GGUF 模型（约 1GB）
   - ⚙️ 生成本地 LLM 配置文件
   - 🧪 测试模型加载和推理
   - 📊 显示性能基准

2. **应用本地配置**
   ```bash
   # 复制生成的本地配置
   cp config_local_llm.yaml config.yaml
   
   # 或者手动编辑现有配置文件
   nano config.yaml
   ```

3. **验证本地模型**
   ```bash
   # 检查本地 LLM 配置
   python check.py
   ```

4. **启动程序**
   ```bash
   python agent.py
   ```

**本地 LLM 优势：**
- 🔒 **完全离线**：无需网络连接或 API 调用
- 💰 **无额外成本**：避免 API 调用费用
- 🚀 **响应快速**：本地推理，无网络延迟
- 🛡️ **隐私保护**：数据不离开本地设备

**本地 LLM 风险：**
- ⚠️ **格式错误**：JSON 解析失败率较高
- 📉 **准确性下降**：事件分析质量可能不如云端模型
- 🔧 **维护成本**：需要更多手动调优和监控

**推荐配置：**
- **轻量用户**: Qwen2.5-1.5B (1GB, 2-3GB 内存)
- **平衡用户**: Qwen2.5-3B (2GB, 4-5GB 内存)  
- **性能用户**: Qwen2.5-7B (4GB, 6-8GB 内存)

### Docker 部署

1. **使用 docker-compose（推荐）**
   ```bash
   # 编辑配置文件
   nano config.yaml
   
   # 启动服务
   docker-compose up -d
   
   # 查看日志
   docker-compose logs -f
   ```

2. **使用 Docker 直接运行**
   ```bash
   # 构建镜像
   docker build -t Chrona .
   
   # 运行容器
   docker run -d \
     --name chrona \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/config.yaml:/app/config.yaml:ro \
     Chrona
   ```

## 🚀 新功能快速入门

### 💗 心跳包功能快速配置

#### Uptime Kuma 配置
1. **在 Uptime Kuma 中创建 Push 监控**
   - 登录您的 Uptime Kuma 面板
   - 点击 "Add New Monitor"
   - 选择 "Push" 类型
   - 填写监控名称：`Chrona`
   - 复制生成的推送 URL

2. **配置 config.yaml**
   ```yaml
   heartbeat:
     enabled: true
     url: "https://your-uptime-kuma.com/api/push/AbCdEf123?status=up&msg=OK&ping="
     interval: 60  # 每60秒发送一次
     timeout: 10
     params:
       status: "up"
       msg: "Schedule Manager is running"
       ping: ""
   ```

#### Healthchecks.io 配置
1. **在 Healthchecks.io 创建检查**
   - 登录 [Healthchecks.io](https://healthchecks.io/)
   - 创建新的检查项目
   - 复制 Ping URL

2. **配置 config.yaml**
   ```yaml
   heartbeat:
     enabled: true
     url: "https://hc-ping.com/your-uuid-here"
     interval: 60
     timeout: 10
   ```

### 🌐 API 功能快速配置

#### 启用 API 服务
在 `config.yaml` 中添加：
```yaml
api:
  enabled: true
  host: "0.0.0.0"  # 允许外部访问，仅本地使用可设为 "127.0.0.1"
  port: 8000
  # CORS跨域配置（前端Web应用必需）
  cors:
    enabled: true
    allow_origins: ["*"]  # 开发环境：允许所有源
    # 生产环境建议：
    # allow_origins: ["http://localhost:3000", "https://yourdomain.com"]
    allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers: ["*"]
    allow_credentials: false
```

#### 🌍 CORS 配置说明

**CORS (跨域资源共享)** 允许前端Web应用访问API接口：

- **开发环境**: 使用 `allow_origins: ["*"]` 允许所有源访问
- **生产环境**: 指定具体的前端域名以提高安全性
- **认证应用**: 如需发送cookies或认证信息，设置 `allow_credentials: true`

**常见前端配置示例**：
```yaml
# React/Vue.js 开发服务器
allow_origins: ["http://localhost:3000", "http://localhost:8080"]

# 生产环境
allow_origins: ["https://app.yourdomain.com", "https://dashboard.yourdomain.com"]
```

#### 访问 API 文档
启动程序后，在浏览器中访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### 常用 API 接口测试
```bash
# 健康检查
curl http://localhost:8000/health

# 获取统计信息
curl http://localhost:8000/stats

# 获取即将到来的事件
curl http://localhost:8000/events/upcoming

# 查看心跳包状态
curl http://localhost:8000/heartbeat/status

# 手动发送心跳包
curl -X POST http://localhost:8000/heartbeat/send

# 测试CORS预检请求
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8000/health

# 前端JavaScript示例
# fetch('http://localhost:8000/events/upcoming')
#   .then(response => response.json())
#   .then(data => console.log(data))
#   .catch(error => console.error('Error:', error));
```

### 🧪 功能测试

#### 完整检查和测试
```bash
python check.py
```
运行项目完整性检查，包括：
- 文件结构检查
- 依赖验证  
- 配置验证
- Webhook推送验证
- 心跳包功能测试
- API功能测试

## ⚙️ 配置说明

### 基本配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `llm.provider` | LLM 提供商 | `gemini`、`deepseek`、`openai`、`custom` |
| `llm.api_key` | API 密钥 | `your-api-key` |
| `llm.parameters.temperature` | 创造性参数 | `0.7` |
| `llm.parameters.max_tokens` | 最大令牌数 | `1000` |
| `database` | 数据库路径 | `./data/agent.db` |
| `webhook_url` | 通知 Webhook 地址 | `https://api.example.com/webhook` |
| `webhook_type` | Webhook 类型 | `gotify`、`slack`、`generic` 或 `custom` |

**向后兼容：** 仍支持旧格式 `model` 和 `api_key`，但建议使用新的 `llm` 配置块。

### 心跳包配置

通过心跳包功能，程序可以定期向监控服务发送状态更新，确保监控系统能及时发现程序异常。

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `heartbeat.enabled` | 是否启用心跳包 | `true` 或 `false` |
| `heartbeat.url` | 心跳包推送URL | Uptime Kuma: `https://uptime.example.com/api/push/xxxxx` |
| `heartbeat.interval` | 发送间隔（秒） | `60` |
| `heartbeat.timeout` | 请求超时时间（秒） | `10` |
| `heartbeat.params.status` | 状态参数 | `up`、`down` 或 `ping` |
| `heartbeat.params.msg` | 消息内容 | `Schedule Manager is running` |
| `heartbeat.params.ping` | ping值（可选） | `10` |

**支持的监控服务：**
- **Uptime Kuma**: `https://uptime-kuma.example.com/api/push/AbCdEf123?status=up&msg=OK&ping=`
- **Healthchecks.io**: `https://hc-ping.com/your-uuid`
- **StatusCake**: `https://push.statuscake.com/?PK=your-key&TestID=your-test-id`
- **自定义HTTP端点**: 任何接受GET请求的HTTP服务

### API服务配置

启用API服务后，可以通过HTTP接口远程监控和控制程序。

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `api.enabled` | 是否启用API服务 | `true` 或 `false` |
| `api.host` | 监听地址 | `0.0.0.0`（所有接口）或 `127.0.0.1`（仅本地） |
| `api.port` | 监听端口 | `8000` |

**API接口列表：**

**基础接口：**
- `GET /` - 根路径，返回基本信息
- `GET /health` - 健康检查
- `GET /config` - 获取配置信息（隐藏敏感信息）

**统计接口：**
- `GET /stats` - 获取统计信息和心跳包状态

**事件接口：**
- `GET /events/upcoming` - 获取即将到来的事件
- `GET /events/recent?limit=10` - 获取最近的事件记录
- `GET /events/reminders` - 获取需要提醒的事件

**心跳包接口：**
- `GET /heartbeat/status` - 获取心跳包发送状态
- `POST /heartbeat/send` - 手动发送心跳包

**代理操作接口：**
- `POST /agent/fetch` - 手动触发事件获取和分析
- `POST /agent/check-reminders` - 手动触发提醒检查

**API文档：**
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### CalDAV 配置

Chrona 支持单个或多个 CalDAV 提供商，让您可以从不同的日历服务获取日程。

#### 单个提供商配置（向后兼容）

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `caldav.url` | CalDAV 服务器地址 | `https://caldav.icloud.com` |
| `caldav.username` | 用户名/邮箱 | `user@example.com` |
| `caldav.password` | 密码（建议使用应用专用密码） | `app-specific-password` |

```yaml
caldav:
  url: "https://caldav.icloud.com"
  username: "your-email@icloud.com"
  password: "your-app-specific-password"
```

#### 多提供商配置 🆕

**方式一：命名提供商格式（推荐）**
```yaml
caldav:
  providers:
    icloud:
      url: "https://caldav.icloud.com"
      username: "your-icloud@icloud.com"
      password: "your-icloud-app-password"
    
    google:
      url: "https://apidata.googleusercontent.com/caldav/v2/your-email@gmail.com/events"
      username: "your-email@gmail.com"
      password: "your-google-app-password"
    
    outlook:
      url: "https://outlook.live.com/owa/"
      username: "your-email@outlook.com"
      password: "your-outlook-password"
```

**方式二：列表格式**
```yaml
caldav:
  - name: "iCloud"
    url: "https://caldav.icloud.com"
    username: "your-icloud@icloud.com"
    password: "your-icloud-app-password"
  
  - name: "Google Calendar"
    url: "https://apidata.googleusercontent.com/caldav/v2/your-email@gmail.com/events"
    username: "your-email@gmail.com"
    password: "your-google-app-password"
```

**多提供商特性：**
- 🔄 **并发获取**: 同时从多个服务获取事件，提高效率
- 🏷️ **来源标识**: 自动标记事件来源，如 "工作日历 (iCloud)"
- ⚡ **容错处理**: 单个服务故障不影响其他服务
- 📊 **统一管理**: 所有日历事件在一个界面中统一显示

### 支持的 CalDAV 服务

#### 主流服务配置

| 服务 | URL | 说明 |
|------|-----|------|
| **iCloud** | `https://caldav.icloud.com` | Apple 的日历服务 |
| **Google Calendar** | `https://apidata.googleusercontent.com/caldav/v2/` | Google 的日历服务 |
| **Outlook/Exchange** | `https://outlook.live.com/owa/` | Microsoft 的邮箱和日历服务 |
| **Yahoo** | `https://caldav.calendar.yahoo.com` | Yahoo 的日历服务 |

#### 获取配置信息

**iCloud:**
1. 访问 [appleid.apple.com](https://appleid.apple.com/)
2. 登录并生成应用专用密码
3. 使用该密码作为 CalDAV 密码

**Google Calendar:**
1. 访问 [Google Calendar 设置](https://calendar.google.com/calendar/u/0/r/settings/export)
2. 获取您的日历 ID
3. 使用应用密码进行身份验证

**Outlook:**
1. 启用 IMAP/CalDAV 访问
2. 使用您的 Outlook 账户凭据

#### 自定义 CalDAV 服务

Chrona 支持任何标准的 CalDAV 服务：

```yaml
caldav:
  providers:
    custom_server:
      url: "https://your-caldav-server.com"
      username: "your-username"
      password: "your-password"
```

### Webhook 通知配置

系统支持多种 Webhook 通知格式，通过 `webhook_type` 配置项选择：

#### Gotify 通知

Gotify 是一个简单的自托管通知服务器。

**配置示例：**
```yaml
webhook_url: "https://your-gotify-server.com/message?token=YOUR_TOKEN"
webhook_type: "gotify"
```

**特性：**
- 支持优先级设置（重要事件优先级为 8，普通事件为 5）
- 支持 Markdown 格式内容
- 附加事件元数据信息

#### Slack 通知

通过 Slack Incoming Webhooks 发送通知。

**配置示例：**
```yaml
webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
webhook_type: "slack"
```

**特性：**
- 使用 Slack Blocks 格式
- 支持富文本格式
- 结构化信息展示

#### 自定义 Webhook 🆕

完全自定义的 Webhook 格式，适用于任何第三方服务。

**配置示例：**
```yaml
webhook_type: "custom"
webhook_custom:
  enabled: true
  url: "https://your-custom-api.com/notifications"
  method: "POST"  # 支持 GET, POST, PUT
  timeout: 30
  headers:
    Authorization: "Bearer your-api-token"
    Content-Type: "application/json"
    X-Custom-Header: "custom-value"
  payload_template: |
    {
      "alert": {
        "title": {{title}},
        "message": {{body}},
        "timestamp": {{timestamp}},
        "priority": {{priority}},
        "event": {
          "summary": {{event.summary}},
          "start_time": {{event.start_time}},
          "calendar": {{event.calendar_name}},
          "duration": {{event.duration_minutes}}
        },
        "analysis": {
          "important": {{analysis.important}},
          "reason": {{analysis.reason}}
        }
      }
    }
```

**特性：**
- **完全自定义请求格式**：支持任意 JSON 结构
- **模板变量系统**：使用 `{{variable}}` 格式动态插入数据
- **多种 HTTP 方法**：支持 GET、POST、PUT 请求
- **自定义请求头**：支持认证、内容类型等任意请求头
- **灵活的数据映射**：可访问事件和 AI 分析的所有字段

**可用变量：**

完整的模板变量系统，支持嵌套访问：

**基础变量：**
- `{{title}}` - 通知标题
- `{{body}}` - 通知内容
- `{{timestamp}}` - 时间戳
- `{{priority}}` - 优先级（数字）
- `{{event.summary}}` - 事件标题
- `{{event.description}}` - 事件描述
- `{{event.start_time}}` - 开始时间
- `{{event.calendar_name}}` - 日历名称
- `{{event.duration_minutes}}` - 持续时间（分钟）
- `{{analysis.important}}` - 是否重要（true/false）
- `{{analysis.need_remind}}` - 是否需要提醒
- `{{analysis.reason}}` - AI 分析原因
- `{{analysis.task}}` - 任务描述

**事件详细信息：**
- `{{event.end_time}}` - 结束时间
- `{{event.location}}` - 事件地点（如果有）
- `{{event.organizer}}` - 组织者信息（如果有）
- `{{event.uid}}` - 事件唯一标识符

**系统信息：**
- `{{system.hostname}}` - 主机名
- `{{system.timestamp_iso}}` - ISO 格式时间戳

**使用示例：**

```yaml
# Discord Webhook 示例
webhook_custom:
  url: "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"
  method: "POST"
  headers:
    Content-Type: "application/json"
  payload_template: |
    {
      "embeds": [{
        "title": "📅 日程提醒",
        "description": {{event.summary}},
        "color": 3447003,
        "fields": [
          {
            "name": "⏰ 开始时间",
            "value": {{event.start_time}},
            "inline": true
          },
          {
            "name": "🗂️ 日历",
            "value": {{event.calendar_name}},
            "inline": true
          },
          {
            "name": "🎯 任务",
            "value": {{analysis.task}},
            "inline": false
          }
        ],
        "timestamp": {{system.timestamp_iso}}
      }]
    }

# 企业微信群机器人示例
webhook_custom:
  url: "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"
  method: "POST"
  headers:
    Content-Type: "application/json"
  payload_template: |
    {
      "msgtype": "markdown",
      "markdown": {
        "content": "## 📅 日程提醒\n\n> **事件**: {{event.summary}}\n> **时间**: {{event.start_time}}\n> **日历**: {{event.calendar_name}}\n> **重要**: {{analysis.important}}\n> **任务**: {{analysis.task}}"
      }
    }

# 钉钉群机器人示例
webhook_custom:
  url: "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
  method: "POST"
  headers:
    Content-Type: "application/json"
  payload_template: |
    {
      "msgtype": "actionCard",
      "actionCard": {
        "title": "📅 {{event.summary}}",
        "text": "### 日程提醒\n\n**事件**: {{event.summary}}\n\n**时间**: {{event.start_time}}\n\n**日历**: {{event.calendar_name}}\n\n**重要程度**: {{analysis.important}}\n\n**建议任务**: {{analysis.task}}",
        "btnOrientation": "0"
      }
    }
```

#### 通用 Webhook

适用于简单的自定义通知服务。

**配置示例：**
```yaml
webhook_url: "https://your-custom-webhook.com/notify"
webhook_type: "generic"
```

**特性：**
- JSON 格式数据
- 包含完整事件和分析信息
- 易于集成其他服务

## 🔧 LLM API 配置

### V3.0 新配置方式（推荐）

#### Gemini API

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建 API 密钥
3. 在配置文件中设置：
   ```yaml
   llm:
     provider: "gemini"
     api_key: "your-gemini-api-key"
     parameters:
       temperature: 0.7  # 创造性参数
       max_tokens: 1000  # 最大令牌数
       top_p: 0.9       # 核采样参数
   ```

#### DeepSeek API

1. 访问 [DeepSeek 控制台](https://platform.deepseek.com/api_keys)
2. 创建 API 密钥
3. 在配置文件中设置：
   ```yaml
   llm:
     provider: "deepseek"
     api_key: "your-deepseek-api-key"
     parameters:
       temperature: 0.7
       max_tokens: 1000
   ```

#### OpenAI API

1. 访问 [OpenAI 控制台](https://platform.openai.com/api-keys)
2. 创建 API 密钥
3. 在配置文件中设置：
   ```yaml
   llm:
     provider: "openai"
     api_key: "your-openai-api-key"
     parameters:
       temperature: 0.7
       max_tokens: 1000
       top_p: 0.9
   ```

#### 自定义 API

支持任何兼容 OpenAI 格式的 API：
```yaml
llm:
  provider: "custom"
  custom:
    enabled: true
    url: "https://your-api-endpoint.com/v1/chat/completions"
    model: "your-model-name"
    headers:
      Authorization: "Bearer your-api-key"
    payload_format: "openai"
    response_format: "openai"
    timeout: 30
  parameters:
    temperature: 0.7
    max_tokens: 1000
```

#### 本地 LLM 模型（GGUF）🆕

Chrona 现在支持本地 GGUF 格式的 LLM 模型，可完全离线运行，保护隐私并降低成本。

**🔧 环境要求：**
- 支持 GGUF 格式的本地模型文件
- `llama-cpp-python` 库（会自动安装）
- 足够的系统内存（建议 8GB+）

**📦 安装和配置：**

1. **自动下载推荐模型（推荐）**
   ```bash
   # 运行自动下载脚本
   python download_model.py
   ```
   
   这将自动：
   - 下载推荐的 GGUF 模型到 `models/` 目录
   - 生成本地 LLM 配置示例
   - 测试模型加载和推理
   - 显示性能基准

2. **手动下载模型**
   
   创建 `models/` 目录并下载 GGUF 模型：
   ```bash
   mkdir models
   # 下载示例（使用 HuggingFace Hub）
   pip install huggingface-hub
   python -c "
   from huggingface_hub import hf_hub_download
   hf_hub_download(
       repo_id='Qwen/Qwen2.5-1.5B-Instruct-GGUF',
       filename='qwen2.5-1.5b-instruct-q4_k_m.gguf',
       local_dir='./models'
   )"
   ```

3. **配置本地 LLM**
   ```yaml
   llm:
     provider: "local"
     local:
       enabled: true
       model_path: "./models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
       # 模型参数
       n_ctx: 4096          # 上下文长度
       n_threads: 4         # CPU 线程数
       n_gpu_layers: 0      # GPU 层数（0=仅CPU）
       verbose: false       # 是否显示详细日志
     parameters:
       temperature: 0.7     # 创造性
       max_tokens: 1000     # 最大输出长度
       top_p: 0.9          # 核采样
       repeat_penalty: 1.1  # 重复惩罚
   ```

**🚀 推荐模型：**

| 模型名称 | 大小 | 内存需求 | 性能 | 推荐用途 |
|----------|------|----------|------|----------|
| Qwen2.5-1.5B-Instruct-Q4_K_M | ~1.0GB | 2-3GB | 快速 | 轻量部署，快速响应 |
| Qwen2.5-3B-Instruct-Q4_K_M | ~2.0GB | 4-5GB | 中等 | 平衡性能和质量 |
| Qwen2.5-7B-Instruct-Q4_K_M | ~4.0GB | 6-8GB | 高 | 高质量分析 |

**⚙️ 性能优化：**

```yaml
# CPU 优化配置
llm:
  provider: "local"
  local:
    model_path: "./models/your-model.gguf"
    n_ctx: 2048          # 减少上下文长度
    n_threads: 8         # 使用更多 CPU 线程
    n_batch: 512         # 批处理大小
    use_mlock: true      # 锁定内存

# GPU 加速配置（如有 CUDA GPU）
llm:
  provider: "local"
  local:
    model_path: "./models/your-model.gguf"
    n_gpu_layers: 35     # 将层加载到 GPU
    # 其他参数...
```

**🔍 依赖检查：**
运行配置检查会自动检测本地 LLM 依赖：
```bash
python check.py
```

**🛠️ 故障排除：**

**问题：模型加载失败**
```bash
# 检查模型文件是否存在和完整
python -c "
import os
model_path = './models/your-model.gguf'
if os.path.exists(model_path):
    print(f'模型文件存在，大小: {os.path.getsize(model_path) / 1024**3:.2f} GB')
else:
    print('模型文件不存在')
"
```

**问题：内存不足**
- 选择更小的模型（如 1.5B 而不是 7B）
- 减少 `n_ctx` 参数
- 设置 `n_gpu_layers: 0` 仅使用 CPU

**问题：推理速度慢**
- 增加 `n_threads` 到 CPU 核心数
- 使用量化程度更高的模型（Q4_K_M）
- 考虑 GPU 加速（如果可用）

**📚 更多信息：**
- 详细模型说明：查看 `models/README.md`
- 完整配置示例：查看 `config_local_llm.yaml`
- 模型下载工具：使用 `download_model.py`

### 向后兼容配置

#### 传统 Gemini 配置
```yaml
model: gemini
api_key: "your-gemini-api-key"
```

#### 传统 DeepSeek 配置
```yaml
model: deepseek
api_key: "your-deepseek-api-key"
```

## 📱 Gotify 通知服务配置

### 什么是 Gotify？

Gotify 是一个简单的自托管推送通知服务器，特别适合个人或小团队使用。它提供了：
- 📱 移动应用（Android）
- 🌐 Web 界面
- 🔧 简单的 REST API
- 🔒 完全自托管，数据隐私可控

### 快速部署 Gotify

#### 使用 Docker（推荐）

```bash
# 创建数据目录
mkdir -p /opt/gotify/data

# 运行 Gotify 容器
docker run -d \
  --name gotify \
  -p 8080:80 \
  -v /opt/gotify/data:/app/data \
  --restart unless-stopped \
  gotify/server:latest
```

#### 使用 Docker Compose

创建 `docker-compose.yml` 文件：
```yaml
version: '3.8'
services:
  gotify:
    image: gotify/server:latest
    container_name: gotify
    ports:
      - "8080:80"
    volumes:
      - ./gotify_data:/app/data
    restart: unless-stopped
    environment:
      - GOTIFY_DEFAULTUSER_NAME=admin
      - GOTIFY_DEFAULTUSER_PASS=your_password_here
```

运行：
```bash
docker-compose up -d
```

### 配置 Gotify

1. **访问 Gotify Web 界面**
   - 打开浏览器访问 `http://your-server:8080`
   - 使用默认账户登录（admin/admin）

2. **创建应用程序**
   - 在 "Apps" 页面点击 "Create App"
   - 输入应用名称：`Chrona`
   - 保存并复制生成的 Token

3. **配置 Chrona**
   ```yaml
   webhook_url: "http://your-gotify-server:8080/message?token=YOUR_TOKEN"
   webhook_type: "gotify"
   ```

4. **安装移动应用**
   - 下载 [Gotify Android 应用](https://github.com/gotify/android/releases)
   - 添加服务器：`http://your-gotify-server:8080`
   - 使用您的账户登录

### Gotify 优先级说明

Chrona 会根据事件重要性自动设置通知优先级：

| 优先级 | 说明 | 使用场景 |
|--------|------|----------|
| 8 | 高优先级 | 重要事件（`important: true`） |
| 5 | 普通优先级 | 一般事件 |

### 安全建议

1. **修改默认密码**：首次登录后立即修改默认的 admin 密码
2. **使用 HTTPS**：在生产环境中配置 SSL/TLS
3. **防火墙规则**：限制 Gotify 服务器的访问
4. **定期备份**：备份 Gotify 数据目录

## 📊 使用场景

### 工作场景
- 会议提醒
- 截止日期提醒
- 重要约会提醒

### 个人场景
- 生日提醒
- 约会提醒
- 活动提醒

### 监控场景 🆕
- **Uptime Kuma 集成**: 实时监控程序运行状态
- **API 监控**: 通过接口查看程序健康状态和统计信息
- **远程管理**: 通过 API 远程触发事件获取和提醒检查
- **状态看板**: 实时查看心跳包发送状态和错误统计

### API 使用示例 🆕

```bash
# 检查程序健康状态
curl http://localhost:8000/health

# 获取统计信息
curl http://localhost:8000/stats

# 查看即将到来的事件
curl http://localhost:8000/events/upcoming

# 手动触发事件获取
curl -X POST http://localhost:8000/agent/fetch

# 查看心跳包状态
curl http://localhost:8000/heartbeat/status

# 手动发送心跳包
curl -X POST http://localhost:8000/heartbeat/send

# 创建新的日程事件 🆕
curl -X POST "http://localhost:8000/events/create" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "会议标题",
    "start_time": "2025-06-25T14:30:00",
    "duration_minutes": 60,
    "provider_name": "iCloud",
    "calendar_name": "工作",
    "description": "会议描述"
  }'

# 最简单的创建事件（使用默认提供商和日历）
curl -X POST "http://localhost:8000/events/create" \
  -H "Content-Type: application/json" \
  -d '{
    "summary": "会议标题",
    "start_time": "2025-06-25T14:30:00",
    "duration_minutes": 60
  }'

# 获取可用的提供商和日历
curl http://localhost:8000/providers
curl http://localhost:8000/calendars
```

## � 创建事件API参数说明

### 必填参数
- `summary`: 事件标题
- `start_time`: 开始时间（ISO格式，如 "2025-06-25T14:30:00"）
- `duration_minutes`: 持续时间（分钟）

### 可选参数
- `provider_name`: 提供商名称（不指定时使用配置文件中的第一个提供商）
- `calendar_name`: 日历名称（不指定时使用该提供商的第一个日历）
- `description`: 事件描述

### 默认行为
> ⚠️ **重要**: 当不指定 `provider_name` 和 `calendar_name` 时，事件将被创建到配置文件中第一个提供商的第一个日历中。建议明确指定以确保事件创建到正确的位置。

## �🔔 通知格式

### Gotify 格式
```json
{
  "title": "📅 日程提醒: 项目评审会议",
  "message": "⏰ 开始时间: 2025-06-19 14:00:00\n⏰ 结束时间: 2025-06-19 15:30:00\n⏱️ 持续时间: 1小时30分钟\n🗂️ 日历: 工作日历\n📝 描述: 讨论Q2项目进展和下阶段计划\n🎯 任务: 参加项目评审会议\n⭐ 重要程度: 高\n⏱️ 建议提前: 15分钟\n💭 分析: 基于工作日历判断，这是重要的工作会议",
  "priority": 8,
  "extras": {
    "client::display": {
      "contentType": "text/markdown"
    },
    "event": {
      "summary": "项目评审会议",
      "description": "讨论Q2项目进展和下阶段计划",
      "start_time": "2025-06-19 14:00:00",
      "calendar_name": "工作日历"
    },
    "analysis": {
      "task": "参加项目评审会议",
      "important": true,
      "need_remind": true,
      "minutes_before_remind": 15,
      "reason": "基于工作日历判断，这是重要的工作会议"
    }
  }
}
```

### Slack 格式
```json
{
  "text": "📅 日程提醒: 会议标题",
  "blocks": [
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*📅 会议标题*"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*⏰ 时间:*\n2024-01-01 14:00:00"
        },
        {
          "type": "mrkdwn",
          "text": "*⏱️ 建议提前:*\n15分钟"
        }
      ]
    }
  ]
}
```

### 通用 Webhook 格式
```json
{
  "title": "📅 日程提醒: 会议标题",
  "body": "⏰ 时间: 2024-01-01 14:00:00\n📝 描述: 会议描述\n⏱️ 建议提前: 15分钟",
  "timestamp": "2024-01-01T13:45:00",
  "event": {
    "summary": "会议标题",
    "description": "会议描述",
    "start_time": "2024-01-01 14:00:00"
  },
  "analysis": {
    "task": "参加团队会议",
    "important": true,
    "need_remind": true,
    "minutes_before_remind": 15,
    "reason": "重要的团队会议需要提前准备"
  }
}
```

## 📁 项目结构

```
Chrona/
├── agent.py                 # 主应用程序入口
├── config.py               # 配置加载器
├── config.yaml.example     # 配置文件模板
├── check.py                # 项目完整性检查工具
├── requirements.txt        # Python依赖
├── Dockerfile             # Docker镜像构建文件
├── docker-compose.yml     # Docker Compose配置
├── start.sh               # 启动脚本
├── stop.sh                # 停止脚本
├── LICENSE                # MIT许可证
├── README.md              # 项目说明
├── .gitignore             # Git忽略文件
├── ai/                    # AI分析模块
│   ├── __init__.py
│   └── LLM_agent.py       # Gemini/DeepSeek API接口
├── caldav_client/         # CalDAV客户端模块
│   ├── __init__.py
│   └── caldav_client.py   # CalDAV协议实现
├── memory/                # 数据存储模块
│   ├── __init__.py
│   └── database.py        # SQLite数据库操作
├── notifier/              # 通知模块
│   ├── __init__.py
│   └── webhook.py         # Webhook通知实现
├── heartbeat/             # 心跳包模块 🆕
│   ├── __init__.py
│   └── heartbeat.py       # 心跳包发送器
├── api/                   # API服务模块 🆕
│   ├── __init__.py
│   └── api_server.py      # FastAPI服务器
└── data/                  # 数据目录(运行时创建)
    └── agent.db           # SQLite数据库文件
```

## 🗄️ 数据库结构

### events 表
存储日程事件和 AI 分析结果
- `id`: 主键
- `uid`: 事件唯一标识
- `summary`: 事件标题
- `description`: 事件描述
- `start_time`: 开始时间
- `end_time`: 结束时间
- `duration_minutes`: 持续时间（分钟）
- `calendar_name`: 日历名称
- `result`: AI 分析结果（JSON）
- `reminded`: 是否已提醒
- `created_at`: 创建时间
- `updated_at`: 更新时间

### reminders 表
存储提醒发送记录
- `id`: 主键
- `event_id`: 关联事件 ID
- `sent_at`: 发送时间
- `status`: 发送状态

## 🛠️ 开发和调试

### 查看日志
```bash
# Docker 环境
docker-compose logs -f Chrona

# 本地环境
python agent.py
```

### 测试功能 🆕
```bash
# 项目完整性和功能检查
python check.py
```

### 测试 Webhook
程序启动时会自动发送测试通知，确保 Webhook 配置正确。

### 测试 API 接口 🆕
```bash
# 测试健康检查
curl http://localhost:8000/health

# 查看 API 文档
# 在浏览器中打开: http://localhost:8000/docs
```

### 测试心跳包 🆕
```bash
# 查看心跳包状态
curl http://localhost:8000/heartbeat/status

# 手动发送心跳包
curl -X POST http://localhost:8000/heartbeat/send
```

### 手动触发分析
```python
from caldav_client.caldav_client import get_upcoming_events
from ai.LLM_agent import analyze_event
from config import CONFIG

events = get_upcoming_events(CONFIG['caldav'])
for event in events:
    result = analyze_event(event['summary'], event['description'], CONFIG)
    print(result)
```

## 🔧 故障排除

### 心跳包相关问题

1. **心跳包发送失败**
   ```bash
   # 检查心跳包状态
   curl http://localhost:8000/heartbeat/status
   
   # 查看错误次数和最后发送时间
   ```

2. **URL 配置错误**
   - 检查 Uptime Kuma 或监控服务的 URL 是否正确
   - 确认网络连接正常
   - 验证推送 Token 是否有效

3. **网络权限问题**
   - 检查防火墙设置
   - 确认监控服务允许接收推送
   - 验证 SSL 证书是否有效

### API 相关问题

1. **端口占用**
   ```bash
   # 检查端口是否被占用
   netstat -an | grep 8000
   
   # 或者修改配置文件中的端口
   ```

2. **访问权限**
   - 检查 host 配置是否正确
   - 确认防火墙允许相应端口访问
   - 验证绑定权限

3. **依赖包问题**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt
   ```

### 本地 LLM 相关问题 🆕

1. **llama-cpp-python 安装失败**
   ```bash
   # Windows 系统可能需要额外工具
   # 安装 Microsoft C++ Build Tools
   # 或者使用预编译版本：
   pip install llama-cpp-python --only-binary=llama-cpp-python
   ```

2. **模型加载失败**
   ```bash
   # 检查模型文件是否存在
   python -c "
   import os
   model_path = './models/your-model.gguf'
   if os.path.exists(model_path):
       size_gb = os.path.getsize(model_path) / (1024**3)
       print(f'模型文件存在，大小: {size_gb:.2f} GB')
   else:
       print('模型文件不存在，请重新下载')
   "
   
   # 测试模型兼容性
   python -c "
   try:
       from llama_cpp import Llama
       print('llama-cpp-python 已正确安装')
   except ImportError:
       print('llama-cpp-python 未安装或安装有问题')
   "
   ```

3. **内存不足错误**
   ```bash
   # 选择更小的模型或调整参数
   # 在 config.yaml 中：
   # n_ctx: 2048      # 减少上下文长度
   # n_batch: 256     # 减少批处理大小
   ```

4. **推理速度过慢**
   ```bash
   # 检查 CPU 使用情况并调整线程数
   # 在 config.yaml 中：
   # n_threads: 8     # 设置为 CPU 核心数
   # use_mlock: true  # 锁定内存提高性能
   ```

5. **CUDA/GPU 相关问题**
   ```bash
   # 检查 CUDA 是否可用
   python -c "
   try:
       import torch
       print(f'CUDA 可用: {torch.cuda.is_available()}')
       if torch.cuda.is_available():
           print(f'CUDA 设备数: {torch.cuda.device_count()}')
   except ImportError:
       print('PyTorch 未安装，无法检查 CUDA')
   "
   
   # 如果 CUDA 不可用，设置仅使用 CPU
   # n_gpu_layers: 0
   ```

6. **配置检查和测试**
   ```bash
   # 运行配置检查，会自动检测本地 LLM 问题
   python check.py
   
   # 使用模型下载工具重新配置
   python download_model.py
   ```

### 监控和性能

#### 监控面板示例脚本
创建一个简单的监控脚本：

```bash
#!/bin/bash
# monitor.sh - 简单的API监控脚本

API_URL="http://localhost:8000"

echo "🔍 检查程序状态..."

# 健康检查
health=$(curl -s "$API_URL/health" | jq -r '.status')
if [ "$health" = "healthy" ]; then
    echo "✅ 程序健康状态: $health"
else
    echo "❌ 程序健康检查失败"
    exit 1
fi

# 获取统计信息
stats=$(curl -s "$API_URL/stats")
total_events=$(echo $stats | jq -r '.database_stats.total_events')
heartbeat_count=$(echo $stats | jq -r '.heartbeat_status.send_count')

echo "📊 统计信息:"
echo "   总事件数: $total_events"
echo "   心跳包发送次数: $heartbeat_count"

# 心跳包状态
heartbeat_status=$(curl -s "$API_URL/heartbeat/status")
heartbeat_running=$(echo $heartbeat_status | jq -r '.running')
heartbeat_errors=$(echo $heartbeat_status | jq -r '.error_count')

echo "💗 心跳包状态:"
echo "   运行状态: $heartbeat_running"
echo "   错误次数: $heartbeat_errors"

echo "✅ 监控检查完成"
```

使用方法：
```bash
chmod +x monitor.sh
./monitor.sh
```

### 最佳实践

#### 监控配置建议
- 心跳包间隔建议设置为 60-300 秒
- 配置多个监控服务以提高可靠性
- 设置适当的超时时间

#### API 安全建议
- 在生产环境中使用反向代理
- 配置适当的访问控制
- 考虑添加身份验证

#### 性能优化
- 根据实际需求调整发送间隔
- 监控 API 响应时间
- 定期检查内存和CPU使用情况

## 🔒 安全注意事项

⚠️ **重要提醒**: 
1. **配置文件安全**: `config.yaml` 包含敏感信息，已在 `.gitignore` 中排除
2. **API 密钥安全**: 请妥善保管您的 API 密钥，不要分享或提交到公共仓库
3. **应用专用密码**: CalDAV 建议使用应用专用密码而非主密码
4. **Webhook 安全**: 确保 Webhook 端点的安全性和访问控制
5. **网络安全**: 在生产环境中使用 HTTPS

### 配置文件管理
```bash
# 第一次运行时，复制示例配置
cp config.yaml.example config.yaml

# 编辑配置文件（添加您的真实凭据）
nano config.yaml

# config.yaml 不会被提交到 git（已在 .gitignore 中）
```

1. **API 密钥安全**: 不要将 API 密钥提交到版本控制系统
2. **应用专用密码**: CalDAV 建议使用应用专用密码而非主密码
3. **Webhook 安全**: 确保 Webhook 端点的安全性
4. **网络安全**: 在生产环境中使用 HTTPS

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

1. Fork 这个仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 安装开发依赖 (`pip install -r requirements.txt`)
4. 复制并配置 `config.yaml` (`cp config.yaml.example config.yaml`)
5. 运行完整性检查 (`python check.py`)
6. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
7. 推送到分支 (`git push origin feature/AmazingFeature`)
8. 开启一个 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 添加必要的注释和文档字符串
- 在提交前运行 `python check.py` 确保所有检查通过
- 保持敏感信息不被提交（使用 .gitignore）

## 📄 许可证

MIT License

## � 常见问题 (FAQ)

### 本地 LLM 相关问题

#### Q1: 本地模型响应格式错误怎么办？

**问题**: 本地 LLM 有时生成的 JSON 格式不规范，导致解析失败和事件提醒失效。

**⚠️ 重要警告**：
- 本地模型约有 **30-50%** 的概率生成错误格式
- 可能导致重要事件**无法正确分析和提醒**
- 生产环境强烈建议使用云端 LLM

**解决方案**: Chrona v3.0 已内置智能容错机制：

1. **自动 JSON 提取**: 从复杂响应中自动提取 JSON 对象
2. **容错解析**: JSON 格式错误时使用关键词分析
3. **优化提示词**: 为本地模型定制更严格的输出格式要求
4. **回退机制**: 解析失败时基于规则进行智能判断

**本地模型优化配置**:
```yaml
llm:
  local:
    enabled: true
    model_path: "models/Qwen3-1.7B-Q4_K_M.gguf"
    temperature: 0.1  # 极低温度提高稳定性
    top_p: 0.6        # 大幅减少随机性
    max_tokens: 300   # 限制输出长度
    repeat_penalty: 1.2  # 避免重复内容
```

**最佳实践**:
- 🌟 **生产环境**: 使用 Gemini（免费额度充足）或 DeepSeek（价格便宜）
- 🧪 **测试环境**: 可使用本地模型进行实验，但需密切监控输出质量
- 📊 **混合模式**: 重要日历使用云端 LLM，一般日历使用本地模型

#### Q2: 本地模型加载速度慢？

**优化建议**:
- 使用 SSD 存储模型文件
- 增加 `n_threads` 参数（CPU 核心数）
- 启用 GPU 加速（设置 `gpu_layers`）
- 选择更小的量化模型（如 Q4_K_M）

#### Q3: 依赖安装失败？

**Windows 用户**:
```powershell
# 1. 安装 Visual Studio Build Tools
# 2. 安装 CMake
# 3. 使用预编译版本
pip install llama-cpp-python --prefer-binary
```

**详细说明**: 参考 [models/README.md](models/README.md)

### CalDAV 连接问题

#### Q4: CalDAV 认证失败？

**常见原因**:
1. 密码错误（需要使用应用专用密码）
2. URL 格式不正确
3. 服务器不支持 CalDAV

**解决步骤**:
```bash
# 测试配置
python check.py
```

#### Q5: 多个日历服务部分失败？

Chrona 支持容错处理，单个服务失败不影响其他服务：

```yaml
caldav:
  providers:
    working_service:     # 正常工作的服务
      url: "https://caldav.icloud.com"
      # ...
    
    failing_service:     # 即使此服务失败
      url: "https://broken-service.com"
      # ...
```

**日志查看**: 检查终端输出中的错误信息

### Webhook 配置问题

#### Q6: Webhook 不触发？

**检查列表**:
- [ ] URL 是否可访问
- [ ] HTTP 方法是否正确
- [ ] 网络连接是否正常
- [ ] 服务器是否返回 200 状态码

**测试方法**:
```bash
# 手动测试 webhook
curl -X POST -H "Content-Type: application/json" \
  -d '{"test": "message"}' \
  https://your-webhook-url.com
```

### 性能优化

#### Q7: 系统资源占用高？

**优化配置**:
```yaml
# 减少检查频率
check_interval: 300  # 5分钟检查一次

# 本地模型优化
llm:
  local:
    context_length: 1024  # 减少上下文长度
    gpu_layers: 0         # 关闭 GPU（如果不需要）
```

#### Q8: 日程分析太慢？

**建议**:
1. 使用云端 LLM（Gemini/DeepSeek）获得更快响应
2. 优化本地模型参数：
   ```yaml
   temperature: 0.1      # 降低随机性，加快生成
   max_tokens: 300       # 减少输出长度
   ```

### 调试和日志

#### Q9: 如何启用详细日志？

```yaml
# 启用详细日志
llm:
  local:
    verbose: true

# 或在启动时
python agent.py --verbose
```

#### Q10: 如何报告问题？

提交 Issue 时请包含：
1. 完整的错误日志
2. 配置文件（删除敏感信息）
3. 系统环境信息
4. 重现步骤

**获取系统信息**:
```bash
python check.py --verbose
```

## �📞 支持

如有问题，请创建 Issue 或联系维护者。

## 📚 更多文档

- ⚙️ [配置文件模板](config.yaml.example) - 配置文件示例和说明
- 🤖 [本地模型指南](models/README.md) - 本地 LLM 详细配置说明

---

**🎉 Chrona v3.0 - 让您的日程管理更智能、更可靠！**

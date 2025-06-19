# Chrona

Chrona 是一个基于 Gemini API（可切换为 DeepSeek API）的智能日程提醒助手。

## 🆕 v2.0 新功能亮点

- 💗 **心跳包监控**: 支持向 Uptime Kuma、Healthchecks.io 等监控服务发送状态更新
- 🌐 **完整REST API**: 提供丰富的HTTP接口，支持远程监控和控制
- 📊 **实时状态监控**: 通过API实时查看程序运行状态、统计信息和心跳包状态
- 🔧 **远程操作**: 支持通过API远程触发事件获取、提醒检查等操作
- 📚 **自动API文档**: 内置Swagger UI和ReDoc文档，开箱即用
- 🧪 **测试工具**: 提供完整的功能测试脚本，确保部署正确

## ✨ 功能特性

- 🔄 **自动同步**: 每 10 分钟通过 CalDAV 获取接下来 1 小时的日程
- 🤖 **AI 分析**: 使用 Gemini/DeepSeek API 智能分析日程重要性和提醒需求
- 💾 **数据存储**: 本地 SQLite 数据库存储分析结果
- 📱 **智能通知**: 通过 Webhook 发送个性化提醒通知
- 🐳 **容器化部署**: 支持 Docker 和 docker-compose 部署
- 🔧 **灵活配置**: 支持多种 AI 模型和 CalDAV 服务
- 💗 **心跳包监控**: 定期向 Uptime Kuma 等监控服务发送状态更新
- 🌐 **REST API**: 完整的 API 接口支持远程监控和控制
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
   
   编辑 `config.yaml`：
   ```yaml
   model: gemini     # gemini 或 deepseek
   api_key: "your-api-key-here"
   caldav:
     url: "https://caldav.icloud.com"
     username: "your-icloud@example.com"
     password: "your-app-specific-password"
   database: "./data/agent.db"
   webhook_url: "https://your.webhook.endpoint"
   webhook_type: "gotify"  # gotify, slack, or generic
   
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
   - ✅ Webhook 推送功能是否正常（支持 Gotify、Slack、通用格式）
   - ✅ 心跳包功能是否可用
   - ✅ API 功能是否正常

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
     --name dummy_schedule_manager \
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

# 手动触发事件获取
curl -X POST http://localhost:8000/agent/fetch
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
| `model` | AI 模型选择 | `gemini` 或 `deepseek` |
| `api_key` | API 密钥 | `your-api-key` |
| `database` | 数据库路径 | `./data/agent.db` |
| `webhook_url` | 通知 Webhook 地址 | `https://api.example.com/webhook` |
| `webhook_type` | Webhook 类型 | `gotify`、`slack` 或 `generic` |

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

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `url` | CalDAV 服务器地址 | `https://caldav.icloud.com` |
| `username` | 用户名/邮箱 | `user@example.com` |
| `password` | 密码（建议使用应用专用密码） | `app-specific-password` |

### 支持的 CalDAV 服务

- **iCloud**: `https://caldav.icloud.com`
- **Google Calendar**: `https://apidata.googleusercontent.com/caldav/v2/`
- **Outlook**: `https://outlook.live.com/owa/`
- **Yahoo**: `https://caldav.calendar.yahoo.com`
- 其他支持 CalDAV 的服务

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

#### 通用 Webhook

适用于自定义或其他通知服务。

**配置示例：**
```yaml
webhook_url: "https://your-custom-webhook.com/notify"
webhook_type: "generic"
```

**特性：**
- JSON 格式数据
- 包含完整事件和分析信息
- 易于集成其他服务

## 🔧 API 配置

### Gemini API

1. 访问 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 创建 API 密钥
3. 在配置文件中设置：
   ```yaml
   model: gemini
   api_key: "your-gemini-api-key"
   ```

### DeepSeek API

1. 访问 [DeepSeek 控制台](https://platform.deepseek.com/api_keys)
2. 创建 API 密钥
3. 在配置文件中设置：
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
```

## 🔔 通知格式

### Gotify 格式
```json
{
  "title": "📅 日程提醒: 会议标题",
  "message": "⏰ 时间: 2024-01-01 14:00:00\n📝 描述: 会议描述\n⏱️ 建议提前: 15分钟",
  "priority": 8,
  "extras": {
    "client::display": {
      "contentType": "text/markdown"
    },
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

## 📞 支持

如有问题，请创建 Issue 或联系维护者。

## 📚 更多文档

- ⚙️ [配置文件模板](config.yaml.example) - 配置文件示例和说明

---

**🎉 Chrona v2.0 - 让您的日程管理更智能、更可靠！**

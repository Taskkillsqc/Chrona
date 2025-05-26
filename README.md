# Dummy Schedule Manager

Dummy Schedule Manager 是一个基于 Gemini API（可切换为 DeepSeek API）的智能日程提醒助手。

## ✨ 功能特性

- 🔄 **自动同步**: 每 10 分钟通过 CalDAV 获取接下来 1 小时的日程
- 🤖 **AI 分析**: 使用 Gemini/DeepSeek API 智能分析日程重要性和提醒需求
- 💾 **数据存储**: 本地 SQLite 数据库存储分析结果
- 📱 **智能通知**: 通过 Webhook 发送个性化提醒通知
- 🐳 **容器化部署**: 支持 Docker 和 docker-compose 部署
- 🔧 **灵活配置**: 支持多种 AI 模型和 CalDAV 服务

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
   git clone <repository-url>
   cd dummy-schedule-manager
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
   ```

4. **运行程序**
   ```bash
   python agent.py
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
   - ✅ Gotify 推送功能是否正常

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
   docker build -t dummy-schedule-manager .
   
   # 运行容器
   docker run -d \
     --name dummy_schedule_manager \
     -v $(pwd)/data:/app/data \
     -v $(pwd)/config.yaml:/app/config.yaml:ro \
     dummy-schedule-manager
   ```

## ⚙️ 配置说明

### 基本配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `model` | AI 模型选择 | `gemini` 或 `deepseek` |
| `api_key` | API 密钥 | `your-api-key` |
| `database` | 数据库路径 | `./data/agent.db` |
| `webhook_url` | 通知 Webhook 地址 | `https://api.example.com/webhook` |

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

## 📊 使用场景

### 工作场景
- 会议提醒
- 截止日期提醒
- 重要约会提醒

### 个人场景
- 生日提醒
- 约会提醒
- 活动提醒

## 🔔 通知格式

### 标准 Webhook
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
dummy-schedule-manager/
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
│   └── gemini_agent.py    # Gemini/DeepSeek API接口
├── caldav_client/         # CalDAV客户端模块
│   ├── __init__.py
│   └── caldav_client.py   # CalDAV协议实现
├── memory/                # 数据存储模块
│   ├── __init__.py
│   └── database.py        # SQLite数据库操作
├── notifier/              # 通知模块
│   ├── __init__.py
│   └── webhook.py         # Webhook通知实现
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
docker-compose logs -f dummy-schedule-manager

# 本地环境
python agent.py
```

### 测试 Webhook
程序启动时会自动发送测试通知，确保 Webhook 配置正确。

### 手动触发分析
```python
from caldav_client.caldav_client import get_upcoming_events
from ai.gemini_agent import analyze_event
from config import CONFIG

events = get_upcoming_events(CONFIG['caldav'])
for event in events:
    result = analyze_event(event['summary'], event['description'], CONFIG)
    print(result)
```

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

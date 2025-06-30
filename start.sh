#!/bin/bash

# Chrona 启动脚本

set -e

echo "🚀 Chrona 启动脚本"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装 Python 3.8+"
    exit 1
fi

# 检查配置文件
if [ ! -f "config.yaml" ]; then
    echo "⚠️  配置文件不存在，正在创建示例配置..."
    if [ -f "config.yaml.example" ]; then
        cp config.yaml.example config.yaml
        echo "✅ 已创建 config.yaml，请编辑后重新运行"
        echo "📝 主要需要配置的项目："
        echo "   - api_key: 你的 Gemini 或 DeepSeek API 密钥"
        echo "   - caldav.username: 你的 CalDAV 用户名"
        echo "   - caldav.password: 你的 CalDAV 密码"
        echo "   - webhook_url: 你的 Webhook 通知地址"
        exit 1
    else
        echo "❌ 配置文件模板不存在"
        exit 1
    fi
fi

# 检查并创建数据目录
if [ ! -d "data" ]; then
    echo "📁 创建数据目录..."
    mkdir -p data
fi

# 检查并创建虚拟环境
VENV_DIR="venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 创建虚拟环境..."
    python3 -m venv "$VENV_DIR"
    echo "✅ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source "$VENV_DIR/bin/activate"
echo "✅ 虚拟环境已激活"

# 升级pip
echo "📦 升级pip..."
python -m pip install --upgrade pip

# 检查依赖
echo "🔍 安装 Python 依赖..."
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt
else
    echo "⚠️  requirements.txt 不存在，手动安装依赖..."
    python -m pip install caldav PyYAML requests vobject pytz fastapi uvicorn pydantic
fi

# 验证配置
echo "✅ 验证配置文件..."
python -c "
import yaml
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    required_fields = ['api_key', 'caldav', 'database', 'webhook_url']
    missing_fields = []
    
    for field in required_fields:
        if field not in config or not config[field]:
            missing_fields.append(field)
    
    if missing_fields:
        print(f'❌ 配置文件缺少必要字段: {missing_fields}')
        exit(1)
    
    if config['api_key'] == 'your-api-key-here':
        print('❌ 请在 config.yaml 中设置正确的 API 密钥')
        exit(1)
    
    print('✅ 配置文件验证通过')
    
except Exception as e:
    print(f'❌ 配置文件验证失败: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ 配置验证失败，请检查 config.yaml 文件"
    exit 1
fi

echo ""
echo "🎯 准备启动 Chrona..."
echo "📊 当前配置："
python -c "
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
print(f\"  模型: {config.get('model', 'unknown')}\")
print(f\"  CalDAV: {config.get('caldav', {}).get('url', 'unknown')}\")
print(f\"  数据库: {config.get('database', 'unknown')}\")
print(f\"  Webhook: {config.get('webhook_url', 'unknown')[:50]}{'...' if len(config.get('webhook_url', '')) > 50 else ''}\")
"

echo ""
echo "🚀 启动程序..."
echo "💡 使用 Ctrl+C 停止程序"
echo "🔧 虚拟环境: $VENV_DIR"
echo ""

# 启动主程序
python agent.py

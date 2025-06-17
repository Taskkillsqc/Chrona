#!/usr/bin/env python3
"""
Dummy Schedule Manager 项目完整性检查
验证项目是否已正确构建并可以使用
"""

import os
import sys
import subprocess
import random
import requests
import yaml
from pathlib import Path

def check_files():
    """检查必要文件是否存在"""
    print("📁 检查项目文件...")
    
    required_files = [
        'agent.py',
        'config.py', 
        'config.yaml',
        'config.yaml.example',
        'requirements.txt',
        'Dockerfile',
        'docker-compose.yml',
        'README.md',
        'start.sh',
        'stop.sh',
        'caldav_client/__init__.py',
        'caldav_client/caldav_client.py',
        'ai/__init__.py',
        'ai/LLM_agent.py',
        'memory/__init__.py',
        'memory/database.py',
        'notifier/__init__.py',
        'notifier/webhook.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ 缺少文件:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    print("✅ 所有必要文件都存在")
    return True

def check_dependencies():
    """检查Python依赖"""
    print("\n📦 检查Python依赖...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        missing_deps = []
        for req in requirements:
            if req.strip():
                package = req.split('==')[0].strip()
                # 特殊处理PyYAML
                import_name = 'yaml' if package == 'PyYAML' else package.replace('-', '_')
                try:
                    __import__(import_name)
                    print(f"  ✅ {package}")
                except ImportError:
                    missing_deps.append(package)
                    print(f"  ❌ {package}")
        
        if missing_deps:
            print(f"\n❌ 缺少依赖包:")
            for dep in missing_deps:
                print(f"  - {dep}")
            print(f"\n💡 运行以下命令安装:")
            print(f"  pip install -r requirements.txt")
            return False
        
        print("✅ 所有依赖都已安装")
        return True
        
    except Exception as e:
        print(f"❌ 检查依赖时出错: {e}")
        return False

def check_configuration():
    """检查配置文件"""
    print("\n⚙️ 检查配置...")
    
    if not os.path.exists('config.yaml'):
        print("❌ config.yaml 不存在")
        if os.path.exists('config.yaml.example'):
            print("💡 请复制 config.yaml.example 到 config.yaml 并编辑")
        return False
    
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        required_keys = ['model', 'api_key', 'caldav', 'database', 'webhook_url']
        missing_keys = []
        
        for key in required_keys:
            if key not in config or not config[key]:
                missing_keys.append(key)
            else:
                print(f"  ✅ {key}")
        
        # 检查可选的 webhook_type 配置
        webhook_type = config.get('webhook_type', 'generic')
        print(f"  ✅ webhook_type ({webhook_type})")
        
        if webhook_type not in ['gotify', 'slack', 'generic']:
            print(f"  ⚠️  不支持的 webhook_type: {webhook_type}，将使用 generic 格式")
        
        if missing_keys:
            print(f"\n❌ 配置文件缺少字段:")
            for key in missing_keys:
                print(f"  - {key}")
            return False
        
        # 检查API密钥是否为默认值
        if config['api_key'] == 'your-api-key-here':
            print("⚠️  请设置正确的API密钥")
            return False
        
        print("✅ 配置文件格式正确")
        return True
        
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return False

def check_permissions():
    """检查脚本执行权限"""
    print("\n🔒 检查执行权限...")
    
    scripts = ['start.sh', 'stop.sh']
    
    for script in scripts:
        if os.path.exists(script):
            if os.access(script, os.X_OK):
                print(f"  ✅ {script}")
            else:
                print(f"  ❌ {script} (无执行权限)")
                print(f"     运行: chmod +x {script}")
        else:
            print(f"  ⚠️  {script} (不存在)")
    
    return True

def check_docker():
    """检查Docker配置"""
    print("\n🐳 检查Docker配置...")
    
    # 检查Docker是否安装
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✅ Docker: {result.stdout.strip()}")
        else:
            print("  ❌ Docker未正确安装")
            return False
    except:
        print("  ❌ Docker未安装或不可用")
        return False
    
    # 检查docker-compose
    try:
        result = subprocess.run(['docker', 'compose', 'version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"  ✅ Docker Compose: {result.stdout.strip()}")
        else:
            print("  ❌ Docker Compose未正确安装")
            return False
    except:
        print("  ❌ Docker Compose未安装或不可用")
        return False
    
    # 检查Dockerfile语法
    if os.path.exists('Dockerfile'):
        print("  ✅ Dockerfile存在")
    else:
        print("  ❌ Dockerfile不存在")
        return False
    
    # 检查docker-compose.yml语法
    if os.path.exists('docker-compose.yml'):
        try:
            result = subprocess.run(['docker', 'compose', 'config'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("  ✅ docker-compose.yml语法正确")
            else:
                print(f"  ❌ docker-compose.yml语法错误: {result.stderr}")
                return False
        except:
            print("  ❌ 无法验证docker-compose.yml")
            return False
    else:
        print("  ❌ docker-compose.yml不存在")
        return False
    
    return True

def check_webhook_push():
    """检查Webhook推送功能（支持不同类型）"""
    print("\n📱 检查Webhook推送功能...")
    
    try:
        # 加载配置
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        webhook_url = config.get('webhook_url')
        webhook_type = config.get('webhook_type', 'generic')
        
        if not webhook_url:
            print("❌ 配置文件中未找到webhook_url")
            return False
        
        print(f"📡 Webhook URL: {webhook_url}")
        print(f"🔧 Webhook类型: {webhook_type}")
        
        # 生成6位随机验证码
        verification_code = str(random.randint(100000, 999999))
        
        # 根据webhook类型构建不同格式的消息
        if webhook_type == "gotify":
            return check_gotify_push_specific(webhook_url, verification_code)
        elif webhook_type == "slack":
            return check_slack_push_specific(webhook_url, verification_code)
        else:
            return check_generic_push_specific(webhook_url, verification_code)
            
    except Exception as e:
        print(f"❌ Webhook推送检查失败: {e}")
        return False

def check_gotify_push_specific(webhook_url, verification_code):
    """检查Gotify格式推送"""
    message_data = {
        "title": "🔍 Dummy Schedule Manager 验证",
        "message": f"验证码: {verification_code}\n\n请在终端中输入此验证码以确认Gotify推送功能正常工作。",
        "priority": 5,
        "extras": {
            "client::display": {
                "contentType": "text/markdown"
            }
        }
    }
    
    print("📤 正在发送Gotify格式验证码...")
    return send_verification_and_check(webhook_url, message_data, verification_code)

def check_slack_push_specific(webhook_url, verification_code):
    """检查Slack格式推送"""
    message_data = {
        "text": "🔍 Dummy Schedule Manager 验证",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🔍 Dummy Schedule Manager 验证*\n\n验证码: `{verification_code}`\n\n请在终端中输入此验证码以确认Slack推送功能正常工作。"
                }
            }
        ]
    }
    
    print("📤 正在发送Slack格式验证码...")
    return send_verification_and_check(webhook_url, message_data, verification_code)

def check_generic_push_specific(webhook_url, verification_code):
    """检查通用格式推送"""
    from datetime import datetime
    
    message_data = {
        "title": "🔍 Dummy Schedule Manager 验证",
        "body": f"验证码: {verification_code}\n\n请在终端中输入此验证码以确认Webhook推送功能正常工作。",
        "timestamp": datetime.now().isoformat()
    }
    
    print("📤 正在发送通用格式验证码...")
    return send_verification_and_check(webhook_url, message_data, verification_code)

def send_verification_and_check(webhook_url, message_data, verification_code):
    """发送验证码并检查用户输入"""
    try:
        response = requests.post(webhook_url, json=message_data, timeout=10)
        
        if response.status_code == 200:
            print("✅ 验证码已发送")
            
            # 等待用户输入验证码
            print("\n📱 请检查您的通知应用，然后输入收到的6位验证码:")
            
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    user_input = input("验证码 (6位数字): ").strip()
                    
                    if user_input == verification_code:
                        print("✅ 验证码正确！Webhook推送功能正常工作")
                        return True
                    else:
                        remaining = max_attempts - attempt - 1
                        if remaining > 0:
                            print(f"❌ 验证码错误，还有 {remaining} 次机会")
                        else:
                            print("❌ 验证码错误次数过多")
                except KeyboardInterrupt:
                    print("\n⚠️ 用户取消验证")
                    return False
                except Exception as e:
                    print(f"❌ 输入错误: {e}")
                    return False
            
            print("❌ Webhook推送验证失败")
            return False
            
        else:
            print(f"❌ 发送失败: HTTP {response.status_code}")
            print(f"响应: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查网络连接和Webhook服务器状态")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败，请检查网络连接和Webhook服务器地址")
        return False
    except Exception as e:
        print(f"❌ 发送请求失败: {e}")
        return False

def show_usage_instructions():
    """显示使用说明"""
    print("\n📖 使用说明")
    print("=" * 40)
    
    print("\n1. 本地运行:")
    print("   ./start.sh")
    print("   或")
    print("   python agent.py")
    
    print("\n2. Docker运行:")
    print("   docker-compose up -d")
    
    print("\n3. 查看日志:")
    print("   # 本地运行时直接在终端查看")
    print("   # Docker运行时:")
    print("   docker-compose logs -f")
    
    print("\n4. 停止服务:")
    print("   # 本地运行: Ctrl+C 或")
    print("   ./stop.sh")
    print("   # Docker运行:")
    print("   docker-compose down")

def main():
    """主检查函数"""
    print("🔍 Dummy Schedule Manager 项目完整性检查")
    print("=" * 50)
    
    checks = [
        ("文件检查", check_files),
        ("依赖检查", check_dependencies),
        ("配置检查", check_configuration),
        ("权限检查", check_permissions),
        ("Docker检查", check_docker),
        ("Webhook推送检查", check_webhook_push),
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            if check_func():
                passed += 1
        except Exception as e:
            print(f"❌ {check_name}失败: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 检查结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 项目构建完成！所有检查都通过了！")
        show_usage_instructions()
        return True
    else:
        print("❌ 部分检查失败，请根据上述提示修复问题")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

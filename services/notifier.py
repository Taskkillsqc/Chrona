import requests
import json
import re
from datetime import datetime

def send_notification(event, result, webhook_url, webhook_type="generic", config=None):
    """发送Webhook通知"""
    try:
        # 根据webhook类型构造不同格式的数据
        if webhook_type == "gotify":
            return send_gotify_notification(event, result, webhook_url)
        elif webhook_type == "slack":
            return send_slack_notification(event, result, webhook_url)
        elif webhook_type == "custom":
            return send_custom_notification(event, result, webhook_url, config)
        else:
            return send_generic_notification(event, result, webhook_url)
            
    except Exception as e:
        print(f"❌ 发送通知时出现未知错误: {e}")
        return False

def send_gotify_notification(event, result, webhook_url):
    """发送Gotify格式的通知"""
    try:
        # Gotify消息格式
        title = f"📅 日程提醒: {event.get('summary', '未知事件')}"
        message = format_notification_body(event, result)
        
        # 根据重要性设置优先级
        priority = 8 if result.get('important', False) else 5
        
        data = {
            "title": title,
            "message": message,
            "priority": priority,
            "extras": {
                "client::display": {
                    "contentType": "text/markdown"
                },
                "event": {
                    "summary": event.get('summary', ''),
                    "description": event.get('description', ''),
                    "start_time": event.get('start_time', ''),
                    "calendar_name": event.get('calendar_name', ''),
                    "provider": event.get('provider', ''),
                    "uid": event.get('uid', '')
                },
                "analysis": result
            }
        }
        
        # 发送POST请求到Gotify
        response = requests.post(
            webhook_url, 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Gotify通知发送成功: {event.get('summary', '')}")
            return True
        else:
            print(f"❌ Gotify通知发送失败 ({response.status_code}): {event.get('summary', '')}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 网络错误，Gotify通知发送失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 发送Gotify通知时出现未知错误: {e}")
        return False

def send_generic_notification(event, result, webhook_url):
    """发送通用格式的Webhook通知"""
    try:
        # 构造通知数据
        data = {
            "title": f"📅 日程提醒: {event.get('summary', '未知事件')}",
            "body": format_notification_body(event, result),
            "timestamp": datetime.now().isoformat(),
            "event": {
                "summary": event.get('summary', ''),
                "description": event.get('description', ''),
                "start_time": event.get('start_time', ''),
                "calendar_name": event.get('calendar_name', ''),
                "provider": event.get('provider', ''),
                "uid": event.get('uid', '')
            },
            "analysis": result
        }
        
        # 发送POST请求
        response = requests.post(
            webhook_url, 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ 通知发送成功: {event.get('summary', '')}")
            return True
        else:
            print(f"❌ 通知发送失败 ({response.status_code}): {event.get('summary', '')}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 网络错误，通知发送失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 发送通知时出现未知错误: {e}")
        return False

def format_notification_body(event, result):
    """格式化通知内容"""
    lines = []
    
    # 基本信息
    if event.get('start_time'):
        lines.append(f"⏰ 开始时间: {event['start_time']}")
    
    if event.get('end_time'):
        lines.append(f"⏰ 结束时间: {event['end_time']}")
    
    if event.get('duration_minutes'):
        duration = event['duration_minutes']
        hours = duration // 60
        minutes = duration % 60
        if hours > 0:
            lines.append(f"⏱️ 持续时间: {hours}小时{minutes}分钟")
        else:
            lines.append(f"⏱️ 持续时间: {minutes}分钟")
    
    # 日历信息
    if event.get('calendar_name'):
        calendar_info = event['calendar_name']
        if event.get('provider'):
            calendar_info += f" (来自 {event['provider']})"
        lines.append(f"📅 日历: {calendar_info}")
    
    if event.get('description'):
        lines.append(f"📝 描述: {event['description']}")
    
    # AI分析结果
    if result.get('task'):
        lines.append(f"🎯 任务: {result['task']}")
    
    if result.get('important'):
        lines.append("⭐ 重要程度: 高")
    
    if result.get('minutes_before_remind'):
        lines.append(f"⏱️ 建议提前: {result['minutes_before_remind']}分钟")
    
    if result.get('reason'):
        lines.append(f"💭 分析: {result['reason']}")
    
    return "\n".join(lines)

def send_test_notification(webhook_url, webhook_type="generic", config=None):
    """发送测试通知"""
    test_event = {
        'summary': '测试通知',
        'description': '这是一个测试通知，用于验证Webhook是否正常工作',
        'start_time': datetime.now().isoformat(),
        'calendar_name': '测试日历',
        'provider': '测试提供商',
        'uid': 'test-notification'
    }
    
    test_result = {
        'task': '测试Webhook连接',
        'important': True,
        'need_remind': True,
        'minutes_before_remind': 5,
        'reason': '系统测试'
    }
    
    return send_notification(test_event, test_result, webhook_url, webhook_type, config)

def send_slack_notification(event, result, slack_webhook_url):
    """发送Slack格式的通知（可选）"""
    try:
        # Slack消息格式
        slack_data = {
            "text": f"📅 日程提醒: {event.get('summary', '未知事件')}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*📅 {event.get('summary', '未知事件')}*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*⏰ 时间:*\n{event.get('start_time', 'N/A')}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*⏱️ 建议提前:*\n{result.get('minutes_before_remind', 15)}分钟"
                        }
                    ]
                }
            ]
        }
        
        # 添加日历和提供商信息
        calendar_info = event.get('calendar_name', '')
        if event.get('provider'):
            calendar_info += f" (来自 {event['provider']})"
        
        if calendar_info:
            slack_data["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📅 日历:* {calendar_info}"
                }
            })
        
        if event.get('description'):
            slack_data["blocks"].append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*📝 描述:*\n{event['description']}"
                }
            })
        
        response = requests.post(
            slack_webhook_url,
            json=slack_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Slack通知发送失败: {e}")
        return False

def send_custom_notification(event, result, webhook_url, config):
    """发送自定义格式的Webhook通知"""
    try:
        # 获取自定义配置
        webhook_config = config.get('webhook_custom', {})
        
        if not webhook_config.get('enabled', False):
            print("❌ 自定义 webhook 未启用")
            return False
        
        # 构建变量字典
        variables = {
            'title': f"📅 日程提醒: {event.get('summary', '未知事件')}",
            'body': format_notification_body(event, result),
            'timestamp': datetime.now().isoformat(),
            'priority': 8 if result.get('important', False) else 5,
            'event': {
                'summary': event.get('summary', ''),
                'description': event.get('description', ''),
                'start_time': event.get('start_time', ''),
                'end_time': event.get('end_time', ''),
                'duration_minutes': event.get('duration_minutes', 0),
                'calendar_name': event.get('calendar_name', ''),
                'provider': event.get('provider', ''),
                'uid': event.get('uid', '')
            },
            'analysis': {
                'important': result.get('important', False),
                'need_remind': result.get('need_remind', False),
                'minutes_before_remind': result.get('minutes_before_remind', 15),
                'reason': result.get('reason', ''),
                'task': result.get('task', '')
            }
        }
        
        # 处理模板字符串
        payload_template = webhook_config.get('payload_template', '{}')
        payload_str = replace_template_variables(payload_template, variables)
        
        # 解析为 JSON
        try:
            payload = json.loads(payload_str)
        except json.JSONDecodeError as e:
            print(f"❌ 自定义 webhook 模板 JSON 解析失败: {e}")
            print(f"模板内容: {payload_str}")
            return False
        
        # 构建请求头
        headers = {"Content-Type": "application/json"}
        custom_headers = webhook_config.get('headers', {})
        headers.update(custom_headers)
        
        # 获取请求方法和超时时间
        method = webhook_config.get('method', 'POST').upper()
        timeout = webhook_config.get('timeout', 30)
        custom_url = webhook_config.get('url', webhook_url)
        
        # 发送请求
        if method == 'GET':
            response = requests.get(custom_url, params=payload, headers=headers, timeout=timeout)
        elif method == 'POST':
            response = requests.post(custom_url, json=payload, headers=headers, timeout=timeout)
        elif method == 'PUT':
            response = requests.put(custom_url, json=payload, headers=headers, timeout=timeout)
        else:
            print(f"❌ 不支持的 HTTP 方法: {method}")
            return False
        
        if response.status_code in [200, 201, 202, 204]:
            print(f"✅ 自定义通知发送成功: {event.get('summary', '')}")
            return True
        else:
            print(f"❌ 自定义通知发送失败 ({response.status_code}): {event.get('summary', '')}")
            print(f"响应内容: {response.text[:200]}...")
            return False
            
    except requests.RequestException as e:
        print(f"❌ 网络错误，自定义通知发送失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 发送自定义通知时出现未知错误: {e}")
        return False

def replace_template_variables(template, variables):
    """递归替换模板变量"""
    def replace_var(match):
        var_path = match.group(1)
        keys = var_path.split('.')
        
        try:
            value = variables
            for key in keys:
                value = value[key]
            
            # 根据类型进行格式化
            if isinstance(value, bool):
                return 'true' if value else 'false'
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, str):
                # 转义字符串中的特殊字符
                escaped_value = value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                return f'"{escaped_value}"'
            else:
                return json.dumps(value)
        except (KeyError, TypeError):
            print(f"⚠️ 模板变量 {{{{{{var_path}}}}}} 未找到")
            return f'"{{{{{{var_path}}}}}}"'  # 保持原样
    
    # 替换所有 {{variable}} 格式的变量
    result = re.sub(r'\{\{([^}]+)\}\}', replace_var, template)
    return result

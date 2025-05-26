import requests
import json
from datetime import datetime

def send_notification(event, result, webhook_url):
    """发送Webhook通知"""
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
        lines.append(f"⏰ 时间: {event['start_time']}")
    
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

def send_test_notification(webhook_url):
    """发送测试通知"""
    test_event = {
        'summary': '测试通知',
        'description': '这是一个测试通知，用于验证Webhook是否正常工作',
        'start_time': datetime.now().isoformat(),
        'uid': 'test-notification'
    }
    
    test_result = {
        'task': '测试Webhook连接',
        'important': True,
        'need_remind': True,
        'minutes_before_remind': 5,
        'reason': '系统测试'
    }
    
    return send_notification(test_event, test_result, webhook_url)

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

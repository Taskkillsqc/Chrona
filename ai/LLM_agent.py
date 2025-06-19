import requests
import json
import time

def analyze_event(summary, description, config, start_time=None, end_time=None, duration_minutes=None, current_time=None):
    """使用AI分析日程事件的重要性和提醒需求"""
    from datetime import datetime
    import pytz
    
    # 获取当前时间
    if current_time is None:
        china_tz = pytz.timezone('Asia/Shanghai')
        current_time = datetime.now(china_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    # 构建时间信息文本
    time_info = ""
    if start_time:
        time_info += f"开始时间: {start_time}\n"
    if end_time:
        time_info += f"结束时间: {end_time}\n"
    if duration_minutes:
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        if hours > 0:
            time_info += f"持续时间: {hours}小时{minutes}分钟 (共{duration_minutes}分钟)\n"
        else:
            time_info += f"持续时间: {minutes}分钟\n"
    
    prompt = f"""
你是一个智能日程助手。请分析如下日程并输出以下字段：
- task: 事件任务（简化后的任务描述）
- important: 是否重要 (true/false)
- need_remind: 是否需要提醒 (true/false)
- minutes_before_remind: 建议提前几分钟提醒（数字）
- reason: 判断理由

分析规则：
1. 会议、面试、重要约会等需要提醒
2. 普通的个人时间、休息时间通常不需要提醒
3. 重要事件建议提前15-30分钟提醒
4. 普通事件提前5-10分钟提醒
5. 考虑事件时长：长时间事件（>=2小时）可能需要更早提醒
6. 考虑当前时间与事件开始时间的距离来调整提醒策略

当前时间: {current_time}
{time_info}
标题: {summary}
描述: {description}

请只输出JSON格式，不要包含其他文字：
"""

    headers = {"Content-Type": "application/json"}

    try:
        if config['model'] == 'gemini':
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={config['api_key']}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if res.status_code == 200:
                response_data = res.json()
                text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return {"error": f"API请求失败: {res.status_code}", "raw": res.text}
                
        elif config['model'] == 'deepseek':
            url = "https://api.deepseek.com/chat/completions"
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}]
            }
            headers["Authorization"] = f"Bearer {config['api_key']}"
            res = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if res.status_code == 200:
                response_data = res.json()
                text = response_data['choices'][0]['message']['content']
            else:
                return {"error": f"API请求失败: {res.status_code}", "raw": res.text}
        else:
            return {"error": "不支持的模型类型"}

        # 尝试解析JSON
        try:
            # 清理可能的markdown标记
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            result = json.loads(text)
            
            # 验证必需字段
            required_fields = ['task', 'important', 'need_remind', 'minutes_before_remind']
            for field in required_fields:
                if field not in result:
                    result[field] = False if field in ['important', 'need_remind'] else 15
                    
            return result
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {e}", "raw": text}
            
    except requests.RequestException as e:
        return {"error": f"网络请求失败: {e}"}
    except Exception as e:
        return {"error": f"未知错误: {e}"}

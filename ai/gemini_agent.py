import requests
import json
import time

def analyze_event(summary, description, config):
    """使用AI分析日程事件的重要性和提醒需求"""
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

请只输出JSON格式，不要包含其他文字：

标题: {summary}
描述: {description}
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

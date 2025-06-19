import requests
import json
import time
from .llm_client import LLMClient

def analyze_event(summary, description, config, start_time=None, end_time=None, duration_minutes=None, current_time=None, calendar_name=None):
    """使用AI分析日程事件的重要性和提醒需求 - V3版本"""
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
    
    # 构建日历信息文本
    calendar_info = ""
    if calendar_name:
        calendar_info = f"日历来源: {calendar_name}\n"

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

基于日历名称的智能判断：
- "工作"、"办公"、"会议"等相关日历：通常为工作事务，重要性较高，建议提醒
- "个人"、"私人"、"生活"等相关日历：根据具体内容判断重要性
- "生日"、"纪念日"等相关日历：重要的个人事件，建议提醒
- "假期"、"休息"、"娱乐"等相关日历：通常不需要紧急提醒
- "健康"、"医疗"、"体检"等相关日历：健康相关事务，重要性高
- "学习"、"课程"、"培训"等相关日历：教育相关，建议提醒
- 如果日历名称包含具体项目名、客户名：通常为重要工作事务

当前时间: {current_time}
{time_info}{calendar_info}
标题: {summary}
描述: {description}

请只输出JSON格式，不要包含其他文字：
"""

    # 使用新的LLM客户端
    llm_client = LLMClient(config)
    
    try:
        # 调用LLM生成回复
        result = llm_client.generate(prompt)
        
        if not result.get('success'):
            return {"error": result.get('error', '未知LLM错误')}
        
        text = result['text']
        
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
            
            parsed_result = json.loads(text)
            
            # 验证必需字段
            required_fields = ['task', 'important', 'need_remind', 'minutes_before_remind']
            for field in required_fields:
                if field not in parsed_result:
                    parsed_result[field] = False if field in ['important', 'need_remind'] else 15
            
            # 添加LLM提供商信息用于调试
            parsed_result['_llm_info'] = llm_client.get_provider_info()
                    
            return parsed_result
            
        except json.JSONDecodeError as e:
            return {"error": f"JSON解析失败: {e}", "raw": text}
            
    except Exception as e:
        return {"error": f"分析失败: {e}"}

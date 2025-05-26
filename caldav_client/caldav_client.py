from caldav import DAVClient
from datetime import datetime, timedelta
import logging

class CalDAVClient:
    """CalDAV 客户端，用于连接和获取日历事件"""
    
    def __init__(self, config):
        """初始化 CalDAV 客户端"""
        self.config = config
        self.client = None
        self.logger = logging.getLogger(__name__)
        
    def connect(self):
        """连接到 CalDAV 服务器"""
        try:
            self.client = DAVClient(
                url=self.config['url'],
                username=self.config['username'],
                password=self.config['password']
            )
            # 测试连接
            principal = self.client.principal()
            calendars = principal.calendars()
            self.logger.info(f"成功连接到 CalDAV 服务器，找到 {len(calendars)} 个日历")
            return True
        except Exception as e:
            self.logger.error(f"连接 CalDAV 服务器失败: {e}")
            return False
    
    def get_upcoming_events(self, hours=24):
        """获取接下来指定小时内的日程事件"""
        if not self.client:
            if not self.connect():
                return []
                
        try:
            principal = self.client.principal()
            calendars = principal.calendars()
            events = []
            
            # 获取从现在开始指定小时的事件，使用本地时间
            import pytz
            from datetime import timezone
            
            # 使用中国时区
            china_tz = pytz.timezone('Asia/Shanghai')
            now_local = datetime.now(china_tz)
            
            # 转换为UTC时间供CalDAV查询使用
            start_time = now_local.astimezone(pytz.UTC).replace(tzinfo=None)
            end_time = start_time + timedelta(hours=hours)
            
            self.logger.info(f"查询时间范围: {start_time} 到 {end_time} (UTC)")
            self.logger.info(f"本地时间: {now_local}")
            
            for calendar in calendars:
                try:
                    results = calendar.date_search(start_time, end_time)
                    for event in results:
                        v = event.vobject_instance.vevent
                        
                        # 获取事件的开始时间
                        if not hasattr(v, 'dtstart'):
                            continue
                            
                        event_start = v.dtstart.value
                        event_summary = str(v.summary.value) if hasattr(v, 'summary') else '无标题'
                        
                        self.logger.info(f"处理事件: {event_summary}")
                        self.logger.info(f"  原始开始时间: {event_start} (类型: {type(event_start)})")
                        
                        # 如果事件开始时间是datetime对象，检查是否已经过去
                        if isinstance(event_start, datetime):
                            # 如果事件有时区信息，转换为中国时区比较
                            if event_start.tzinfo:
                                event_start_china = event_start.astimezone(china_tz)
                                self.logger.info(f"  带时区转换为中国时间: {event_start_china}")
                            else:
                                # 假设无时区信息的时间是UTC时间
                                event_start_utc = event_start.replace(tzinfo=pytz.UTC)
                                event_start_china = event_start_utc.astimezone(china_tz)
                                self.logger.info(f"  假设UTC转换为中国时间: {event_start_china}")
                            
                            # 只包含未来的事件（允许10分钟的缓冲时间）
                            buffer_time = timedelta(minutes=10)
                            judgment_time = now_local - buffer_time
                            is_past = event_start_china <= judgment_time
                            
                            self.logger.info(f"  当前时间: {now_local}")
                            self.logger.info(f"  判断基准时间(缓冲10分钟): {judgment_time}")
                            self.logger.info(f"  是否已过去: {is_past}")
                            
                            if is_past:
                                self.logger.info(f"  ⏭️ 跳过已过去的事件: {event_summary}")
                                continue
                            else:
                                self.logger.info(f"  ✅ 包含未来事件: {event_summary}")
                        
                        events.append({
                            'summary': event_summary,
                            'description': str(v.description.value) if hasattr(v, 'description') else '',
                            'start': str(v.dtstart.value) if hasattr(v, 'dtstart') else '',
                            'uid': str(v.uid.value) if hasattr(v, 'uid') else '',
                        })
                except Exception as e:
                    self.logger.warning(f"获取日历 {calendar} 事件时出错: {e}")
                    continue
                    
            return events
        except Exception as e:
            self.logger.error(f"获取事件失败: {e}")
            return []

def get_upcoming_events(caldav_config, hours=24):
    """向后兼容的函数接口"""
    client = CalDAVClient(caldav_config)
    return client.get_upcoming_events(hours)

from caldav import DAVClient
from datetime import datetime, timedelta
import logging
import warnings
import concurrent.futures
import threading

# 抑制CalDAV兼容性警告
logging.getLogger('root').setLevel(logging.WARNING)
warnings.filterwarnings("ignore", category=UserWarning, module="caldav")

class CalDAVClient:
    """CalDAV 客户端，用于连接和获取日历事件"""
    
    def __init__(self, config, provider_name="默认提供商"):
        """初始化 CalDAV 客户端
        
        Args:
            config: CalDAV 配置字典
            provider_name: 提供商名称，用于日志和事件标识
        """
        self.config = config
        self.provider_name = provider_name
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
            self.logger.info(f"[{self.provider_name}] 成功连接到 CalDAV 服务器，找到 {len(calendars)} 个日历")
            return True
        except Exception as e:
            self.logger.error(f"[{self.provider_name}] 连接 CalDAV 服务器失败: {e}")
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
                    # 获取日历名称，不包含提供商信息
                    calendar_name = "未知日历"
                    try:
                        calendar_name = str(calendar.name) if hasattr(calendar, 'name') and calendar.name else calendar.canonical_url.split('/')[-2] if hasattr(calendar, 'canonical_url') else "未知日历"
                    except:
                        calendar_name = "未知日历"
                    
                    self.logger.info(f"[{self.provider_name}] 正在处理日历: {calendar_name}")
                    
                    results = calendar.date_search(start_time, end_time)
                    for event in results:
                        v = event.vobject_instance.vevent
                        
                        # 获取事件的开始时间
                        if not hasattr(v, 'dtstart'):
                            continue
                            
                        event_start = v.dtstart.value
                        event_summary = str(v.summary.value) if hasattr(v, 'summary') else '无标题'
                        
                        self.logger.info(f"[{self.provider_name}] 处理事件: {event_summary}")
                        self.logger.info(f"[{self.provider_name}]   原始开始时间: {event_start} (类型: {type(event_start)})")
                        
                        # 如果事件开始时间是datetime对象，检查是否已经过去
                        if isinstance(event_start, datetime):
                            # 如果事件有时区信息，转换为中国时区比较
                            if event_start.tzinfo:
                                event_start_china = event_start.astimezone(china_tz)
                                self.logger.info(f"[{self.provider_name}]   带时区转换为中国时间: {event_start_china}")
                            else:
                                # 假设无时区信息的时间是UTC时间
                                event_start_utc = event_start.replace(tzinfo=pytz.UTC)
                                event_start_china = event_start_utc.astimezone(china_tz)
                                self.logger.info(f"[{self.provider_name}]   假设UTC转换为中国时间: {event_start_china}")
                            
                            # 只包含未来的事件（允许10分钟的缓冲时间）
                            buffer_time = timedelta(minutes=10)
                            judgment_time = now_local - buffer_time
                            is_past = event_start_china <= judgment_time
                            
                            self.logger.info(f"[{self.provider_name}]   当前时间: {now_local}")
                            self.logger.info(f"[{self.provider_name}]   判断基准时间(缓冲10分钟): {judgment_time}")
                            self.logger.info(f"[{self.provider_name}]   是否已过去: {is_past}")
                            
                            if is_past:
                                self.logger.info(f"[{self.provider_name}]   ⏭️ 跳过已过去的事件: {event_summary}")
                                continue
                            else:
                                self.logger.info(f"[{self.provider_name}]   ✅ 包含未来事件: {event_summary}")
                        
                        # 获取结束时间和计算时长
                        event_end = None
                        duration_minutes = None
                        
                        if hasattr(v, 'dtend'):
                            event_end = v.dtend.value
                        elif hasattr(v, 'duration'):
                            # 如果有duration属性，计算结束时间
                            duration = v.duration.value
                            if isinstance(event_start, datetime) and hasattr(duration, 'total_seconds'):
                                event_end = event_start + duration
                        
                        # 计算时长（分钟）
                        if event_end and isinstance(event_start, datetime) and isinstance(event_end, datetime):
                            duration_minutes = int((event_end - event_start).total_seconds() / 60)
                        
                        events.append({
                            'summary': event_summary,
                            'description': str(v.description.value) if hasattr(v, 'description') else '',
                            'start': str(v.dtstart.value) if hasattr(v, 'dtstart') else '',
                            'end': str(event_end) if event_end else '',
                            'duration_minutes': duration_minutes,
                            'uid': str(v.uid.value) if hasattr(v, 'uid') else '',
                            'calendar_name': calendar_name,  # 添加日历名称信息
                            'provider': self.provider_name,  # 添加提供商信息
                        })
                except Exception as e:
                    self.logger.warning(f"[{self.provider_name}] 获取日历 {calendar} 事件时出错: {e}")
                    continue
                    
            return events
        except Exception as e:
            self.logger.error(f"[{self.provider_name}] 获取事件失败: {e}")
            return []


class MultiCalDAVClient:
    """多 CalDAV 提供商客户端管理器"""
    
    def __init__(self, caldav_configs):
        """
        初始化多 CalDAV 客户端
        
        Args:
            caldav_configs: CalDAV 配置，支持单个配置或多个配置
                单个配置: {'url': '...', 'username': '...', 'password': '...'}
                多个配置: {
                    'providers': {
                        'icloud': {'url': '...', 'username': '...', 'password': '...'},
                        'google': {'url': '...', 'username': '...', 'password': '...'}
                    }
                }
                或简化的多个配置: [
                    {'name': 'iCloud', 'url': '...', 'username': '...', 'password': '...'},
                    {'name': 'Google', 'url': '...', 'username': '...', 'password': '...'}
                ]
        """
        self.clients = []
        self.logger = logging.getLogger(__name__)
        
        # 检测配置格式并初始化客户端
        if isinstance(caldav_configs, list):
            # 配置是列表格式
            if not caldav_configs:
                raise ValueError("CalDAV 提供商列表不能为空")
            
            for i, config in enumerate(caldav_configs):
                provider_name = config.get('name', f'提供商{i+1}')
                client = CalDAVClient(config, provider_name)
                self.clients.append(client)
        elif isinstance(caldav_configs, dict):
            if 'providers' in caldav_configs:
                # 新的多提供商格式
                providers = caldav_configs['providers']
                if not providers or not isinstance(providers, dict):
                    raise ValueError("providers 配置不能为空且必须是字典")
                
                for name, config in providers.items():
                    client = CalDAVClient(config, name)
                    self.clients.append(client)
            elif 'url' in caldav_configs:
                # 传统的单个提供商格式，向后兼容
                client = CalDAVClient(caldav_configs, "默认CalDAV")
                self.clients.append(client)
            else:
                raise ValueError("无效的 CalDAV 配置格式")
        else:
            raise ValueError("CalDAV 配置必须是字典或列表")
        
        self.logger.info(f"初始化了 {len(self.clients)} 个 CalDAV 客户端")
    
    def get_upcoming_events(self, hours=24):
        """从所有配置的 CalDAV 提供商获取即将到来的事件"""
        all_events = []
        
        def fetch_from_client(client):
            """从单个客户端获取事件"""
            try:
                events = client.get_upcoming_events(hours)
                return events
            except Exception as e:
                self.logger.error(f"从 {client.provider_name} 获取事件失败: {e}")
                return []
        
        # 并发获取所有提供商的事件
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.clients)) as executor:
            # 提交所有任务
            future_to_client = {
                executor.submit(fetch_from_client, client): client 
                for client in self.clients
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_client):
                client = future_to_client[future]
                try:
                    events = future.result(timeout=30)  # 30秒超时
                    all_events.extend(events)
                    self.logger.info(f"从 {client.provider_name} 获取到 {len(events)} 个事件")
                except concurrent.futures.TimeoutError:
                    self.logger.warning(f"从 {client.provider_name} 获取事件超时")
                except Exception as e:
                    self.logger.error(f"从 {client.provider_name} 获取事件时发生异常: {e}")
        
        # 按开始时间排序
        all_events.sort(key=lambda x: x.get('start', ''))
        
        self.logger.info(f"总共获取到 {len(all_events)} 个事件")
        return all_events


def get_upcoming_events(caldav_config, hours=24):
    """向后兼容的函数接口，现在支持多提供商配置"""
    try:
        # 使用新的多提供商客户端
        multi_client = MultiCalDAVClient(caldav_config)
        return multi_client.get_upcoming_events(hours)
    except Exception as e:
        # 如果多提供商初始化失败，尝试传统的单提供商方式
        logging.getLogger(__name__).warning(f"多提供商模式失败，尝试单提供商模式: {e}")
        client = CalDAVClient(caldav_config)
        return client.get_upcoming_events(hours)

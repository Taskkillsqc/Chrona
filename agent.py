import time
import os
import signal
import sys
import logging
import warnings
import pytz
from datetime import datetime, timedelta

# 在导入caldav相关模块之前设置日志抑制
logging.getLogger().setLevel(logging.CRITICAL)
logging.getLogger('caldav').setLevel(logging.CRITICAL)
logging.getLogger('root').setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

# 抑制urllib3的OpenSSL警告
import urllib3
urllib3.disable_warnings()

from caldav_client.client import get_upcoming_events
from ai.analyzer import analyze_event
from memory.database import init_db, save_event_analysis, get_events_to_remind, mark_reminded, get_stats, cleanup_old_events
from services.notifier import send_notification, send_test_notification
from services.heartbeat import HeartbeatSender
from services.api_server import APIServer
from config import CONFIG

# 配置常量
INTERVAL = 600  # 每10分钟运行一次
REMIND_CHECK_INTERVAL = 60  # 每1分钟检查一次是否需要发送提醒
CLEANUP_INTERVAL = 3600  # 每1小时清理一次过期事件

class CalendarAgent:
    def __init__(self):
        # 配置日志级别，抑制不必要的错误信息
        self.configure_logging()
        
        self.running = True
        self.last_fetch_time = None
        self.last_remind_check = None
        self.last_cleanup_time = None  # 新增清理时间跟踪
        
        # 初始化心跳包发送器
        self.heartbeat_sender = HeartbeatSender(CONFIG)
        
        # 初始化API服务器
        self.api_server = APIServer(CONFIG, calendar_agent=self, heartbeat_sender=self.heartbeat_sender)
        
        # 注册信号处理器，用于优雅关闭
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def configure_logging(self):
        """配置日志级别，抑制CalDAV兼容性错误"""
        # 抑制根日志器的ERROR级别消息
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.CRITICAL)
        
        # 特别针对caldav模块
        caldav_logger = logging.getLogger('caldav')
        caldav_logger.setLevel(logging.CRITICAL)
        
        # 抑制所有WARNING级别的消息
        logging.getLogger().handlers = []
        logging.basicConfig(level=logging.CRITICAL)
        
        print("🔇 已抑制CalDAV兼容性错误消息")
    
    def signal_handler(self, signum, frame):
        """处理关闭信号"""
        print(f"\n收到信号 {signum}，正在优雅关闭...")
        self.running = False
        
        # 发送关闭状态的心跳包
        if self.heartbeat_sender:
            self.heartbeat_sender.send_status_update("down", "Schedule Manager is shutting down")
            self.heartbeat_sender.stop()
        
        # 停止API服务器
        if self.api_server:
            self.api_server.stop()
    
    def fetch_and_analyze_events(self):
        """获取并分析日程事件"""
        print(f"🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始获取日程...")
        
        try:
            # 获取接下来24小时的事件
            events = get_upcoming_events(CONFIG['caldav'])
            
            if not events:
                print("📭 暂无即将到来的日程")
                return
            
            print(f"📅 发现 {len(events)} 个即将到来的事件")                # 分析每个事件
            for i, event in enumerate(events, 1):
                calendar_info = f" (来自: {event.get('calendar_name', '未知日历')})" if event.get('calendar_name') else ""
                print(f"  🔍 分析事件 {i}/{len(events)}: {event.get('summary', '无标题')}{calendar_info}")
                print(f"      时间: {event.get('start', '未知')}")
                if event.get('duration_minutes'):
                    print(f"      时长: {event.get('duration_minutes')}分钟")
                
                # 获取当前时间
                china_tz = pytz.timezone('Asia/Shanghai')
                current_time = datetime.now(china_tz).strftime('%Y-%m-%d %H:%M:%S')
                
                # 调用AI分析，传递时间信息
                result = analyze_event(
                    event.get('summary', ''), 
                    event.get('description', ''), 
                    CONFIG,
                    start_time=event.get('start', ''),
                    end_time=event.get('end', ''),
                    duration_minutes=event.get('duration_minutes'),
                    current_time=current_time,
                    calendar_name=event.get('calendar_name', '')
                )
                
                if 'error' in result:
                    print(f"    ❌ AI分析失败: {result['error']}")
                    continue
                
                # 保存分析结果
                if save_event_analysis(event, result):
                    print(f"    ✅ 分析完成 - 重要: {result.get('important', False)}, 需提醒: {result.get('need_remind', False)}")
                else:
                    print(f"    ❌ 保存分析结果失败")
                
                # 短暂延迟，避免API调用过于频繁
                time.sleep(1)
            
            self.last_fetch_time = datetime.now()
            
        except Exception as e:
            print(f"❌ 获取和分析事件时出错: {e}")
    
    def check_and_send_reminders(self):
        """检查并发送提醒"""
        try:
            events_to_remind = get_events_to_remind()
            
            if not events_to_remind:
                return
            
            # 获取当前UTC时间，统一使用UTC进行比较
            current_time_utc = datetime.now(pytz.UTC)
            
            for event in events_to_remind:
                try:
                    # 解析事件开始时间
                    start_time_str = event.get('start_time', '')
                    if not start_time_str:
                        continue
                    
                    # 解析事件开始时间（支持多种格式）
                    start_time_utc = None
                    try:
                        # 首先尝试ISO格式（支持时区）
                        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                        # 转换为UTC时间进行统一比较
                        if start_time.tzinfo:
                            start_time_utc = start_time.astimezone(pytz.UTC)
                        else:
                            # 如果没有时区信息，假设是UTC时间
                            start_time_utc = start_time.replace(tzinfo=pytz.UTC)
                    except ValueError:
                        try:
                            # 如果ISO格式失败，尝试标准格式（假设为UTC）
                            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                            start_time_utc = start_time.replace(tzinfo=pytz.UTC)
                        except ValueError:
                            print(f"⚠️ 无法解析时间格式: {start_time_str}")
                            continue
                    
                    if start_time_utc is None:
                        continue
                    
                    # 计算提醒时间（UTC）
                    remind_minutes = event['result'].get('minutes_before_remind', 15)
                    remind_time_utc = start_time_utc - timedelta(minutes=remind_minutes)
                    
                    # 检查是否到了提醒时间（统一使用UTC比较）
                    if current_time_utc >= remind_time_utc:
                        # 为了日志显示，转换为中国时区
                        china_tz = pytz.timezone('Asia/Shanghai')
                        event_time_china = start_time_utc.astimezone(china_tz)
                        current_time_china = current_time_utc.astimezone(china_tz)
                        
                        print(f"🔔 发送提醒: {event.get('summary', '未知事件')}")
                        print(f"   事件时间: {event_time_china.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
                        print(f"   当前时间: {current_time_china.strftime('%Y-%m-%d %H:%M:%S')} (北京时间)")
                        
                        webhook_type = CONFIG.get('webhook_type', 'generic')
                        if send_notification(event, event['result'], CONFIG['webhook_url'], webhook_type, CONFIG):
                            mark_reminded(event['id'], "sent")
                        else:
                            mark_reminded(event['id'], "failed")
                
                except Exception as e:
                    print(f"❌ 处理提醒事件时出错: {e}")
                    continue
            
            self.last_remind_check = datetime.now()
            
        except Exception as e:
            print(f"❌ 检查提醒时出错: {e}")
    
    def print_stats(self):
        """打印统计信息"""
        stats = get_stats()
        print(f"\n📊 统计信息:")
        print(f"  总事件数: {stats.get('total_events', 0)}")
        print(f"  需提醒事件: {stats.get('remind_events', 0)}")
        print(f"  已提醒事件: {stats.get('reminded_events', 0)}")
    
    def run(self):
        """主运行循环"""
        print("🚀 Chrona v3.0 启动")
        print(f"📊 配置信息:")
        
        # 显示 LLM 配置信息
        from ai.llm_client import LLMClient
        llm_client = LLMClient(CONFIG)
        llm_info = llm_client.get_provider_info()
        
        print(f"  🤖 LLM提供商: {llm_info['provider']}")
        if llm_info['provider'] != 'custom':
            print(f"  🧠 模型: {llm_info.get('model', 'default')}")
        else:
            print(f"  🧠 自定义模型: {llm_info.get('model', 'N/A')}")
            print(f"  🔗 自定义URL: {llm_info.get('url', 'N/A')}")
        
        # 显示参数信息
        params = llm_info.get('parameters', {})
        if params:
            print(f"  ⚙️ 参数: 温度={params.get('temperature', 0.7)}, 最大令牌={params.get('max_tokens', 1000)}")
        
        print(f"  💾 数据库: {CONFIG.get('database', 'unknown')}")
        print(f"  📅 CalDAV URL: {CONFIG.get('caldav', {}).get('url', 'unknown')}")
        print(f"  ⏱️ 获取间隔: {INTERVAL}秒")
        print(f"  🔔 提醒检查间隔: {REMIND_CHECK_INTERVAL}秒")
        print(f"  🗑️ 数据清理间隔: {CLEANUP_INTERVAL}秒")
        
        # 显示功能状态
        print(f"\n🔧 功能状态:")
        
        # 心跳包功能状态
        heartbeat_config = CONFIG.get('heartbeat', {})
        if heartbeat_config.get('enabled', False) and heartbeat_config.get('url'):
            print(f"💗 心跳包: 已启用 (间隔: {heartbeat_config.get('interval', 60)}秒)")
            print(f"   目标: {heartbeat_config.get('url')}")
        else:
            print("💗 心跳包: 未启用")
        
        # API服务状态
        api_config = CONFIG.get('api', {})
        if api_config.get('enabled', False):
            host = api_config.get('host', '0.0.0.0')
            port = api_config.get('port', 8000)
            print(f"🌐 API服务: 已启用")
            print(f"   地址: http://{host}:{port}")
            print(f"   文档: http://{host}:{port}/docs")
        else:
            print("🌐 API服务: 未启用")
        
        print(f"\n🔧 正在启动服务...")
        
        # 初始化数据库
        try:
            init_db(CONFIG['database'])
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            return
        
        # 启动心跳包发送器
        if self.heartbeat_sender.start():
            print("✅ 心跳包服务启动成功")
        
        # 启动API服务器
        if self.api_server.start():
            print("✅ API服务启动成功")
        
        # 发送启动状态的心跳包
        self.heartbeat_sender.send_status_update("up", "Schedule Manager started successfully")
        
        # 等待一下确保服务完全启动
        import time
        time.sleep(1)
        
        # 发送测试通知（可选）
        if CONFIG.get('webhook_url') and CONFIG['webhook_url'] != "https://your.gitify.endpoint/webhook":
            print(f"\n🧪 发送测试通知...")
            webhook_type = CONFIG.get('webhook_type', 'generic')
            if send_test_notification(CONFIG['webhook_url'], webhook_type, CONFIG):
                print("✅ 测试通知发送成功")
            else:
                print("❌ 测试通知发送失败，请检查webhook配置")
        
        print(f"\n⏰ 开始监控日程...")
        
        # 立即执行一次，先清理过期事件，再检查提醒
        print("🗑️ 启动时清理过期数据...")
        cleanup_old_events(days=7)  # 首先清理过期事件
        self.last_cleanup_time = datetime.now()  # 记录清理时间
        
        self.fetch_and_analyze_events()
        self.check_and_send_reminders()
        self.print_stats()
        
        # 主循环
        while self.running:
            try:
                current_time = datetime.now()
                
                # 检查是否需要获取新事件（先清理过期数据）
                if (not self.last_fetch_time or 
                    (current_time - self.last_fetch_time).total_seconds() >= INTERVAL):
                    # 每次获取新事件前先清理过期事件
                    cleanup_old_events(days=7)
                    self.fetch_and_analyze_events()
                
                # 检查是否需要发送提醒
                if (not self.last_remind_check or 
                    (current_time - self.last_remind_check).total_seconds() >= REMIND_CHECK_INTERVAL):
                    self.check_and_send_reminders()
                
                # 定期清理过期事件
                if (not self.last_cleanup_time or 
                    (current_time - self.last_cleanup_time).total_seconds() >= CLEANUP_INTERVAL):
                    print(f"🗑️ [{current_time.strftime('%H:%M:%S')}] 执行数据库清理...")
                    cleanup_old_events(days=7)
                    self.last_cleanup_time = current_time
                
                # 每小时打印一次统计信息
                if current_time.minute == 0 and current_time.second < 30:
                    self.print_stats()
                
                # 短暂休眠
                time.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 主循环出现错误: {e}")
                # 发送错误状态的心跳包
                self.heartbeat_sender.send_status_update("down", f"Error in main loop: {str(e)}")
                time.sleep(60)  # 出错后等待1分钟再继续
        
        # 发送关闭状态的心跳包
        self.heartbeat_sender.send_status_update("down", "Schedule Manager stopped")
        
        # 停止服务
        self.heartbeat_sender.stop()
        self.api_server.stop()
        
        print("\n👋 Chrona 已停止")

def main():
    """入口函数"""
    # 检查配置文件
    if not os.path.exists('config.yaml'):
        print("❌ 配置文件 config.yaml 不存在")
        sys.exit(1)
    
    # 检查必要的配置
    required_fields = ['caldav', 'database', 'webhook_url']
    for field in required_fields:
        if field not in CONFIG or not CONFIG[field]:
            print(f"❌ 配置文件中缺少必要字段: {field}")
            sys.exit(1)
    
    # 检查 LLM 配置（支持新的 V3 格式）
    llm_config = CONFIG.get('llm', {})
    if llm_config:
        # 新格式：检查是否有有效的 LLM 配置
        if llm_config.get('local', {}).get('enabled', False):
            # 本地模型配置
            local_config = llm_config['local']
            if not local_config.get('model_path'):
                print("❌ 本地 LLM 配置缺少 model_path")
                sys.exit(1)
        elif llm_config.get('custom', {}).get('enabled', False):
            # 自定义配置
            custom_config = llm_config['custom']
            if not custom_config.get('url') or not custom_config.get('model'):
                print("❌ 自定义 LLM 配置缺少 url 或 model")
                sys.exit(1)
        else:
            # 预设提供商配置
            if not llm_config.get('api_key'):
                print("❌ LLM 配置缺少 api_key")
                sys.exit(1)
            if llm_config.get('api_key') in ['your-api-key-here', '']:
                print("❌ 请在config.yaml中设置正确的 LLM API密钥")
                sys.exit(1)
    else:
        # 兼容旧格式
        if 'api_key' not in CONFIG or not CONFIG['api_key']:
            print("❌ 配置文件中缺少必要字段: api_key 或 llm 配置")
            sys.exit(1)
        if CONFIG['api_key'] == 'your-api-key-here':
            print("❌ 请在config.yaml中设置正确的API密钥")
            sys.exit(1)
    
    # 启动代理
    agent = CalendarAgent()
    agent.run()

if __name__ == '__main__':
    main()

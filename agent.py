import time
import os
import signal
import sys
from datetime import datetime, timedelta
from caldav_client.caldav_client import get_upcoming_events
from ai.gemini_agent import analyze_event
from memory.database import init_db, save_event_analysis, get_events_to_remind, mark_reminded, get_stats, cleanup_old_events
from notifier.webhook import send_notification, send_test_notification
from config import CONFIG

# 配置常量
INTERVAL = 600  # 每10分钟运行一次
REMIND_CHECK_INTERVAL = 60  # 每1分钟检查一次是否需要发送提醒

class CalendarAgent:
    def __init__(self):
        self.running = True
        self.last_fetch_time = None
        self.last_remind_check = None
        
        # 注册信号处理器，用于优雅关闭
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """处理关闭信号"""
        print(f"\n收到信号 {signum}，正在优雅关闭...")
        self.running = False
    
    def fetch_and_analyze_events(self):
        """获取并分析日程事件"""
        print(f"🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始获取日程...")
        
        try:
            # 获取接下来24小时的事件（而不是1小时）
            events = get_upcoming_events(CONFIG['caldav'])
            
            if not events:
                print("📭 暂无即将到来的日程")
                return
            
            print(f"📅 发现 {len(events)} 个即将到来的事件")
            
            # 分析每个事件
            for i, event in enumerate(events, 1):
                print(f"  🔍 分析事件 {i}/{len(events)}: {event.get('summary', '无标题')}")
                print(f"      时间: {event.get('start', '未知')}")
                
                # 调用AI分析
                result = analyze_event(
                    event.get('summary', ''), 
                    event.get('description', ''), 
                    CONFIG
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
            
            current_time = datetime.now()
            
            for event in events_to_remind:
                try:
                    # 解析事件开始时间
                    start_time_str = event.get('start_time', '')
                    if not start_time_str:
                        continue
                    
                    # 简单的时间解析（可能需要根据实际格式调整）
                    try:
                        if 'T' in start_time_str:
                            start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                        else:
                            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
                    except:
                        print(f"⚠️ 无法解析时间格式: {start_time_str}")
                        continue
                    
                    # 计算提醒时间
                    remind_minutes = event['result'].get('minutes_before_remind', 15)
                    remind_time = start_time - timedelta(minutes=remind_minutes)
                    
                    # 检查是否到了提醒时间
                    if current_time >= remind_time:
                        print(f"🔔 发送提醒: {event.get('summary', '未知事件')}")
                        
                        if send_notification(event, event['result'], CONFIG['webhook_url']):
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
        print("🚀 Dummy Schedule Manager 启动")
        print(f"📊 配置信息:")
        print(f"  模型: {CONFIG.get('model', 'unknown')}")
        print(f"  数据库: {CONFIG.get('database', 'unknown')}")
        print(f"  CalDAV URL: {CONFIG.get('caldav', {}).get('url', 'unknown')}")
        print(f"  获取间隔: {INTERVAL}秒")
        print(f"  提醒检查间隔: {REMIND_CHECK_INTERVAL}秒")
        
        # 初始化数据库
        try:
            init_db(CONFIG['database'])
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            return
        
        # 发送测试通知（可选）
        if CONFIG.get('webhook_url') and CONFIG['webhook_url'] != "https://your.gitify.endpoint/webhook":
            print("\n🧪 发送测试通知...")
            if send_test_notification(CONFIG['webhook_url']):
                print("✅ 测试通知发送成功")
            else:
                print("❌ 测试通知发送失败，请检查webhook配置")
        
        print(f"\n⏰ 开始监控日程...")
        
        # 立即执行一次
        self.fetch_and_analyze_events()
        self.check_and_send_reminders()
        self.print_stats()
        
        # 主循环
        while self.running:
            try:
                current_time = datetime.now()
                
                # 检查是否需要获取新事件
                if (not self.last_fetch_time or 
                    (current_time - self.last_fetch_time).total_seconds() >= INTERVAL):
                    self.fetch_and_analyze_events()
                
                # 检查是否需要发送提醒
                if (not self.last_remind_check or 
                    (current_time - self.last_remind_check).total_seconds() >= REMIND_CHECK_INTERVAL):
                    self.check_and_send_reminders()
                
                # 每小时清理一次旧记录
                if current_time.minute == 0 and current_time.second < 30:
                    cleanup_old_events(days=7)
                
                # 每小时打印一次统计信息
                if current_time.minute == 0 and current_time.second < 30:
                    self.print_stats()
                
                # 短暂休眠
                time.sleep(30)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ 主循环出现错误: {e}")
                time.sleep(60)  # 出错后等待1分钟再继续
        
        print("\n👋 Dummy Schedule Manager 已停止")

def main():
    """入口函数"""
    # 检查配置文件
    if not os.path.exists('config.yaml'):
        print("❌ 配置文件 config.yaml 不存在")
        sys.exit(1)
    
    # 检查必要的配置
    required_fields = ['api_key', 'caldav', 'database', 'webhook_url']
    for field in required_fields:
        if field not in CONFIG or not CONFIG[field]:
            print(f"❌ 配置文件中缺少必要字段: {field}")
            sys.exit(1)
    
    # 检查API密钥
    if CONFIG['api_key'] == 'your-api-key-here':
        print("❌ 请在config.yaml中设置正确的API密钥")
        sys.exit(1)
    
    # 启动代理
    agent = CalendarAgent()
    agent.run()

if __name__ == '__main__':
    main()

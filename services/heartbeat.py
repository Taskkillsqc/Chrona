import requests
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Optional

class HeartbeatSender:
    """心跳包发送器，用于向监控服务发送状态更新"""
    
    def __init__(self, config: Dict):
        self.config = config.get('heartbeat', {})
        self.enabled = self.config.get('enabled', False)
        self.url = self.config.get('url', '')
        self.interval = self.config.get('interval', 60)
        self.timeout = self.config.get('timeout', 10)
        self.params = self.config.get('params', {})
        
        self.running = False
        self.thread = None
        self.last_send_time = None
        self.send_count = 0
        self.error_count = 0
        
        # 配置日志
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """启动心跳包发送"""
        if not self.enabled or not self.url:
            print("💗 心跳包功能未启用或URL未配置")
            return False
        
        if self.running:
            print("💗 心跳包发送器已在运行")
            return True
        
        self.running = True
        self.thread = threading.Thread(target=self._run_heartbeat, daemon=True)
        self.thread.start()
        
        print(f"💗 心跳包发送器已启动，间隔: {self.interval}秒")
        print(f"💗 目标URL: {self.url}")
        return True
    
    def stop(self):
        """停止心跳包发送"""
        if not self.running:
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        
        print("💗 心跳包发送器已停止")
    
    def send_heartbeat(self, status: str = None, msg: str = None, ping: str = None) -> bool:
        """发送单次心跳包"""
        if not self.url:
            return False
        
        try:
            # 构建请求参数
            params = {}
            
            # 使用配置中的默认参数
            if self.params:
                params.update(self.params)
            
            # 使用传入的参数覆盖默认值
            if status is not None:
                params['status'] = status
            if msg is not None:
                params['msg'] = msg
            if ping is not None:
                params['ping'] = ping
            
            # 发送请求
            response = requests.get(
                self.url,
                params=params if params else None,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                self.send_count += 1
                self.last_send_time = datetime.now()
                return True
            else:
                self.error_count += 1
                print(f"💗 心跳包发送失败，状态码: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            print(f"💗 心跳包发送异常: {e}")
            return False
        except Exception as e:
            self.error_count += 1
            print(f"💗 心跳包发送错误: {e}")
            return False
    
    def _run_heartbeat(self):
        """心跳包发送主循环"""
        print(f"💗 开始定期发送心跳包...")
        
        while self.running:
            try:
                # 发送心跳包
                success = self.send_heartbeat()
                
                if success:
                    print(f"💗 [{datetime.now().strftime('%H:%M:%S')}] 心跳包发送成功 (总计: {self.send_count})")
                else:
                    print(f"💗 [{datetime.now().strftime('%H:%M:%S')}] 心跳包发送失败 (错误: {self.error_count})")
                
                # 等待下次发送
                for _ in range(self.interval):
                    if not self.running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                print(f"💗 心跳包发送循环异常: {e}")
                time.sleep(5)  # 出错后短暂等待
    
    def get_status(self) -> Dict:
        """获取心跳包发送状态"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'url': self.url if self.url else None,
            'interval': self.interval,
            'send_count': self.send_count,
            'error_count': self.error_count,
            'last_send_time': self.last_send_time.isoformat() if self.last_send_time else None
        }
    
    def send_status_update(self, status: str, message: str = None):
        """发送状态更新（用于程序状态变化时）"""
        if not self.enabled:
            return
        
        msg = message or f"Schedule Manager status: {status}"
        self.send_heartbeat(status=status, msg=msg)
        print(f"💗 发送状态更新: {status} - {msg}")

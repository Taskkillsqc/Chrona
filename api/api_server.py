from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import threading
import uvicorn
from datetime import datetime

from memory.database import get_stats, get_events_to_remind, get_recent_events
from caldav_client.caldav_client import get_upcoming_events
from ai.LLM_agent import analyze_event

class APIServer:
    """API服务器"""
    
    def __init__(self, config: Dict, calendar_agent=None, heartbeat_sender=None):
        self.config = config.get('api', {})
        self.enabled = self.config.get('enabled', False)
        self.host = self.config.get('host', '0.0.0.0')
        self.port = self.config.get('port', 8000)
        
        self.calendar_agent = calendar_agent
        self.heartbeat_sender = heartbeat_sender
        self.app_config = config
        
        self.app = FastAPI(
            title="Dummy Schedule Manager API",
            description="智能日程管理系统API",
            version="2.0.0"
        )
        
        self.server = None
        self.server_thread = None
        self.running = False
        
        self._setup_routes()
    
    def _setup_routes(self):
        """设置API路由"""
        
        @self.app.get("/")
        async def root():
            """根路径"""
            return {
                "message": "Dummy Schedule Manager API",
                "version": "2.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/health")
        async def health_check():
            """健康检查"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime": "running" if self.running else "stopped"
            }
        
        @self.app.get("/stats")
        async def get_statistics():
            """获取统计信息"""
            try:
                stats = get_stats()
                
                # 添加心跳包状态
                heartbeat_status = None
                if self.heartbeat_sender:
                    heartbeat_status = self.heartbeat_sender.get_status()
                
                return {
                    "database_stats": stats,
                    "heartbeat_status": heartbeat_status,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/events/upcoming")
        async def get_upcoming_events_api():
            """获取即将到来的事件"""
            try:
                events = get_upcoming_events(self.app_config['caldav'])
                return {
                    "events": events,
                    "count": len(events),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/events/recent")
        async def get_recent_events_api(limit: int = 10):
            """获取最近的事件"""
            try:
                events = get_recent_events(limit)
                return {
                    "events": events,
                    "count": len(events),
                    "limit": limit,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/events/reminders")
        async def get_reminder_events():
            """获取需要提醒的事件"""
            try:
                events = get_events_to_remind()
                return {
                    "events": events,
                    "count": len(events),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/heartbeat/send")
        async def send_heartbeat_manual(background_tasks: BackgroundTasks):
            """手动发送心跳包"""
            if not self.heartbeat_sender or not self.heartbeat_sender.enabled:
                raise HTTPException(status_code=400, detail="心跳包功能未启用")
            
            def send_heartbeat():
                success = self.heartbeat_sender.send_heartbeat()
                return success
            
            background_tasks.add_task(send_heartbeat)
            
            return {
                "message": "心跳包发送请求已提交",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/heartbeat/status")
        async def get_heartbeat_status():
            """获取心跳包状态"""
            if not self.heartbeat_sender:
                return {"enabled": False, "message": "心跳包功能未配置"}
            
            return self.heartbeat_sender.get_status()
        
        @self.app.post("/agent/fetch")
        async def trigger_fetch(background_tasks: BackgroundTasks):
            """手动触发事件获取和分析"""
            if not self.calendar_agent:
                raise HTTPException(status_code=400, detail="日程代理未配置")
            
            def fetch_events():
                self.calendar_agent.fetch_and_analyze_events()
            
            background_tasks.add_task(fetch_events)
            
            return {
                "message": "事件获取和分析已触发",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/agent/check-reminders")
        async def trigger_reminder_check(background_tasks: BackgroundTasks):
            """手动触发提醒检查"""
            if not self.calendar_agent:
                raise HTTPException(status_code=400, detail="日程代理未配置")
            
            def check_reminders():
                self.calendar_agent.check_and_send_reminders()
            
            background_tasks.add_task(check_reminders)
            
            return {
                "message": "提醒检查已触发",
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.get("/config")
        async def get_config():
            """获取配置信息（隐藏敏感信息）"""
            safe_config = {
                "model": self.app_config.get('model'),
                "database": self.app_config.get('database'),
                "webhook_type": self.app_config.get('webhook_type'),
                "settings": self.app_config.get('settings', {}),
                "api": {
                    "enabled": self.config.get('enabled', False),
                    "host": self.host,
                    "port": self.port
                },
                "heartbeat": {
                    "enabled": self.app_config.get('heartbeat', {}).get('enabled', False),
                    "interval": self.app_config.get('heartbeat', {}).get('interval', 60)
                }
            }
            return safe_config
    
    def start(self):
        """启动API服务器"""
        if not self.enabled:
            print("🌐 API服务未启用")
            return False
        
        if self.running:
            print("🌐 API服务器已在运行")
            return True
        
        def run_server():
            config = uvicorn.Config(
                self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            self.server = uvicorn.Server(config)
            self.server.run()
        
        self.running = True
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        
        print(f"🌐 API服务器已启动")
        print(f"🌐 地址: http://{self.host}:{self.port}")
        print(f"🌐 文档: http://{self.host}:{self.port}/docs")
        return True
    
    def stop(self):
        """停止API服务器"""
        if not self.running:
            return
        
        self.running = False
        if self.server:
            self.server.should_exit = True
        
        print("🌐 API服务器已停止")

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import threading
import uvicorn
from datetime import datetime, timedelta

from memory.database import get_stats, get_events_to_remind, get_recent_events
from caldav_client.client import get_upcoming_events, create_event, get_available_calendars
from ai.analyzer import analyze_event

class CreateEventRequest(BaseModel):
    """创建事件请求模型"""
    summary: str
    start_time: str  # ISO格式时间字符串，如 "2025-06-25T14:30:00"
    duration_minutes: int
    provider_name: Optional[str] = None  # 提供商名称（可选）
    calendar_name: Optional[str] = None  # 日历名称（可选）
    description: Optional[str] = ""  # 事件描述（可选）

class EventResponse(BaseModel):
    """事件响应模型"""
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    event: Optional[Dict] = None

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
            title="Chrona API",
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
                "message": "Chrona API",
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
        
        @self.app.post("/events/create", response_model=EventResponse)
        async def create_event_api(request: CreateEventRequest):
            """创建新的日程事件"""
            try:
                # 验证输入
                if not request.summary.strip():
                    raise HTTPException(status_code=400, detail="事件标题不能为空")
                
                if request.duration_minutes <= 0:
                    raise HTTPException(status_code=400, detail="持续时间必须大于0")
                
                # 验证时间格式
                try:
                    start_datetime = datetime.fromisoformat(request.start_time.replace('Z', '+00:00'))
                except ValueError:
                    raise HTTPException(status_code=400, detail="时间格式无效，请使用ISO格式，如：2025-06-25T14:30:00")
                
                # 检查时间是否在未来
                if start_datetime <= datetime.now(start_datetime.tzinfo or None):
                    raise HTTPException(status_code=400, detail="事件时间必须在未来")
                
                # 调用创建事件函数
                result = create_event(
                    caldav_config=self.app_config['caldav'],
                    summary=request.summary,
                    start_time=request.start_time,
                    duration_minutes=request.duration_minutes,
                    provider_name=request.provider_name,
                    calendar_name=request.calendar_name,
                    description=request.description
                )
                
                if result["success"]:
                    return EventResponse(
                        success=True,
                        message=result["message"],
                        event=result["event"]
                    )
                else:
                    raise HTTPException(status_code=400, detail=result["error"])
                    
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"创建事件时发生错误: {str(e)}")
        
        @self.app.get("/calendars")
        async def get_calendars_api():
            """获取所有可用的日历列表"""
            try:
                calendars = get_available_calendars(self.app_config['caldav'])
                return {
                    "calendars": calendars,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"获取日历列表失败: {str(e)}")
        
        @self.app.get("/providers")
        async def get_providers_api():
            """获取所有可用的CalDAV提供商"""
            try:
                caldav_config = self.app_config.get('caldav', {})
                providers = []
                
                if isinstance(caldav_config, list):
                    # 列表格式
                    for i, provider in enumerate(caldav_config):
                        provider_name = provider.get('name', f'提供商{i+1}')
                        providers.append({
                            "name": provider_name,
                            "url": provider.get('url', 'unknown')
                        })
                elif isinstance(caldav_config, dict):
                    if 'providers' in caldav_config:
                        # 命名提供商格式
                        for name, config in caldav_config['providers'].items():
                            providers.append({
                                "name": name,
                                "url": config.get('url', 'unknown')
                            })
                    elif caldav_config.get('url'):
                        # 单个提供商格式
                        providers.append({
                            "name": "默认CalDAV",
                            "url": caldav_config.get('url', 'unknown')
                        })
                
                return {
                    "providers": providers,
                    "count": len(providers),
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"获取提供商列表失败: {str(e)}")

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

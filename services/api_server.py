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
        
        self._calendars_cache = None
        self._calendars_cache_time = None
        self._providers_cache = None
        self._providers_cache_time = None
        self._cache_ttl = 30  # 缓存有效期（秒），可根据需要调整
        
        self._upcoming_cache = None
        self._upcoming_cache_time = None
        self._recent_cache = None
        self._recent_cache_time = None
        self._reminders_cache = None
        self._reminders_cache_time = None
        self._stats_cache = None
        self._stats_cache_time = None
        self._heartbeat_status_cache = None
        self._heartbeat_status_cache_time = None
        self._config_cache = None
        self._config_cache_time = None
        
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
            now = datetime.now()
            if self._stats_cache and self._stats_cache_time and (now - self._stats_cache_time).total_seconds() < self._cache_ttl:
                return self._stats_cache
            try:
                stats = get_stats()
                heartbeat_status = None
                if self.heartbeat_sender:
                    heartbeat_status = self.heartbeat_sender.get_status()
                result = {
                    "database_stats": stats,
                    "heartbeat_status": heartbeat_status,
                    "timestamp": now.isoformat()
                }
                self._stats_cache = result
                self._stats_cache_time = now
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/events/upcoming")
        async def get_upcoming_events_api():
            now = datetime.now()
            if self._upcoming_cache and self._upcoming_cache_time and (now - self._upcoming_cache_time).total_seconds() < self._cache_ttl:
                return self._upcoming_cache
            try:
                events = get_upcoming_events(self.app_config['caldav'])
                result = {
                    "events": events,
                    "count": len(events),
                    "timestamp": now.isoformat()
                }
                self._upcoming_cache = result
                self._upcoming_cache_time = now
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/events/recent")
        async def get_recent_events_api(limit: int = 10):
            now = datetime.now()
            if self._recent_cache and self._recent_cache_time and (now - self._recent_cache_time).total_seconds() < self._cache_ttl and self._recent_cache.get("limit") == limit:
                return self._recent_cache
            try:
                events = get_recent_events(limit)
                result = {
                    "events": events,
                    "count": len(events),
                    "limit": limit,
                    "timestamp": now.isoformat()
                }
                self._recent_cache = result
                self._recent_cache_time = now
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/events/reminders")
        async def get_reminder_events():
            now = datetime.now()
            if self._reminders_cache and self._reminders_cache_time and (now - self._reminders_cache_time).total_seconds() < self._cache_ttl:
                return self._reminders_cache
            try:
                events = get_events_to_remind()
                result = {
                    "events": events,
                    "count": len(events),
                    "timestamp": now.isoformat()
                }
                self._reminders_cache = result
                self._reminders_cache_time = now
                return result
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
            now = datetime.now()
            if self._heartbeat_status_cache and self._heartbeat_status_cache_time and (now - self._heartbeat_status_cache_time).total_seconds() < self._cache_ttl:
                return self._heartbeat_status_cache
            if not self.heartbeat_sender:
                return {"enabled": False, "message": "心跳包功能未配置"}
            result = self.heartbeat_sender.get_status()
            self._heartbeat_status_cache = result
            self._heartbeat_status_cache_time = now
            return result

        @self.app.get("/config")
        async def get_config():
            now = datetime.now()
            if self._config_cache and self._config_cache_time and (now - self._config_cache_time).total_seconds() < self._cache_ttl:
                return self._config_cache
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
            self._config_cache = safe_config
            self._config_cache_time = now
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
            """获取所有可用的日历列表（带缓存）"""
            now = datetime.now()
            if self._calendars_cache and self._calendars_cache_time and (now - self._calendars_cache_time).total_seconds() < self._cache_ttl:
                return self._calendars_cache
            try:
                calendars = get_available_calendars(self.app_config['caldav'])
                result = {
                    "calendars": calendars,
                    "timestamp": now.isoformat()
                }
                self._calendars_cache = result
                self._calendars_cache_time = now
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"获取日历列表失败: {str(e)}")

        @self.app.get("/providers")
        async def get_providers_api():
            """获取所有可用的CalDAV提供商（带缓存）"""
            now = datetime.now()
            if self._providers_cache and self._providers_cache_time and (now - self._providers_cache_time).total_seconds() < self._cache_ttl:
                return self._providers_cache
            try:
                caldav_config = self.app_config.get('caldav', {})
                providers = []
                if isinstance(caldav_config, list):
                    for i, provider in enumerate(caldav_config):
                        provider_name = provider.get('name', f'提供商{i+1}')
                        providers.append({
                            "name": provider_name,
                            "url": provider.get('url', 'unknown')
                        })
                elif isinstance(caldav_config, dict):
                    if 'providers' in caldav_config:
                        for name, config in caldav_config['providers'].items():
                            providers.append({
                                "name": name,
                                "url": config.get('url', 'unknown')
                            })
                    elif caldav_config.get('url'):
                        providers.append({
                            "name": "默认CalDAV",
                            "url": caldav_config.get('url', 'unknown')
                        })
                result = {
                    "providers": providers,
                    "count": len(providers),
                    "timestamp": now.isoformat()
                }
                self._providers_cache = result
                self._providers_cache_time = now
                return result
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

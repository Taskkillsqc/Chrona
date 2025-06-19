# CalDAV客户端模块

# 为了保持向后兼容，从新的文件名导入
from .client import CalDAVClient, get_upcoming_events

__all__ = ['CalDAVClient', 'get_upcoming_events']

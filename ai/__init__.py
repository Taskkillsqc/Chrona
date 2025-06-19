# AI分析模块

# 为了保持向后兼容，同时导出新旧模块名
from .analyzer import analyze_event

# 保持旧的导入路径兼容
from .analyzer import *

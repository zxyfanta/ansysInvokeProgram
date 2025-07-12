"""
激光毁伤效能分析软件 - 配置模块

提供系统配置、ANSYS配置和材料数据库管理功能。
"""

__version__ = "1.0.0"
__author__ = "激光毁伤效能分析软件开发团队"

from .settings import get_system_config
from .ansys_config import get_ansys_config, is_ansys_available
from .material_database import MaterialDatabase

__all__ = [
    'get_system_config',
    'get_ansys_config', 
    'is_ansys_available',
    'MaterialDatabase'
]

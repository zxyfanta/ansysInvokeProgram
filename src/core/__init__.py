"""
激光毁伤效能分析软件 - 核心模块

提供基础仿真类、数据模型和异常定义。
"""

from .base_simulator import BaseSimulator
from .data_models import SimulationData, LaserParameters, MaterialData
from .exceptions import (
    LaserDamageError, 
    ANSYSConnectionError, 
    SimulationError,
    DataProcessingError
)

__all__ = [
    'BaseSimulator',
    'SimulationData',
    'LaserParameters', 
    'MaterialData',
    'LaserDamageError',
    'ANSYSConnectionError',
    'SimulationError',
    'DataProcessingError'
]

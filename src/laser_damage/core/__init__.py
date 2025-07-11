"""
核心模块

提供系统的基础类、数据模型和异常定义。
"""

from .base_simulator import BaseSimulator
from .data_models import (
    SimulationResult,
    DamageMetrics, 
    LaserConfiguration,
    MaterialConfiguration,
    EnvironmentConfiguration,
    FlightConfiguration,
    ProcessedData,
    DamageLevel,
    AssessmentReport
)
from .exceptions import (
    SimulationError,
    LicenseError,
    ModelError,
    ConfigurationError,
    DataProcessingError
)

__all__ = [
    "BaseSimulator",
    "SimulationResult",
    "DamageMetrics",
    "LaserConfiguration", 
    "MaterialConfiguration",
    "EnvironmentConfiguration",
    "FlightConfiguration",
    "ProcessedData",
    "DamageLevel",
    "AssessmentReport",
    "SimulationError",
    "LicenseError",
    "ModelError", 
    "ConfigurationError",
    "DataProcessingError",
]

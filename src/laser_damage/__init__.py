"""
激光毁伤仿真系统

基于ANSYS 2021 R1的激光毁伤仿真系统，提供完整的激光武器毁伤效果仿真、
后效分析、数据处理和效果评估功能。

主要模块:
- laser_damage: 激光毁伤仿真模块
- post_damage: 毁伤后效分析模块  
- data_analysis: 数据分析与报告生成模块
- damage_assessment: 毁伤效果评估模块
- gui: 图形用户界面
- utils: 工具函数库
"""

__version__ = "1.0.0"
__author__ = "激光毁伤仿真系统开发团队"
__email__ = "dev-team@company.com"

# 导入核心类
from .core.base_simulator import BaseSimulator
from .core.data_models import SimulationResult, DamageMetrics
from .core.exceptions import SimulationError, LicenseError, ModelError

# 导入主要模块
from .laser_damage.simulator import LaserDamageSimulator
from .post_damage.analyzer import PostDamageAnalyzer
from .data_analysis.reporter import DataAnalysisReporter
from .damage_assessment.assessor import DamageEffectAssessor

__all__ = [
    # 版本信息
    "__version__",
    "__author__", 
    "__email__",
    
    # 核心类
    "BaseSimulator",
    "SimulationResult",
    "DamageMetrics",
    
    # 异常类
    "SimulationError",
    "LicenseError", 
    "ModelError",
    
    # 主要模块
    "LaserDamageSimulator",
    "PostDamageAnalyzer",
    "DataAnalysisReporter",
    "DamageEffectAssessor",
]

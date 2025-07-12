"""
激光毁伤效能分析软件 - 主模块

提供激光毁伤仿真、毁伤后效分析、数据分析和效果评估功能。
"""

__version__ = "1.0.0"
__author__ = "激光毁伤效能分析软件开发团队"
__description__ = "基于ANSYS 2021 R1的激光毁伤效能分析软件"

# 导入核心模块
from .core import BaseSimulator, SimulationData
from .laser_damage import LaserDamageSimulator
from .post_damage import PostDamageAnalyzer
from .data_analysis import DataAnalyzer, ReportGenerator
from .damage_assessment import DamageAssessment

__all__ = [
    'BaseSimulator',
    'SimulationData',
    'LaserDamageSimulator',
    'PostDamageAnalyzer', 
    'DataAnalyzer',
    'ReportGenerator',
    'DamageAssessment'
]

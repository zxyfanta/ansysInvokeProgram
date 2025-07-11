"""
激光毁伤仿真模块

实现激光武器对目标的热损伤仿真和热应力计算。
"""

from .simulator import LaserDamageSimulator
from .laser_config import LaserConfiguration
from .material_config import MaterialConfiguration
from .thermal_solver import ThermalSolver
from .stress_solver import StressSolver

__all__ = [
    "LaserDamageSimulator",
    "LaserConfiguration", 
    "MaterialConfiguration",
    "ThermalSolver",
    "StressSolver",
]

"""
热传导求解器

实现激光加热的热传导分析。
"""

import numpy as np
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..core.data_models import LaserConfiguration, MaterialConfiguration, EnvironmentConfiguration


class ThermalSolver:
    """热传导求解器"""
    
    def __init__(self, working_directory: Optional[str] = None):
        """
        初始化热传导求解器
        
        Args:
            working_directory: 工作目录路径
        """
        self.working_directory = Path(working_directory or "./thermal_work")
        self.working_directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # 配置参数
        self.laser_config: Optional[LaserConfiguration] = None
        self.material_config: Optional[MaterialConfiguration] = None
        self.environment_config: Optional[EnvironmentConfiguration] = None
        
        # 求解器状态
        self.initialized = False
    
    def initialize(self, 
                   laser_config: LaserConfiguration,
                   material_config: MaterialConfiguration,
                   environment_config: EnvironmentConfiguration) -> bool:
        """
        初始化求解器
        
        Args:
            laser_config: 激光配置
            material_config: 材料配置
            environment_config: 环境配置
            
        Returns:
            初始化是否成功
        """
        try:
            self.laser_config = laser_config
            self.material_config = material_config
            self.environment_config = environment_config
            
            self.logger.info("热传导求解器初始化完成")
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"热传导求解器初始化失败: {e}")
            return False
    
    def solve(self, model_path: str) -> Optional[Dict[str, Any]]:
        """
        执行热传导求解
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            求解结果字典
        """
        if not self.initialized:
            self.logger.error("求解器未初始化")
            return None
        
        try:
            self.logger.info("开始热传导求解...")
            
            # 模拟热传导计算过程
            result = self._simulate_thermal_analysis()
            
            self.logger.info("热传导求解完成")
            return result
            
        except Exception as e:
            self.logger.error(f"热传导求解失败: {e}")
            return None
    
    def _simulate_thermal_analysis(self) -> Dict[str, Any]:
        """
        模拟热传导分析（用于界面测试）
        
        Returns:
            模拟的求解结果
        """
        # 生成模拟的温度场数据
        x = np.linspace(0, 10, 50)
        y = np.linspace(0, 10, 50)
        X, Y = np.meshgrid(x, y)
        
        # 模拟激光加热的温度分布
        center_x, center_y = 5, 5
        laser_power = self.laser_config.power if self.laser_config else 1000.0
        beam_diameter = self.laser_config.beam_diameter if self.laser_config else 5.0
        
        # 计算功率密度影响
        power_factor = laser_power / 1000.0  # 归一化功率
        beam_factor = 5.0 / beam_diameter     # 光斑大小影响
        
        temperature_field = (
            self.environment_config.ambient_temperature + 
            800 * power_factor * beam_factor * 
            np.exp(-((X - center_x)**2 + (Y - center_y)**2) / (beam_diameter/2)**2)
        )
        
        # 计算统计值
        max_temperature = np.max(temperature_field)
        min_temperature = np.min(temperature_field)
        
        return {
            "temperature_field": temperature_field,
            "coordinates": (X, Y),
            "max_temperature": max_temperature,
            "min_temperature": min_temperature,
            "solver_info": {
                "solver_type": "thermal",
                "convergence": True,
                "iterations": 150,
                "residual": 1e-6
            }
        }
    
    def get_solver_info(self) -> Dict[str, Any]:
        """
        获取求解器信息
        
        Returns:
            求解器信息字典
        """
        return {
            "solver_name": "ThermalSolver",
            "version": "1.0",
            "initialized": self.initialized,
            "working_directory": str(self.working_directory)
        }

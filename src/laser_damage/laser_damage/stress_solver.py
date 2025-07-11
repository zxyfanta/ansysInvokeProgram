"""
应力求解器

实现热应力分析计算。
"""

import numpy as np
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from ..core.data_models import MaterialConfiguration, EnvironmentConfiguration


class StressSolver:
    """应力求解器"""
    
    def __init__(self, working_directory: Optional[str] = None):
        """
        初始化应力求解器
        
        Args:
            working_directory: 工作目录路径
        """
        self.working_directory = Path(working_directory or "./stress_work")
        self.working_directory.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        
        # 配置参数
        self.material_config: Optional[MaterialConfiguration] = None
        self.environment_config: Optional[EnvironmentConfiguration] = None
        
        # 求解器状态
        self.initialized = False
    
    def initialize(self, 
                   material_config: MaterialConfiguration,
                   environment_config: EnvironmentConfiguration) -> bool:
        """
        初始化求解器
        
        Args:
            material_config: 材料配置
            environment_config: 环境配置
            
        Returns:
            初始化是否成功
        """
        try:
            self.material_config = material_config
            self.environment_config = environment_config
            
            self.logger.info("应力求解器初始化完成")
            self.initialized = True
            return True
            
        except Exception as e:
            self.logger.error(f"应力求解器初始化失败: {e}")
            return False
    
    def solve(self, model_path: str, thermal_result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        执行应力求解
        
        Args:
            model_path: 模型文件路径
            thermal_result: 热分析结果
            
        Returns:
            求解结果字典
        """
        if not self.initialized:
            self.logger.error("求解器未初始化")
            return None
        
        try:
            self.logger.info("开始应力求解...")
            
            # 模拟应力计算过程
            result = self._simulate_stress_analysis(thermal_result)
            
            self.logger.info("应力求解完成")
            return result
            
        except Exception as e:
            self.logger.error(f"应力求解失败: {e}")
            return None
    
    def _simulate_stress_analysis(self, thermal_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟应力分析（用于界面测试）
        
        Args:
            thermal_result: 热分析结果
            
        Returns:
            模拟的求解结果
        """
        # 从热分析结果获取温度场
        temperature_field = thermal_result.get("temperature_field")
        coordinates = thermal_result.get("coordinates")
        
        if temperature_field is None or coordinates is None:
            raise ValueError("无效的热分析结果")
        
        X, Y = coordinates
        
        # 计算热应力
        # 简化的热应力计算：σ = E * α * ΔT / (1 - ν)
        E = getattr(self.material_config, 'youngs_modulus', 70e9)  # 杨氏模量 (Pa)
        alpha = getattr(self.material_config, 'thermal_expansion', 23e-6)  # 热膨胀系数 (1/K)
        nu = getattr(self.material_config, 'poissons_ratio', 0.33)  # 泊松比
        
        T0 = self.environment_config.ambient_temperature
        delta_T = temperature_field - T0
        
        # 热应力计算
        thermal_stress_coeff = E * alpha / (1 - nu)
        stress_field = thermal_stress_coeff * delta_T
        
        # 计算von Mises应力（简化为热应力的等效值）
        von_mises_stress = np.abs(stress_field)
        
        # 计算位移场（简化计算）
        displacement_coeff = alpha
        displacement_field = displacement_coeff * delta_T * 0.001  # 转换为mm
        
        # 计算统计值
        max_stress = np.max(von_mises_stress)
        max_displacement = np.max(np.abs(displacement_field))
        
        return {
            "stress_field": stress_field,
            "von_mises_stress": von_mises_stress,
            "displacement_field": displacement_field,
            "coordinates": coordinates,
            "max_stress": max_stress,
            "max_displacement": max_displacement,
            "solver_info": {
                "solver_type": "structural",
                "convergence": True,
                "iterations": 120,
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
            "solver_name": "StressSolver",
            "version": "1.0",
            "initialized": self.initialized,
            "working_directory": str(self.working_directory)
        }

"""
激光毁伤仿真器

实现激光毁伤仿真的主要逻辑，包括热传导分析和热应力计算。
"""

import os
import numpy as np
from typing import Dict, Any, Optional
from pathlib import Path

from ..core.base_simulator import BaseSimulator
from ..core.data_models import (
    SimulationResult, LaserConfiguration, MaterialConfiguration,
    EnvironmentConfiguration, SimulationStatus
)
from ..core.exceptions import SimulationError, ConfigurationError, AnsysIntegrationError
from ..utils.ansys_utils import AnsysConnector
from .thermal_solver import ThermalSolver
from .stress_solver import StressSolver


class LaserDamageSimulator(BaseSimulator):
    """激光毁伤仿真器"""
    
    def __init__(self, working_directory: Optional[str] = None):
        """
        初始化激光毁伤仿真器
        
        Args:
            working_directory: 工作目录路径
        """
        super().__init__(working_directory)
        
        # 初始化求解器
        self.thermal_solver = ThermalSolver(self.working_directory)
        self.stress_solver = StressSolver(self.working_directory)
        
        # ANSYS连接器
        self.ansys_connector = AnsysConnector()
        
        # 配置对象
        self.laser_config: Optional[LaserConfiguration] = None
        self.material_config: Optional[MaterialConfiguration] = None
        self.environment_config: Optional[EnvironmentConfiguration] = None
        
        # 模型信息
        self.model_loaded = False
        self.model_path: Optional[str] = None
        
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        验证配置参数
        
        Args:
            config: 配置参数字典
            
        Returns:
            验证是否通过
        """
        try:
            # 验证激光参数
            laser_params = config.get("laser_parameters", {})
            if not laser_params:
                raise ConfigurationError("缺少激光参数配置")
            
            self.laser_config = LaserConfiguration(**laser_params)
            self.laser_config.validate()
            
            # 验证材料参数
            material_params = config.get("material_parameters", {})
            if not material_params:
                raise ConfigurationError("缺少材料参数配置")
            
            self.material_config = MaterialConfiguration(**material_params)
            self.material_config.validate()
            
            # 验证环境参数
            env_params = config.get("environment_parameters", {})
            self.environment_config = EnvironmentConfiguration(**env_params)
            
            # 验证模型路径
            model_path = config.get("model_path")
            if not model_path:
                raise ConfigurationError("缺少模型路径")
            
            if not self.load_model(model_path):
                raise ConfigurationError("模型加载失败")
            
            self.logger.info("配置参数验证通过")
            return True
            
        except Exception as e:
            self.logger.error(f"配置验证失败: {e}")
            raise ConfigurationError(f"配置验证失败: {e}")
    
    def prepare_simulation(self) -> bool:
        """
        准备仿真环境
        
        Returns:
            准备是否成功
        """
        try:
            # 检查ANSYS连接
            if not self.ansys_connector.test_connection():
                raise AnsysIntegrationError("ANSYS连接失败")
            
            # 创建工作目录
            self.working_directory.mkdir(parents=True, exist_ok=True)
            
            # 初始化求解器
            self.thermal_solver.initialize(
                self.laser_config,
                self.material_config,
                self.environment_config
            )
            
            self.stress_solver.initialize(
                self.material_config,
                self.environment_config
            )
            
            self.logger.info("仿真环境准备完成")
            return True
            
        except Exception as e:
            self.logger.error(f"仿真环境准备失败: {e}")
            return False
    
    def execute_simulation(self) -> SimulationResult:
        """
        执行仿真计算
        
        Returns:
            仿真结果
        """
        try:
            # 创建结果对象
            result = SimulationResult(
                simulation_id=self.simulation_id,
                timestamp=self.start_time,
                status=SimulationStatus.RUNNING
            )
            
            # 1. 执行热传导分析
            self.logger.info("开始热传导分析...")
            thermal_result = self.thermal_solver.solve(self.model_path)
            
            if thermal_result is None:
                raise SimulationError("热传导分析失败")
            
            # 提取温度场数据
            result.temperature_field = thermal_result.get("temperature_field")
            result.max_temperature = thermal_result.get("max_temperature")
            result.min_temperature = thermal_result.get("min_temperature")
            
            # 2. 执行热应力分析
            self.logger.info("开始热应力分析...")
            stress_result = self.stress_solver.solve(
                self.model_path,
                thermal_result
            )
            
            if stress_result is None:
                raise SimulationError("热应力分析失败")
            
            # 提取应力场数据
            result.stress_field = stress_result.get("stress_field")
            result.max_stress = stress_result.get("max_stress")
            result.von_mises_stress = stress_result.get("von_mises_stress")
            
            # 提取位移场数据
            result.displacement_field = stress_result.get("displacement_field")
            result.max_displacement = stress_result.get("max_displacement")
            
            # 保存结果文件
            result_file = self.working_directory / f"result_{self.simulation_id}.rst"
            result.result_files.append(str(result_file))
            
            # 添加求解器信息
            result.solver_info = {
                "thermal_solver": self.thermal_solver.get_solver_info(),
                "stress_solver": self.stress_solver.get_solver_info(),
                "ansys_version": self.ansys_connector.get_version(),
            }
            
            self.logger.info("仿真计算完成")
            return result
            
        except Exception as e:
            self.logger.error(f"仿真计算失败: {e}")
            raise SimulationError(f"仿真计算失败: {e}")
    
    def post_process_results(self) -> bool:
        """
        后处理仿真结果
        
        Returns:
            后处理是否成功
        """
        try:
            if not self.result:
                return False
            
            # 生成温度分布图
            self._generate_temperature_contour()
            
            # 生成应力分布图
            self._generate_stress_contour()
            
            # 计算毁伤指标
            self._calculate_damage_metrics()
            
            self.logger.info("结果后处理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"结果后处理失败: {e}")
            return False
    
    def _generate_temperature_contour(self) -> None:
        """生成温度分布云图"""
        if self.result and self.result.temperature_field is not None:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 简化的温度分布可视化
            temp_data = self.result.temperature_field
            if temp_data.ndim >= 2:
                im = ax.imshow(temp_data, cmap='hot', interpolation='bilinear')
                ax.set_title('温度分布 (K)')
                plt.colorbar(im, ax=ax, label='温度 (K)')
                
                # 保存图片
                temp_plot_path = self.working_directory / f"temperature_contour_{self.simulation_id}.png"
                plt.savefig(temp_plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                self.output_files.append(str(temp_plot_path))
                self.logger.info(f"温度分布图已保存: {temp_plot_path}")
    
    def _generate_stress_contour(self) -> None:
        """生成应力分布云图"""
        if self.result and self.result.von_mises_stress is not None:
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # 简化的应力分布可视化
            stress_data = self.result.von_mises_stress
            if stress_data.ndim >= 2:
                im = ax.imshow(stress_data, cmap='viridis', interpolation='bilinear')
                ax.set_title('Von Mises应力分布 (Pa)')
                plt.colorbar(im, ax=ax, label='应力 (Pa)')
                
                # 保存图片
                stress_plot_path = self.working_directory / f"stress_contour_{self.simulation_id}.png"
                plt.savefig(stress_plot_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                self.output_files.append(str(stress_plot_path))
                self.logger.info(f"应力分布图已保存: {stress_plot_path}")
    
    def _calculate_damage_metrics(self) -> None:
        """计算毁伤指标"""
        if not self.result:
            return
        
        # 简化的毁伤指标计算
        damage_metrics = {}
        
        # 热损伤面积计算
        if (self.result.temperature_field is not None and 
            self.material_config and 
            self.material_config.melting_point):
            
            melting_temp = self.material_config.melting_point
            temp_field = self.result.temperature_field
            
            # 计算超过熔点的区域
            melting_mask = temp_field > melting_temp
            damage_metrics["thermal_damage_area"] = np.sum(melting_mask)
            damage_metrics["melting_volume"] = np.sum(melting_mask) * 0.1  # 简化计算
        
        # 应力集中系数
        if self.result.max_stress and self.material_config:
            yield_strength = getattr(self.material_config, 'yield_strength', 250e6)  # 默认值
            damage_metrics["stress_concentration"] = self.result.max_stress / yield_strength
        
        # 保存毁伤指标
        metrics_file = self.working_directory / f"damage_metrics_{self.simulation_id}.json"
        import json
        with open(metrics_file, 'w') as f:
            json.dump(damage_metrics, f, indent=2)
        
        self.output_files.append(str(metrics_file))
        self.logger.info(f"毁伤指标已保存: {metrics_file}")
    
    def get_laser_configuration(self) -> Optional[LaserConfiguration]:
        """获取激光配置"""
        return self.laser_config
    
    def get_material_configuration(self) -> Optional[MaterialConfiguration]:
        """获取材料配置"""
        return self.material_config
    
    def get_environment_configuration(self) -> Optional[EnvironmentConfiguration]:
        """获取环境配置"""
        return self.environment_config

"""
激光毁伤仿真器

集成热分析和应力分析的完整激光毁伤仿真功能。
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))
from core.base_simulator import BaseSimulator
from core.data_models import SimulationData, SimulationResults
from core.exceptions import SimulationError

from .thermal_solver import ThermalSolver
from .stress_solver import StressSolver
from .material_models import MaterialModel
from .laser_models import LaserModel

class LaserDamageSimulator(BaseSimulator):
    """激光毁伤仿真器"""
    
    def __init__(self):
        super().__init__("LaserDamageSimulator")
        
        # 子求解器
        self.thermal_solver = ThermalSolver()
        self.stress_solver = StressSolver()
        
        # 模型
        self.material_model: Optional[MaterialModel] = None
        self.laser_model: Optional[LaserModel] = None
        
        # 结果存储
        self.thermal_results: Optional[Dict] = None
        self.stress_results: Optional[Dict] = None
    
    def setup_simulation(self, simulation_data: SimulationData) -> bool:
        """设置仿真参数"""
        try:
            self.log_info("设置激光毁伤仿真参数...")
            
            # 创建材料模型
            self.material_model = MaterialModel(simulation_data.material_data)
            
            # 创建激光模型
            self.laser_model = LaserModel(simulation_data.laser_params)
            
            # 设置热分析求解器
            thermal_setup = self.thermal_solver.setup(
                geometry=simulation_data.geometry_data,
                material=self.material_model,
                laser=self.laser_model,
                boundary_conditions=simulation_data.boundary_conditions,
                settings=simulation_data.simulation_settings
            )
            
            if not thermal_setup:
                raise SimulationError("热分析求解器设置失败")
            
            # 设置应力分析求解器
            stress_setup = self.stress_solver.setup(
                geometry=simulation_data.geometry_data,
                material=self.material_model,
                boundary_conditions=simulation_data.boundary_conditions,
                settings=simulation_data.simulation_settings
            )
            
            if not stress_setup:
                raise SimulationError("应力分析求解器设置失败")
            
            self.log_info("仿真参数设置完成")
            return True
            
        except Exception as e:
            self.log_error(f"仿真设置失败: {e}")
            return False
    
    def run_simulation(self) -> bool:
        """运行仿真"""
        try:
            self.log_info("开始激光毁伤仿真...")
            
            # 第一步：热分析
            self.log_info("执行热分析...")
            self.thermal_results = self.thermal_solver.solve()
            
            if not self.thermal_results:
                raise SimulationError("热分析失败")
            
            self.log_info("热分析完成")
            
            # 第二步：应力分析（使用热分析结果作为载荷）
            self.log_info("执行热应力分析...")
            self.stress_results = self.stress_solver.solve(
                thermal_results=self.thermal_results
            )
            
            if not self.stress_results:
                raise SimulationError("应力分析失败")
            
            self.log_info("应力分析完成")
            
            # 第三步：毁伤评估
            self.log_info("执行毁伤评估...")
            damage_results = self._evaluate_damage()
            
            # 更新仿真数据结果
            if self.current_simulation:
                self.current_simulation.laser_damage_results = SimulationResults(
                    temperature_field=self.thermal_results.get('temperature_field'),
                    stress_field=self.stress_results.get('stress_field'),
                    displacement_field=self.stress_results.get('displacement_field'),
                    damage_region=damage_results.get('damage_region'),
                    max_temperature=self.thermal_results.get('max_temperature', 0.0),
                    max_stress=self.stress_results.get('max_stress', 0.0),
                    damage_volume=damage_results.get('damage_volume', 0.0),
                    damage_depth=damage_results.get('damage_depth', 0.0),
                    computation_time=self.thermal_results.get('computation_time', 0.0) + 
                                   self.stress_results.get('computation_time', 0.0)
                )
            
            self.log_info("激光毁伤仿真完成")
            return True
            
        except Exception as e:
            self.log_error(f"仿真执行失败: {e}")
            return False
    
    def _evaluate_damage(self) -> Dict[str, Any]:
        """评估毁伤效果"""
        try:
            damage_results = {}
            
            if not self.thermal_results or not self.stress_results:
                return damage_results
            
            # 获取材料属性
            if not self.material_model:
                return damage_results
            
            melting_point = self.material_model.melting_point
            yield_strength = self.material_model.yield_strength
            
            # 温度场分析
            temp_field = self.thermal_results.get('temperature_field')
            if temp_field is not None:
                # 计算熔化区域
                melted_region = temp_field > melting_point
                damage_results['melted_volume'] = np.sum(melted_region) * self._get_element_volume()
                
                # 计算热影响区
                heat_affected_region = temp_field > (melting_point * 0.5)
                damage_results['heat_affected_volume'] = np.sum(heat_affected_region) * self._get_element_volume()
            
            # 应力场分析
            stress_field = self.stress_results.get('stress_field')
            if stress_field is not None:
                # 计算塑性变形区域
                plastic_region = stress_field > yield_strength
                damage_results['plastic_volume'] = np.sum(plastic_region) * self._get_element_volume()
            
            # 综合毁伤区域
            if temp_field is not None and stress_field is not None:
                # 综合毁伤判据：温度超过熔点或应力超过屈服强度
                damage_region = (temp_field > melting_point) | (stress_field > yield_strength)
                damage_results['damage_region'] = damage_region
                damage_results['damage_volume'] = np.sum(damage_region) * self._get_element_volume()
                
                # 计算毁伤深度（沿激光入射方向）
                damage_results['damage_depth'] = self._calculate_damage_depth(damage_region)
            
            return damage_results
            
        except Exception as e:
            self.log_error(f"毁伤评估失败: {e}")
            return {}
    
    def _get_element_volume(self) -> float:
        """获取单元体积"""
        # 这里需要根据实际网格信息计算
        # 简化处理，假设均匀网格
        if self.current_simulation and self.current_simulation.geometry_data:
            mesh_size = self.current_simulation.geometry_data.mesh_size
            return mesh_size ** 3
        return 1e-9  # 默认值
    
    def _calculate_damage_depth(self, damage_region: np.ndarray) -> float:
        """计算毁伤深度"""
        try:
            # 简化计算：沿Z轴方向的最大毁伤深度
            if damage_region.ndim == 3:
                # 对于3D数组，计算沿Z轴的投影
                z_projection = np.any(damage_region, axis=(0, 1))
                if np.any(z_projection):
                    depth_indices = np.where(z_projection)[0]
                    max_depth_index = np.max(depth_indices)
                    mesh_size = self._get_element_volume() ** (1/3)  # 立方根得到线性尺寸
                    return max_depth_index * mesh_size
            
            return 0.0
            
        except Exception as e:
            self.log_error(f"毁伤深度计算失败: {e}")
            return 0.0
    
    def get_results(self) -> Dict[str, Any]:
        """获取仿真结果"""
        results = {
            'simulation_type': 'laser_damage',
            'status': self.get_simulation_status().value,
            'thermal_results': self.thermal_results,
            'stress_results': self.stress_results
        }
        
        if self.current_simulation and self.current_simulation.laser_damage_results:
            results['damage_results'] = {
                'max_temperature': self.current_simulation.laser_damage_results.max_temperature,
                'max_stress': self.current_simulation.laser_damage_results.max_stress,
                'damage_volume': self.current_simulation.laser_damage_results.damage_volume,
                'damage_depth': self.current_simulation.laser_damage_results.damage_depth,
                'computation_time': self.current_simulation.laser_damage_results.computation_time
            }
        
        return results
    
    def get_temperature_field(self) -> Optional[np.ndarray]:
        """获取温度场"""
        if self.thermal_results:
            return self.thermal_results.get('temperature_field')
        return None
    
    def get_stress_field(self) -> Optional[np.ndarray]:
        """获取应力场"""
        if self.stress_results:
            return self.stress_results.get('stress_field')
        return None
    
    def get_damage_region(self) -> Optional[np.ndarray]:
        """获取毁伤区域"""
        if self.current_simulation and self.current_simulation.laser_damage_results:
            return self.current_simulation.laser_damage_results.damage_region
        return None
    
    def export_results(self, output_dir: str) -> bool:
        """导出结果文件"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 导出温度场
            if self.thermal_results:
                thermal_file = output_path / "thermal_results.npz"
                np.savez(thermal_file, **self.thermal_results)
            
            # 导出应力场
            if self.stress_results:
                stress_file = output_path / "stress_results.npz"
                np.savez(stress_file, **self.stress_results)
            
            # 导出综合结果
            results_file = output_path / "simulation_results.json"
            self.save_results(str(results_file))
            
            self.log_info(f"结果已导出到: {output_dir}")
            return True
            
        except Exception as e:
            self.log_error(f"结果导出失败: {e}")
            return False

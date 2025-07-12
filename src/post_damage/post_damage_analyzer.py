"""
毁伤后效分析器

集成气动力计算、飞行模拟和轨迹分析的完整毁伤后效分析功能。
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))
from core.base_simulator import BaseSimulator
from core.data_models import SimulationData, PostDamageResults
from core.exceptions import SimulationError

from .aerodynamics import AerodynamicsCalculator
from .flight_simulator import FlightSimulator, FlightState, AircraftParameters
from .trajectory_analysis import TrajectoryAnalyzer

class PostDamageAnalyzer(BaseSimulator):
    """毁伤后效分析器"""
    
    def __init__(self):
        super().__init__("PostDamageAnalyzer")
        
        # 子分析器
        self.aero_calculator = AerodynamicsCalculator()
        self.flight_simulator = FlightSimulator()
        self.trajectory_analyzer = TrajectoryAnalyzer()
        
        # 分析结果存储
        self.aerodynamic_results: Optional[Dict] = None
        self.flight_simulation_results: Optional[Dict] = None
        self.trajectory_analysis_results: Optional[Dict] = None
        
        # 原始（未毁伤）状态的参考数据
        self.reference_aero_coefficients: Optional[Dict] = None
        self.reference_flight_results: Optional[Dict] = None
    
    def setup_simulation(self, simulation_data: SimulationData) -> bool:
        """设置毁伤后效分析参数"""
        try:
            self.log_info("设置毁伤后效分析参数...")
            
            # 设置飞行器参数
            aircraft_params = {
                'mass': 1000.0,  # 从仿真数据中获取，这里使用默认值
                'wing_area': 20.0,
                'wing_span': 10.0,
                'chord': 2.0
            }
            
            # 从几何数据中提取参数
            if simulation_data.geometry_data:
                # 根据几何尺寸估算飞行器参数
                length, width, height = simulation_data.geometry_data.dimensions
                aircraft_params['wing_area'] = width * length * 0.7  # 估算机翼面积
                aircraft_params['wing_span'] = width
                aircraft_params['chord'] = length * 0.2
            
            self.flight_simulator.set_aircraft_parameters(aircraft_params)
            
            # 设置飞行条件
            flight_conditions = {
                'altitude': 10000.0,
                'mach_number': 0.8,
                'angle_of_attack': 5.0,
                'sideslip_angle': 0.0
            }
            
            self.aero_calculator.set_flight_conditions(flight_conditions)
            
            self.log_info("毁伤后效分析参数设置完成")
            return True
            
        except Exception as e:
            self.log_error(f"毁伤后效分析设置失败: {e}")
            return False
    
    def run_simulation(self) -> bool:
        """运行毁伤后效分析"""
        try:
            self.log_info("开始毁伤后效分析...")
            
            # 获取毁伤结果
            damage_results = self._get_damage_results()
            
            # 第一步：气动力分析
            self.log_info("执行气动力分析...")
            aero_success = self._run_aerodynamic_analysis(damage_results)
            
            if not aero_success:
                self.log_warning("气动力分析失败，使用估算值")
                self._estimate_aerodynamic_effects(damage_results)
            
            # 第二步：飞行仿真
            self.log_info("执行飞行仿真...")
            flight_success = self._run_flight_simulation()
            
            if not flight_success:
                raise SimulationError("飞行仿真失败")
            
            # 第三步：轨迹分析
            self.log_info("执行轨迹分析...")
            trajectory_success = self._run_trajectory_analysis()
            
            if not trajectory_success:
                self.log_warning("轨迹分析失败")
            
            # 第四步：综合评估
            self.log_info("执行综合评估...")
            self._perform_comprehensive_assessment()
            
            # 更新仿真数据结果
            if self.current_simulation:
                self.current_simulation.post_damage_results = PostDamageResults(
                    aerodynamic_coefficients=self.aerodynamic_results or {},
                    flight_trajectory=self._extract_trajectory_array(),
                    stability_analysis=self.trajectory_analysis_results.get('stability_analysis', {}) if self.trajectory_analysis_results else {},
                    performance_degradation=self._calculate_performance_degradation()
                )
            
            self.log_info("毁伤后效分析完成")
            return True
            
        except Exception as e:
            self.log_error(f"毁伤后效分析失败: {e}")
            return False
    
    def _get_damage_results(self) -> Optional[Dict]:
        """获取激光毁伤结果"""
        if self.current_simulation and self.current_simulation.laser_damage_results:
            return {
                'damage_region': self.current_simulation.laser_damage_results.damage_region,
                'damage_volume': self.current_simulation.laser_damage_results.damage_volume,
                'max_temperature': self.current_simulation.laser_damage_results.max_temperature,
                'max_stress': self.current_simulation.laser_damage_results.max_stress
            }
        return None
    
    def _run_aerodynamic_analysis(self, damage_results: Optional[Dict]) -> bool:
        """运行气动力分析"""
        try:
            # 设置CFD分析
            geometry_file = "aircraft_model.stl"  # 应该从仿真数据中获取
            damage_regions = damage_results.get('damage_region') if damage_results else None
            
            if not self.aero_calculator.setup_cfd_analysis(geometry_file, damage_regions):
                return False
            
            # 运行CFD计算
            if not self.aero_calculator.run_cfd_analysis():
                return False
            
            # 提取气动力系数
            self.aerodynamic_results = self.aero_calculator.extract_aerodynamic_coefficients()
            
            return True
            
        except Exception as e:
            self.log_error(f"气动力分析执行失败: {e}")
            return False
    
    def _estimate_aerodynamic_effects(self, damage_results: Optional[Dict]):
        """估算气动力影响（当CFD不可用时）"""
        try:
            # 基于毁伤程度估算气动力系数变化
            base_coefficients = {
                'CL': 0.5, 'CD': 0.05, 'CM': 0.0,
                'CY': 0.0, 'Cl': 0.0, 'Cn': 0.0
            }
            
            if damage_results:
                damage_volume = damage_results.get('damage_volume', 0.0)
                total_volume = 0.1  # 假设总体积，应从几何数据获取
                
                damage_ratio = min(damage_volume / total_volume, 1.0) if total_volume > 0 else 0.0
                
                # 根据毁伤比例调整气动力系数
                degradation_factor = 1.0 + damage_ratio * 0.5  # 阻力增加
                improvement_factor = 1.0 - damage_ratio * 0.3   # 升力减少
                
                self.aerodynamic_results = {
                    'CL': base_coefficients['CL'] * improvement_factor,
                    'CD': base_coefficients['CD'] * degradation_factor,
                    'CM': base_coefficients['CM'] * (1.0 + damage_ratio * 0.2),
                    'CY': base_coefficients['CY'],
                    'Cl': base_coefficients['Cl'],
                    'Cn': base_coefficients['Cn']
                }
            else:
                self.aerodynamic_results = base_coefficients.copy()
            
            self.log_info("气动力系数估算完成")
            
        except Exception as e:
            self.log_error(f"气动力估算失败: {e}")
            self.aerodynamic_results = {
                'CL': 0.5, 'CD': 0.05, 'CM': 0.0,
                'CY': 0.0, 'Cl': 0.0, 'Cn': 0.0
            }
    
    def _run_flight_simulation(self) -> bool:
        """运行飞行仿真"""
        try:
            # 设置气动力系数
            if self.aerodynamic_results:
                self.flight_simulator.set_aerodynamic_coefficients(self.aerodynamic_results)
            
            # 设置初始飞行状态
            initial_state = FlightState(
                x=0.0, y=0.0, z=-10000.0,  # 初始位置：10km高度
                u=200.0, v=0.0, w=0.0,     # 初始速度：200m/s
                phi=0.0, theta=0.087, psi=0.0,  # 初始姿态：5度攻角
                p=0.0, q=0.0, r=0.0        # 初始角速度
            )
            
            # 设置环境条件
            environment = {
                'rho': 0.414,  # 10km高度空气密度
                'g': 9.81
            }
            
            self.flight_simulator.set_initial_conditions(initial_state, environment)
            
            # 执行飞行仿真
            simulation_duration = 60.0  # 60秒仿真
            self.flight_simulation_results = self.flight_simulator.simulate_flight(simulation_duration)
            
            return self.flight_simulation_results.get('success', False)
            
        except Exception as e:
            self.log_error(f"飞行仿真执行失败: {e}")
            return False
    
    def _run_trajectory_analysis(self) -> bool:
        """运行轨迹分析"""
        try:
            if not self.flight_simulation_results:
                return False
            
            self.trajectory_analysis_results = self.trajectory_analyzer.analyze_trajectory(
                self.flight_simulation_results
            )
            
            return 'error' not in self.trajectory_analysis_results
            
        except Exception as e:
            self.log_error(f"轨迹分析执行失败: {e}")
            return False
    
    def _perform_comprehensive_assessment(self):
        """执行综合评估"""
        try:
            # 综合评估毁伤后效影响
            assessment = {
                'overall_impact': 0.0,
                'flight_capability': 0.0,
                'mission_effectiveness': 0.0,
                'survivability': 0.0
            }
            
            # 基于各项分析结果计算综合影响
            if self.trajectory_analysis_results:
                stability = self.trajectory_analysis_results.get('stability_analysis', {})
                controllability = self.trajectory_analysis_results.get('controllability_analysis', {})
                
                # 飞行能力评估
                overall_stability = stability.get('overall_stability', 0.0)
                overall_controllability = controllability.get('overall_controllability', 0.0)
                assessment['flight_capability'] = (overall_stability + overall_controllability) / 2.0
                
                # 任务效能评估
                performance = self.trajectory_analysis_results.get('flight_performance', {})
                speed_ratio = performance.get('average_speed', 0.0) / 200.0  # 相对于初始速度
                assessment['mission_effectiveness'] = min(100.0, speed_ratio * 100.0)
                
                # 生存能力评估
                metrics = self.trajectory_analysis_results.get('trajectory_metrics', {})
                if hasattr(metrics, 'flight_time'):
                    flight_time = metrics.flight_time
                    assessment['survivability'] = min(100.0, flight_time / 60.0 * 100.0)  # 相对于预期飞行时间
            
            # 总体影响评估
            assessment['overall_impact'] = np.mean([
                assessment['flight_capability'],
                assessment['mission_effectiveness'],
                assessment['survivability']
            ])
            
            # 存储评估结果
            if not hasattr(self, 'comprehensive_assessment'):
                self.comprehensive_assessment = {}
            self.comprehensive_assessment.update(assessment)
            
            self.log_info(f"综合评估完成，总体影响: {assessment['overall_impact']:.1f}%")
            
        except Exception as e:
            self.log_error(f"综合评估失败: {e}")
    
    def _extract_trajectory_array(self) -> Optional[np.ndarray]:
        """提取轨迹数组"""
        try:
            if self.trajectory_analysis_results and 'trajectory_data' in self.trajectory_analysis_results:
                traj_data = self.trajectory_analysis_results['trajectory_data']
                
                # 提取位置数据
                x_data = traj_data['position']['x']
                y_data = traj_data['position']['y']
                z_data = traj_data['position']['z']
                
                # 组合为轨迹数组
                trajectory = np.column_stack([x_data, y_data, z_data])
                return trajectory
            
            return None
            
        except Exception as e:
            self.log_error(f"轨迹数据提取失败: {e}")
            return None
    
    def _calculate_performance_degradation(self) -> float:
        """计算性能退化程度"""
        try:
            if self.trajectory_analysis_results:
                performance = self.trajectory_analysis_results.get('flight_performance', {})
                
                # 基于多个性能指标计算退化程度
                speed_degradation = max(0, (200.0 - performance.get('average_speed', 200.0)) / 200.0)
                energy_loss = performance.get('energy_loss', 0.0)
                
                # 综合退化程度
                degradation = (speed_degradation * 0.6 + min(energy_loss / 10000.0, 1.0) * 0.4) * 100.0
                
                return min(100.0, degradation)
            
            return 0.0
            
        except Exception as e:
            self.log_error(f"性能退化计算失败: {e}")
            return 0.0
    
    def get_results(self) -> Dict[str, Any]:
        """获取毁伤后效分析结果"""
        results = {
            'simulation_type': 'post_damage_analysis',
            'status': self.get_simulation_status().value,
            'aerodynamic_results': self.aerodynamic_results,
            'flight_simulation_results': self.flight_simulation_results,
            'trajectory_analysis_results': self.trajectory_analysis_results
        }
        
        if hasattr(self, 'comprehensive_assessment'):
            results['comprehensive_assessment'] = self.comprehensive_assessment
        
        if self.current_simulation and self.current_simulation.post_damage_results:
            results['post_damage_summary'] = {
                'performance_degradation': self.current_simulation.post_damage_results.performance_degradation,
                'flight_capability': getattr(self, 'comprehensive_assessment', {}).get('flight_capability', 0.0),
                'mission_effectiveness': getattr(self, 'comprehensive_assessment', {}).get('mission_effectiveness', 0.0)
            }
        
        return results
    
    def compare_with_reference(self, reference_results: Dict) -> Dict[str, Any]:
        """与参考状态比较"""
        try:
            if not self.trajectory_analysis_results:
                return {'error': '无当前分析结果'}
            
            comparison = self.trajectory_analyzer.compare_trajectories(
                reference_results, 
                self.flight_simulation_results or {}
            )
            
            return comparison
            
        except Exception as e:
            self.log_error(f"参考比较失败: {e}")
            return {'error': str(e)}
    
    def generate_analysis_report(self) -> str:
        """生成分析报告"""
        report = []
        report.append("=" * 60)
        report.append("毁伤后效分析报告")
        report.append("=" * 60)
        
        # 气动力分析结果
        if self.aerodynamic_results:
            report.append("\n气动力分析结果:")
            for coeff, value in self.aerodynamic_results.items():
                report.append(f"  {coeff}: {value:.4f}")
        
        # 轨迹分析结果
        if self.trajectory_analysis_results:
            trajectory_report = self.trajectory_analyzer.generate_trajectory_report()
            report.append("\n" + trajectory_report)
        
        # 综合评估
        if hasattr(self, 'comprehensive_assessment'):
            assessment = self.comprehensive_assessment
            report.append("\n综合评估:")
            report.append(f"  飞行能力: {assessment.get('flight_capability', 0):.1f}%")
            report.append(f"  任务效能: {assessment.get('mission_effectiveness', 0):.1f}%")
            report.append(f"  生存能力: {assessment.get('survivability', 0):.1f}%")
            report.append(f"  总体影响: {assessment.get('overall_impact', 0):.1f}%")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def cleanup(self):
        """清理资源"""
        try:
            self.aero_calculator.cleanup()
            super().cleanup()
        except:
            pass

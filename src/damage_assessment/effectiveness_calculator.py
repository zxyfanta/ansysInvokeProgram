"""
激光毁伤效果评估 - 效能计算器

计算激光武器的毁伤效能指标。
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class EffectivenessMetrics:
    """效能指标"""
    damage_efficiency: float        # 毁伤效率 (0-100%)
    energy_utilization: float       # 能量利用率 (0-100%)
    target_vulnerability: float     # 目标易损性 (0-100%)
    weapon_lethality: float         # 武器致命性 (0-100%)
    overall_effectiveness: float    # 总体效能 (0-100%)

class EffectivenessCalculator:
    """效能计算器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 效能计算参数
        self.calculation_params = {
            'energy_threshold': 1000.0,     # 能量阈值 (J)
            'damage_threshold': 0.1,        # 毁伤阈值
            'time_factor': 1.0,             # 时间因子
            'distance_factor': 1.0          # 距离因子
        }
    
    def calculate_effectiveness(self, laser_params: Dict, damage_results: Dict, 
                              target_params: Dict) -> EffectivenessMetrics:
        """计算激光毁伤效能"""
        try:
            # 计算各项效能指标
            damage_efficiency = self._calculate_damage_efficiency(laser_params, damage_results)
            energy_utilization = self._calculate_energy_utilization(laser_params, damage_results)
            target_vulnerability = self._calculate_target_vulnerability(target_params, damage_results)
            weapon_lethality = self._calculate_weapon_lethality(laser_params, damage_results)
            
            # 计算总体效能
            overall_effectiveness = self._calculate_overall_effectiveness(
                damage_efficiency, energy_utilization, target_vulnerability, weapon_lethality
            )
            
            return EffectivenessMetrics(
                damage_efficiency=damage_efficiency,
                energy_utilization=energy_utilization,
                target_vulnerability=target_vulnerability,
                weapon_lethality=weapon_lethality,
                overall_effectiveness=overall_effectiveness
            )
            
        except Exception as e:
            self.logger.error(f"效能计算失败: {e}")
            return EffectivenessMetrics(0, 0, 0, 0, 0)
    
    def _calculate_damage_efficiency(self, laser_params: Dict, damage_results: Dict) -> float:
        """计算毁伤效率"""
        try:
            # 基于毁伤体积和激光功率计算效率
            damage_volume = damage_results.get('damage_volume', 0.0)
            laser_power = laser_params.get('power', 1000.0)
            exposure_time = damage_results.get('computation_time', 1.0)
            
            if laser_power > 0 and exposure_time > 0:
                total_energy = laser_power * exposure_time
                efficiency = (damage_volume * 1e6) / total_energy * 100  # 转换单位
                return min(100.0, efficiency)
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"毁伤效率计算失败: {e}")
            return 0.0
    
    def _calculate_energy_utilization(self, laser_params: Dict, damage_results: Dict) -> float:
        """计算能量利用率"""
        try:
            # 基于吸收率和毁伤效果计算能量利用率
            absorptivity = laser_params.get('absorptivity', 0.15)
            max_temperature = damage_results.get('max_temperature', 0.0)
            
            # 简化计算：基于温度升高和吸收率
            if max_temperature > 300:  # 室温以上
                temp_factor = min(1.0, (max_temperature - 300) / 1000)
                utilization = absorptivity * temp_factor * 100
                return min(100.0, utilization)
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"能量利用率计算失败: {e}")
            return 0.0
    
    def _calculate_target_vulnerability(self, target_params: Dict, damage_results: Dict) -> float:
        """计算目标易损性"""
        try:
            # 基于材料属性和毁伤结果计算易损性
            melting_point = target_params.get('melting_point', 1000.0)
            thermal_conductivity = target_params.get('thermal_conductivity', 100.0)
            max_temperature = damage_results.get('max_temperature', 0.0)
            
            # 温度易损性
            temp_vulnerability = min(100.0, (max_temperature / melting_point) * 100)
            
            # 热导率影响（热导率越低，越易损）
            conductivity_factor = max(0.1, 1.0 - thermal_conductivity / 200.0)
            
            vulnerability = temp_vulnerability * conductivity_factor
            return min(100.0, vulnerability)
            
        except Exception as e:
            self.logger.warning(f"目标易损性计算失败: {e}")
            return 0.0
    
    def _calculate_weapon_lethality(self, laser_params: Dict, damage_results: Dict) -> float:
        """计算武器致命性"""
        try:
            # 基于激光参数和毁伤结果计算致命性
            laser_power = laser_params.get('power', 1000.0)
            beam_diameter = laser_params.get('beam_diameter', 0.01)
            max_stress = damage_results.get('max_stress', 0.0)
            
            # 功率密度
            beam_area = np.pi * (beam_diameter / 2) ** 2
            power_density = laser_power / beam_area if beam_area > 0 else 0
            
            # 基于功率密度和应力的致命性评估
            power_factor = min(1.0, power_density / 1e8)  # 归一化到100MW/m²
            stress_factor = min(1.0, max_stress / 1e9)    # 归一化到1GPa
            
            lethality = (power_factor + stress_factor) / 2 * 100
            return min(100.0, lethality)
            
        except Exception as e:
            self.logger.warning(f"武器致命性计算失败: {e}")
            return 0.0
    
    def _calculate_overall_effectiveness(self, damage_efficiency: float, energy_utilization: float,
                                       target_vulnerability: float, weapon_lethality: float) -> float:
        """计算总体效能"""
        try:
            # 加权平均计算总体效能
            weights = {
                'damage_efficiency': 0.3,
                'energy_utilization': 0.2,
                'target_vulnerability': 0.2,
                'weapon_lethality': 0.3
            }
            
            overall = (
                damage_efficiency * weights['damage_efficiency'] +
                energy_utilization * weights['energy_utilization'] +
                target_vulnerability * weights['target_vulnerability'] +
                weapon_lethality * weights['weapon_lethality']
            )
            
            return min(100.0, overall)
            
        except Exception as e:
            self.logger.warning(f"总体效能计算失败: {e}")
            return 0.0
    
    def compare_effectiveness(self, metrics_list: List[EffectivenessMetrics]) -> Dict[str, Any]:
        """比较多个效能指标"""
        try:
            if not metrics_list:
                return {}
            
            comparison = {
                'count': len(metrics_list),
                'average': {},
                'best': {},
                'worst': {},
                'variance': {}
            }
            
            # 提取各项指标
            damage_efficiencies = [m.damage_efficiency for m in metrics_list]
            energy_utilizations = [m.energy_utilization for m in metrics_list]
            target_vulnerabilities = [m.target_vulnerability for m in metrics_list]
            weapon_lethalities = [m.weapon_lethality for m in metrics_list]
            overall_effectivenesses = [m.overall_effectiveness for m in metrics_list]
            
            # 计算统计指标
            metrics_data = {
                'damage_efficiency': damage_efficiencies,
                'energy_utilization': energy_utilizations,
                'target_vulnerability': target_vulnerabilities,
                'weapon_lethality': weapon_lethalities,
                'overall_effectiveness': overall_effectivenesses
            }
            
            for metric_name, values in metrics_data.items():
                comparison['average'][metric_name] = np.mean(values)
                comparison['best'][metric_name] = np.max(values)
                comparison['worst'][metric_name] = np.min(values)
                comparison['variance'][metric_name] = np.var(values)
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"效能比较失败: {e}")
            return {}
    
    def generate_effectiveness_report(self, metrics: EffectivenessMetrics) -> str:
        """生成效能报告"""
        try:
            report = []
            report.append("=" * 50)
            report.append("激光武器毁伤效能报告")
            report.append("=" * 50)
            
            report.append(f"\n总体效能: {metrics.overall_effectiveness:.1f}%")
            
            report.append(f"\n详细指标:")
            report.append(f"  毁伤效率: {metrics.damage_efficiency:.1f}%")
            report.append(f"  能量利用率: {metrics.energy_utilization:.1f}%")
            report.append(f"  目标易损性: {metrics.target_vulnerability:.1f}%")
            report.append(f"  武器致命性: {metrics.weapon_lethality:.1f}%")
            
            # 效能等级评估
            if metrics.overall_effectiveness >= 80:
                effectiveness_level = "优秀"
            elif metrics.overall_effectiveness >= 60:
                effectiveness_level = "良好"
            elif metrics.overall_effectiveness >= 40:
                effectiveness_level = "一般"
            elif metrics.overall_effectiveness >= 20:
                effectiveness_level = "较差"
            else:
                effectiveness_level = "很差"
            
            report.append(f"\n效能等级: {effectiveness_level}")
            
            # 改进建议
            report.append(f"\n改进建议:")
            if metrics.damage_efficiency < 50:
                report.append("  • 优化激光功率和光束参数以提高毁伤效率")
            if metrics.energy_utilization < 50:
                report.append("  • 改善目标表面处理以提高能量吸收")
            if metrics.weapon_lethality < 50:
                report.append("  • 增加激光功率密度以提高致命性")
            
            report.append("=" * 50)
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"效能报告生成失败: {e}")
            return "效能报告生成失败"

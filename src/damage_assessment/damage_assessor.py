"""
激光毁伤效果评估 - 毁伤评估器

综合评估激光毁伤效果和影响。
"""

import sys
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))
from core.base_simulator import BaseSimulator
from core.data_models import SimulationData
from core.exceptions import SimulationError

class DamageLevel(Enum):
    """毁伤等级"""
    NONE = "无毁伤"
    LIGHT = "轻微毁伤"
    MODERATE = "中等毁伤"
    SEVERE = "严重毁伤"
    CRITICAL = "致命毁伤"

class DamageType(Enum):
    """毁伤类型"""
    THERMAL = "热毁伤"
    MECHANICAL = "机械毁伤"
    STRUCTURAL = "结构毁伤"
    FUNCTIONAL = "功能毁伤"
    COMBINED = "复合毁伤"

@dataclass
class DamageAssessment:
    """毁伤评估结果"""
    overall_damage_level: DamageLevel
    damage_types: List[DamageType]
    damage_score: float  # 0-100分
    affected_area_ratio: float  # 受影响面积比例
    structural_integrity: float  # 结构完整性 (0-100%)
    functional_capability: float  # 功能能力 (0-100%)
    mission_impact: float  # 任务影响 (0-100%)
    recovery_possibility: float  # 恢复可能性 (0-100%)
    assessment_confidence: float  # 评估置信度 (0-100%)

class DamageAssessor(BaseSimulator):
    """毁伤评估器"""
    
    def __init__(self):
        super().__init__("DamageAssessor")
        
        # 评估标准
        self.damage_criteria = self._initialize_damage_criteria()
        
        # 评估结果
        self.assessment_result: Optional[DamageAssessment] = None
        
        # 评估历史
        self.assessment_history: List[DamageAssessment] = []
    
    def _initialize_damage_criteria(self) -> Dict[str, Any]:
        """初始化毁伤评估标准"""
        return {
            'temperature_thresholds': {
                'light': 400.0,      # 轻微毁伤温度阈值 (K)
                'moderate': 600.0,   # 中等毁伤温度阈值 (K)
                'severe': 900.0,     # 严重毁伤温度阈值 (K)
                'critical': 1200.0   # 致命毁伤温度阈值 (K)
            },
            'stress_thresholds': {
                'light': 100e6,      # 轻微毁伤应力阈值 (Pa)
                'moderate': 300e6,   # 中等毁伤应力阈值 (Pa)
                'severe': 500e6,     # 严重毁伤应力阈值 (Pa)
                'critical': 800e6    # 致命毁伤应力阈值 (Pa)
            },
            'damage_area_thresholds': {
                'light': 0.05,       # 轻微毁伤面积比例
                'moderate': 0.15,    # 中等毁伤面积比例
                'severe': 0.35,      # 严重毁伤面积比例
                'critical': 0.60     # 致命毁伤面积比例
            },
            'performance_degradation_thresholds': {
                'light': 0.10,       # 轻微性能下降
                'moderate': 0.30,    # 中等性能下降
                'severe': 0.60,      # 严重性能下降
                'critical': 0.85     # 致命性能下降
            }
        }
    
    def setup_simulation(self, simulation_data: SimulationData) -> bool:
        """设置毁伤评估参数"""
        try:
            self.log_info("设置毁伤评估参数...")
            
            # 这里可以根据仿真数据调整评估标准
            if simulation_data.material_data:
                # 根据材料属性调整阈值
                self._adjust_criteria_for_material(simulation_data.material_data)
            
            self.log_info("毁伤评估参数设置完成")
            return True
            
        except Exception as e:
            self.log_error(f"毁伤评估设置失败: {e}")
            return False
    
    def _adjust_criteria_for_material(self, material_data):
        """根据材料属性调整评估标准"""
        try:
            # 根据材料熔点调整温度阈值
            melting_point = material_data.melting_point
            
            # 调整温度阈值为熔点的百分比
            self.damage_criteria['temperature_thresholds'] = {
                'light': melting_point * 0.4,
                'moderate': melting_point * 0.6,
                'severe': melting_point * 0.8,
                'critical': melting_point * 0.95
            }
            
            # 根据材料强度调整应力阈值
            yield_strength = material_data.yield_strength
            
            self.damage_criteria['stress_thresholds'] = {
                'light': yield_strength * 0.3,
                'moderate': yield_strength * 0.6,
                'severe': yield_strength * 0.9,
                'critical': yield_strength * 1.2
            }
            
            self.log_info("评估标准已根据材料属性调整")
            
        except Exception as e:
            self.log_warning(f"材料属性调整失败: {e}")
    
    def run_simulation(self) -> bool:
        """运行毁伤评估"""
        try:
            self.log_info("开始毁伤评估...")
            
            # 获取仿真结果
            simulation_results = self._get_simulation_results()
            
            if not simulation_results:
                raise SimulationError("无可用的仿真结果")
            
            # 执行综合评估
            assessment = self._perform_comprehensive_assessment(simulation_results)
            
            # 保存评估结果
            self.assessment_result = assessment
            self.assessment_history.append(assessment)
            
            self.log_info("毁伤评估完成")
            return True
            
        except Exception as e:
            self.log_error(f"毁伤评估失败: {e}")
            return False
    
    def _get_simulation_results(self) -> Optional[Dict]:
        """获取仿真结果"""
        if self.current_simulation:
            results = {}
            
            # 激光毁伤结果
            if self.current_simulation.laser_damage_results:
                results['laser_damage'] = {
                    'max_temperature': self.current_simulation.laser_damage_results.max_temperature,
                    'max_stress': self.current_simulation.laser_damage_results.max_stress,
                    'damage_volume': self.current_simulation.laser_damage_results.damage_volume,
                    'damage_region': self.current_simulation.laser_damage_results.damage_region
                }
            
            # 毁伤后效结果
            if self.current_simulation.post_damage_results:
                results['post_damage'] = {
                    'performance_degradation': self.current_simulation.post_damage_results.performance_degradation,
                    'stability_analysis': self.current_simulation.post_damage_results.stability_analysis,
                    'flight_trajectory': self.current_simulation.post_damage_results.flight_trajectory
                }
            
            return results if results else None
        
        return None
    
    def _perform_comprehensive_assessment(self, simulation_results: Dict) -> DamageAssessment:
        """执行综合毁伤评估"""
        try:
            # 初始化评估指标
            damage_scores = []
            damage_types = []
            
            # 1. 热毁伤评估
            thermal_score, thermal_level = self._assess_thermal_damage(simulation_results)
            damage_scores.append(thermal_score)
            if thermal_level != DamageLevel.NONE:
                damage_types.append(DamageType.THERMAL)
            
            # 2. 机械毁伤评估
            mechanical_score, mechanical_level = self._assess_mechanical_damage(simulation_results)
            damage_scores.append(mechanical_score)
            if mechanical_level != DamageLevel.NONE:
                damage_types.append(DamageType.MECHANICAL)
            
            # 3. 结构毁伤评估
            structural_score, structural_level = self._assess_structural_damage(simulation_results)
            damage_scores.append(structural_score)
            if structural_level != DamageLevel.NONE:
                damage_types.append(DamageType.STRUCTURAL)
            
            # 4. 功能毁伤评估
            functional_score, functional_level = self._assess_functional_damage(simulation_results)
            damage_scores.append(functional_score)
            if functional_level != DamageLevel.NONE:
                damage_types.append(DamageType.FUNCTIONAL)
            
            # 综合评估
            overall_score = np.mean(damage_scores)
            overall_level = self._score_to_damage_level(overall_score)
            
            # 计算其他指标
            affected_area_ratio = self._calculate_affected_area_ratio(simulation_results)
            structural_integrity = max(0, 100 - structural_score)
            functional_capability = max(0, 100 - functional_score)
            mission_impact = self._calculate_mission_impact(simulation_results)
            recovery_possibility = self._calculate_recovery_possibility(overall_score, damage_types)
            assessment_confidence = self._calculate_assessment_confidence(simulation_results)
            
            # 创建评估结果
            assessment = DamageAssessment(
                overall_damage_level=overall_level,
                damage_types=damage_types,
                damage_score=overall_score,
                affected_area_ratio=affected_area_ratio,
                structural_integrity=structural_integrity,
                functional_capability=functional_capability,
                mission_impact=mission_impact,
                recovery_possibility=recovery_possibility,
                assessment_confidence=assessment_confidence
            )
            
            return assessment
            
        except Exception as e:
            self.log_error(f"综合评估失败: {e}")
            # 返回默认评估结果
            return DamageAssessment(
                overall_damage_level=DamageLevel.NONE,
                damage_types=[],
                damage_score=0.0,
                affected_area_ratio=0.0,
                structural_integrity=100.0,
                functional_capability=100.0,
                mission_impact=0.0,
                recovery_possibility=100.0,
                assessment_confidence=0.0
            )
    
    def _assess_thermal_damage(self, simulation_results: Dict) -> Tuple[float, DamageLevel]:
        """评估热毁伤"""
        try:
            if 'laser_damage' not in simulation_results:
                return 0.0, DamageLevel.NONE
            
            laser_damage = simulation_results['laser_damage']
            max_temperature = laser_damage.get('max_temperature', 0.0)
            
            thresholds = self.damage_criteria['temperature_thresholds']
            
            if max_temperature >= thresholds['critical']:
                return 90.0, DamageLevel.CRITICAL
            elif max_temperature >= thresholds['severe']:
                return 70.0, DamageLevel.SEVERE
            elif max_temperature >= thresholds['moderate']:
                return 50.0, DamageLevel.MODERATE
            elif max_temperature >= thresholds['light']:
                return 25.0, DamageLevel.LIGHT
            else:
                return 0.0, DamageLevel.NONE
                
        except Exception as e:
            self.log_warning(f"热毁伤评估失败: {e}")
            return 0.0, DamageLevel.NONE
    
    def _assess_mechanical_damage(self, simulation_results: Dict) -> Tuple[float, DamageLevel]:
        """评估机械毁伤"""
        try:
            if 'laser_damage' not in simulation_results:
                return 0.0, DamageLevel.NONE
            
            laser_damage = simulation_results['laser_damage']
            max_stress = laser_damage.get('max_stress', 0.0)
            
            thresholds = self.damage_criteria['stress_thresholds']
            
            if max_stress >= thresholds['critical']:
                return 85.0, DamageLevel.CRITICAL
            elif max_stress >= thresholds['severe']:
                return 65.0, DamageLevel.SEVERE
            elif max_stress >= thresholds['moderate']:
                return 45.0, DamageLevel.MODERATE
            elif max_stress >= thresholds['light']:
                return 20.0, DamageLevel.LIGHT
            else:
                return 0.0, DamageLevel.NONE
                
        except Exception as e:
            self.log_warning(f"机械毁伤评估失败: {e}")
            return 0.0, DamageLevel.NONE
    
    def _assess_structural_damage(self, simulation_results: Dict) -> Tuple[float, DamageLevel]:
        """评估结构毁伤"""
        try:
            # 基于毁伤区域和体积评估结构毁伤
            if 'laser_damage' not in simulation_results:
                return 0.0, DamageLevel.NONE
            
            laser_damage = simulation_results['laser_damage']
            damage_volume = laser_damage.get('damage_volume', 0.0)
            
            # 假设总体积
            total_volume = 0.0002  # 应该从几何数据获取
            damage_ratio = damage_volume / total_volume if total_volume > 0 else 0.0
            
            thresholds = self.damage_criteria['damage_area_thresholds']
            
            if damage_ratio >= thresholds['critical']:
                return 95.0, DamageLevel.CRITICAL
            elif damage_ratio >= thresholds['severe']:
                return 75.0, DamageLevel.SEVERE
            elif damage_ratio >= thresholds['moderate']:
                return 55.0, DamageLevel.MODERATE
            elif damage_ratio >= thresholds['light']:
                return 30.0, DamageLevel.LIGHT
            else:
                return 0.0, DamageLevel.NONE
                
        except Exception as e:
            self.log_warning(f"结构毁伤评估失败: {e}")
            return 0.0, DamageLevel.NONE
    
    def _assess_functional_damage(self, simulation_results: Dict) -> Tuple[float, DamageLevel]:
        """评估功能毁伤"""
        try:
            if 'post_damage' not in simulation_results:
                return 0.0, DamageLevel.NONE
            
            post_damage = simulation_results['post_damage']
            performance_degradation = post_damage.get('performance_degradation', 0.0)
            
            # 将性能退化转换为毁伤评分
            degradation_ratio = performance_degradation / 100.0
            
            thresholds = self.damage_criteria['performance_degradation_thresholds']
            
            if degradation_ratio >= thresholds['critical']:
                return 80.0, DamageLevel.CRITICAL
            elif degradation_ratio >= thresholds['severe']:
                return 60.0, DamageLevel.SEVERE
            elif degradation_ratio >= thresholds['moderate']:
                return 40.0, DamageLevel.MODERATE
            elif degradation_ratio >= thresholds['light']:
                return 15.0, DamageLevel.LIGHT
            else:
                return 0.0, DamageLevel.NONE
                
        except Exception as e:
            self.log_warning(f"功能毁伤评估失败: {e}")
            return 0.0, DamageLevel.NONE
    
    def _score_to_damage_level(self, score: float) -> DamageLevel:
        """将评分转换为毁伤等级"""
        if score >= 80:
            return DamageLevel.CRITICAL
        elif score >= 60:
            return DamageLevel.SEVERE
        elif score >= 35:
            return DamageLevel.MODERATE
        elif score >= 10:
            return DamageLevel.LIGHT
        else:
            return DamageLevel.NONE
    
    def _calculate_affected_area_ratio(self, simulation_results: Dict) -> float:
        """计算受影响面积比例"""
        try:
            if 'laser_damage' in simulation_results:
                laser_damage = simulation_results['laser_damage']
                damage_region = laser_damage.get('damage_region')
                
                if damage_region is not None:
                    total_elements = damage_region.size
                    damaged_elements = np.sum(damage_region)
                    return damaged_elements / total_elements if total_elements > 0 else 0.0
            
            return 0.0
            
        except Exception as e:
            self.log_warning(f"受影响面积计算失败: {e}")
            return 0.0
    
    def _calculate_mission_impact(self, simulation_results: Dict) -> float:
        """计算任务影响"""
        try:
            if 'post_damage' in simulation_results:
                post_damage = simulation_results['post_damage']
                performance_degradation = post_damage.get('performance_degradation', 0.0)
                
                # 任务影响与性能退化正相关
                return min(100.0, performance_degradation * 1.2)
            
            return 0.0
            
        except Exception as e:
            self.log_warning(f"任务影响计算失败: {e}")
            return 0.0
    
    def _calculate_recovery_possibility(self, damage_score: float, damage_types: List[DamageType]) -> float:
        """计算恢复可能性"""
        try:
            # 基础恢复可能性与毁伤程度反相关
            base_recovery = max(0, 100 - damage_score * 1.5)
            
            # 根据毁伤类型调整
            type_penalty = 0
            if DamageType.STRUCTURAL in damage_types:
                type_penalty += 20
            if DamageType.THERMAL in damage_types:
                type_penalty += 15
            if DamageType.MECHANICAL in damage_types:
                type_penalty += 10
            
            recovery_possibility = max(0, base_recovery - type_penalty)
            
            return recovery_possibility
            
        except Exception as e:
            self.log_warning(f"恢复可能性计算失败: {e}")
            return 50.0
    
    def _calculate_assessment_confidence(self, simulation_results: Dict) -> float:
        """计算评估置信度"""
        try:
            confidence_factors = []
            
            # 数据完整性
            if 'laser_damage' in simulation_results:
                confidence_factors.append(40.0)
            if 'post_damage' in simulation_results:
                confidence_factors.append(30.0)
            
            # 数据质量
            if simulation_results:
                confidence_factors.append(30.0)
            
            return sum(confidence_factors)
            
        except Exception as e:
            self.log_warning(f"置信度计算失败: {e}")
            return 50.0
    
    def get_results(self) -> Dict[str, Any]:
        """获取评估结果"""
        results = {
            'simulation_type': 'damage_assessment',
            'status': self.get_simulation_status().value
        }
        
        if self.assessment_result:
            results['assessment'] = {
                'overall_damage_level': self.assessment_result.overall_damage_level.value,
                'damage_types': [dt.value for dt in self.assessment_result.damage_types],
                'damage_score': self.assessment_result.damage_score,
                'affected_area_ratio': self.assessment_result.affected_area_ratio,
                'structural_integrity': self.assessment_result.structural_integrity,
                'functional_capability': self.assessment_result.functional_capability,
                'mission_impact': self.assessment_result.mission_impact,
                'recovery_possibility': self.assessment_result.recovery_possibility,
                'assessment_confidence': self.assessment_result.assessment_confidence
            }
        
        return results
    
    def generate_assessment_report(self) -> str:
        """生成评估报告"""
        if not self.assessment_result:
            return "无评估结果可用"
        
        assessment = self.assessment_result
        
        report = []
        report.append("=" * 60)
        report.append("激光毁伤效果评估报告")
        report.append("=" * 60)
        
        report.append(f"\n总体毁伤等级: {assessment.overall_damage_level.value}")
        report.append(f"毁伤评分: {assessment.damage_score:.1f}/100")
        report.append(f"评估置信度: {assessment.assessment_confidence:.1f}%")
        
        report.append(f"\n毁伤类型:")
        for damage_type in assessment.damage_types:
            report.append(f"  • {damage_type.value}")
        
        report.append(f"\n详细指标:")
        report.append(f"  受影响面积比例: {assessment.affected_area_ratio:.1%}")
        report.append(f"  结构完整性: {assessment.structural_integrity:.1f}%")
        report.append(f"  功能能力: {assessment.functional_capability:.1f}%")
        report.append(f"  任务影响: {assessment.mission_impact:.1f}%")
        report.append(f"  恢复可能性: {assessment.recovery_possibility:.1f}%")
        
        report.append("=" * 60)
        
        return "\n".join(report)

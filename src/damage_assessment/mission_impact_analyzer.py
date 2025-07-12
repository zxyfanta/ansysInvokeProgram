"""
激光毁伤效果评估 - 任务影响分析器

分析激光毁伤对任务执行的影响。
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class MissionType(Enum):
    """任务类型"""
    RECONNAISSANCE = "侦察任务"
    STRIKE = "打击任务"
    TRANSPORT = "运输任务"
    PATROL = "巡逻任务"
    ESCORT = "护航任务"
    TRAINING = "训练任务"

class ImpactLevel(Enum):
    """影响等级"""
    NEGLIGIBLE = "可忽略"
    MINOR = "轻微影响"
    MODERATE = "中等影响"
    MAJOR = "重大影响"
    CRITICAL = "致命影响"

@dataclass
class MissionImpactAssessment:
    """任务影响评估结果"""
    mission_type: MissionType
    impact_level: ImpactLevel
    mission_success_probability: float  # 任务成功概率 (0-100%)
    capability_degradation: Dict[str, float]  # 能力退化
    operational_limitations: List[str]  # 作战限制
    mission_modifications: List[str]  # 任务修改建议
    abort_recommendation: bool  # 是否建议中止任务

class MissionImpactAnalyzer:
    """任务影响分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 任务影响评估标准
        self.impact_criteria = {
            'capability_thresholds': {
                'flight_performance': {
                    'negligible': 5.0,
                    'minor': 15.0,
                    'moderate': 35.0,
                    'major': 60.0,
                    'critical': 85.0
                },
                'structural_integrity': {
                    'negligible': 95.0,
                    'minor': 80.0,
                    'moderate': 60.0,
                    'major': 40.0,
                    'critical': 20.0
                },
                'mission_systems': {
                    'negligible': 95.0,
                    'minor': 80.0,
                    'moderate': 60.0,
                    'major': 40.0,
                    'critical': 20.0
                }
            },
            'mission_criticality': {
                MissionType.STRIKE: 0.9,
                MissionType.RECONNAISSANCE: 0.8,
                MissionType.ESCORT: 0.7,
                MissionType.PATROL: 0.6,
                MissionType.TRANSPORT: 0.5,
                MissionType.TRAINING: 0.3
            }
        }
    
    def analyze_mission_impact(self, mission_type: MissionType, damage_assessment: Dict,
                             post_damage_results: Dict) -> MissionImpactAssessment:
        """分析任务影响"""
        try:
            # 计算能力退化
            capability_degradation = self._calculate_capability_degradation(
                damage_assessment, post_damage_results
            )
            
            # 评估影响等级
            impact_level = self._assess_impact_level(capability_degradation, mission_type)
            
            # 计算任务成功概率
            mission_success_probability = self._calculate_mission_success_probability(
                capability_degradation, mission_type
            )
            
            # 识别作战限制
            operational_limitations = self._identify_operational_limitations(
                capability_degradation, damage_assessment
            )
            
            # 生成任务修改建议
            mission_modifications = self._generate_mission_modifications(
                impact_level, capability_degradation, mission_type
            )
            
            # 评估是否建议中止任务
            abort_recommendation = self._evaluate_abort_recommendation(
                impact_level, mission_success_probability, mission_type
            )
            
            return MissionImpactAssessment(
                mission_type=mission_type,
                impact_level=impact_level,
                mission_success_probability=mission_success_probability,
                capability_degradation=capability_degradation,
                operational_limitations=operational_limitations,
                mission_modifications=mission_modifications,
                abort_recommendation=abort_recommendation
            )
            
        except Exception as e:
            self.logger.error(f"任务影响分析失败: {e}")
            return MissionImpactAssessment(
                mission_type=mission_type,
                impact_level=ImpactLevel.NEGLIGIBLE,
                mission_success_probability=100.0,
                capability_degradation={},
                operational_limitations=[],
                mission_modifications=[],
                abort_recommendation=False
            )
    
    def _calculate_capability_degradation(self, damage_assessment: Dict, 
                                        post_damage_results: Dict) -> Dict[str, float]:
        """计算能力退化"""
        try:
            degradation = {}
            
            # 飞行性能退化
            if 'performance_degradation' in post_damage_results:
                degradation['flight_performance'] = post_damage_results['performance_degradation']
            else:
                degradation['flight_performance'] = 0.0
            
            # 结构完整性
            if 'structural_integrity' in damage_assessment:
                structural_integrity = damage_assessment['structural_integrity']
                degradation['structural_integrity'] = 100.0 - structural_integrity
            else:
                degradation['structural_integrity'] = 0.0
            
            # 功能能力
            if 'functional_capability' in damage_assessment:
                functional_capability = damage_assessment['functional_capability']
                degradation['functional_capability'] = 100.0 - functional_capability
            else:
                degradation['functional_capability'] = 0.0
            
            # 任务系统（基于功能能力估算）
            degradation['mission_systems'] = degradation['functional_capability']
            
            # 机动能力（基于飞行性能）
            degradation['maneuverability'] = degradation['flight_performance']
            
            # 生存能力（综合评估）
            degradation['survivability'] = (
                degradation['structural_integrity'] * 0.4 +
                degradation['flight_performance'] * 0.3 +
                degradation['functional_capability'] * 0.3
            )
            
            return degradation
            
        except Exception as e:
            self.logger.warning(f"能力退化计算失败: {e}")
            return {}
    
    def _assess_impact_level(self, capability_degradation: Dict[str, float], 
                           mission_type: MissionType) -> ImpactLevel:
        """评估影响等级"""
        try:
            # 计算加权影响分数
            weights = {
                'flight_performance': 0.3,
                'structural_integrity': 0.25,
                'functional_capability': 0.25,
                'mission_systems': 0.2
            }
            
            weighted_score = 0.0
            total_weight = 0.0
            
            for capability, degradation in capability_degradation.items():
                if capability in weights:
                    weighted_score += degradation * weights[capability]
                    total_weight += weights[capability]
            
            if total_weight > 0:
                average_degradation = weighted_score / total_weight
            else:
                average_degradation = 0.0
            
            # 根据任务关键性调整
            mission_criticality = self.impact_criteria['mission_criticality'].get(mission_type, 0.5)
            adjusted_score = average_degradation * mission_criticality
            
            # 确定影响等级
            if adjusted_score >= 70:
                return ImpactLevel.CRITICAL
            elif adjusted_score >= 50:
                return ImpactLevel.MAJOR
            elif adjusted_score >= 25:
                return ImpactLevel.MODERATE
            elif adjusted_score >= 10:
                return ImpactLevel.MINOR
            else:
                return ImpactLevel.NEGLIGIBLE
                
        except Exception as e:
            self.logger.warning(f"影响等级评估失败: {e}")
            return ImpactLevel.NEGLIGIBLE
    
    def _calculate_mission_success_probability(self, capability_degradation: Dict[str, float],
                                             mission_type: MissionType) -> float:
        """计算任务成功概率"""
        try:
            # 基础成功概率
            base_probability = 100.0
            
            # 根据能力退化调整概率
            for capability, degradation in capability_degradation.items():
                if capability == 'flight_performance':
                    base_probability -= degradation * 0.4
                elif capability == 'mission_systems':
                    base_probability -= degradation * 0.3
                elif capability == 'structural_integrity':
                    base_probability -= degradation * 0.2
                elif capability == 'survivability':
                    base_probability -= degradation * 0.1
            
            # 根据任务类型调整
            mission_factor = {
                MissionType.STRIKE: 0.8,      # 打击任务对性能要求高
                MissionType.RECONNAISSANCE: 0.9,  # 侦察任务相对容错
                MissionType.ESCORT: 0.85,     # 护航任务需要机动性
                MissionType.PATROL: 0.9,      # 巡逻任务要求中等
                MissionType.TRANSPORT: 0.95,  # 运输任务要求较低
                MissionType.TRAINING: 1.0     # 训练任务可以降低标准
            }.get(mission_type, 0.9)
            
            adjusted_probability = base_probability * mission_factor
            
            return max(0.0, min(100.0, adjusted_probability))
            
        except Exception as e:
            self.logger.warning(f"任务成功概率计算失败: {e}")
            return 50.0
    
    def _identify_operational_limitations(self, capability_degradation: Dict[str, float],
                                        damage_assessment: Dict) -> List[str]:
        """识别作战限制"""
        limitations = []
        
        try:
            # 飞行性能限制
            flight_degradation = capability_degradation.get('flight_performance', 0.0)
            if flight_degradation > 50:
                limitations.append("严重限制机动能力和飞行包线")
            elif flight_degradation > 25:
                limitations.append("限制高机动动作和极限飞行")
            elif flight_degradation > 10:
                limitations.append("轻微限制飞行性能")
            
            # 结构完整性限制
            structural_degradation = capability_degradation.get('structural_integrity', 0.0)
            if structural_degradation > 60:
                limitations.append("严重结构损伤，限制载荷和过载")
            elif structural_degradation > 30:
                limitations.append("结构受损，避免高过载机动")
            
            # 任务系统限制
            systems_degradation = capability_degradation.get('mission_systems', 0.0)
            if systems_degradation > 50:
                limitations.append("任务系统功能严重受限")
            elif systems_degradation > 25:
                limitations.append("部分任务系统功能受影响")
            
            # 生存能力限制
            survivability_degradation = capability_degradation.get('survivability', 0.0)
            if survivability_degradation > 60:
                limitations.append("生存能力严重下降，避免高威胁区域")
            elif survivability_degradation > 30:
                limitations.append("生存能力下降，增加防护措施")
            
        except Exception as e:
            self.logger.warning(f"作战限制识别失败: {e}")
        
        return limitations
    
    def _generate_mission_modifications(self, impact_level: ImpactLevel,
                                      capability_degradation: Dict[str, float],
                                      mission_type: MissionType) -> List[str]:
        """生成任务修改建议"""
        modifications = []
        
        try:
            if impact_level == ImpactLevel.CRITICAL:
                modifications.extend([
                    "立即中止当前任务",
                    "返回基地进行损伤评估",
                    "等待维修后再执行任务"
                ])
            elif impact_level == ImpactLevel.MAJOR:
                modifications.extend([
                    "降低任务难度和复杂性",
                    "缩短任务时间",
                    "增加支援和护航",
                    "避免高风险区域"
                ])
            elif impact_level == ImpactLevel.MODERATE:
                modifications.extend([
                    "调整任务参数和路径",
                    "降低飞行高度和速度",
                    "增加安全裕度"
                ])
            elif impact_level == ImpactLevel.MINOR:
                modifications.extend([
                    "监控系统状态",
                    "准备应急预案"
                ])
            
            # 根据具体能力退化添加建议
            flight_degradation = capability_degradation.get('flight_performance', 0.0)
            if flight_degradation > 30:
                modifications.append("限制机动动作，采用保守飞行模式")
            
            systems_degradation = capability_degradation.get('mission_systems', 0.0)
            if systems_degradation > 30:
                modifications.append("使用备用系统或手动操作模式")
            
        except Exception as e:
            self.logger.warning(f"任务修改建议生成失败: {e}")
        
        return modifications
    
    def _evaluate_abort_recommendation(self, impact_level: ImpactLevel,
                                     mission_success_probability: float,
                                     mission_type: MissionType) -> bool:
        """评估是否建议中止任务"""
        try:
            # 基于影响等级的中止建议
            if impact_level == ImpactLevel.CRITICAL:
                return True
            
            # 基于成功概率的中止建议
            if mission_success_probability < 30:
                return True
            
            # 基于任务类型的特殊考虑
            if mission_type == MissionType.STRIKE and mission_success_probability < 50:
                return True  # 打击任务要求较高成功率
            
            if mission_type == MissionType.TRAINING and impact_level in [ImpactLevel.MAJOR, ImpactLevel.CRITICAL]:
                return True  # 训练任务安全第一
            
            return False
            
        except Exception as e:
            self.logger.warning(f"中止建议评估失败: {e}")
            return False
    
    def generate_mission_impact_report(self, assessment: MissionImpactAssessment) -> str:
        """生成任务影响报告"""
        try:
            report = []
            report.append("=" * 60)
            report.append("任务影响分析报告")
            report.append("=" * 60)
            
            report.append(f"\n任务类型: {assessment.mission_type.value}")
            report.append(f"影响等级: {assessment.impact_level.value}")
            report.append(f"任务成功概率: {assessment.mission_success_probability:.1f}%")
            
            if assessment.abort_recommendation:
                report.append(f"\n⚠️  建议中止任务")
            
            report.append(f"\n能力退化分析:")
            for capability, degradation in assessment.capability_degradation.items():
                report.append(f"  {capability}: {degradation:.1f}%")
            
            if assessment.operational_limitations:
                report.append(f"\n作战限制:")
                for limitation in assessment.operational_limitations:
                    report.append(f"  • {limitation}")
            
            if assessment.mission_modifications:
                report.append(f"\n任务修改建议:")
                for modification in assessment.mission_modifications:
                    report.append(f"  • {modification}")
            
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"任务影响报告生成失败: {e}")
            return "任务影响报告生成失败"

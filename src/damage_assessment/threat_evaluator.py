"""
激光毁伤效果评估 - 威胁评估器

评估激光武器对不同目标的威胁程度。
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class ThreatLevel(Enum):
    """威胁等级"""
    MINIMAL = "极低威胁"
    LOW = "低威胁"
    MODERATE = "中等威胁"
    HIGH = "高威胁"
    CRITICAL = "极高威胁"

@dataclass
class ThreatAssessment:
    """威胁评估结果"""
    threat_level: ThreatLevel
    threat_score: float  # 0-100分
    vulnerability_factors: Dict[str, float]
    protection_effectiveness: float
    countermeasure_requirements: List[str]
    risk_mitigation_strategies: List[str]

class ThreatEvaluator:
    """威胁评估器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 威胁评估标准
        self.threat_criteria = {
            'laser_power_thresholds': {
                'minimal': 100.0,      # 100W
                'low': 1000.0,         # 1kW
                'moderate': 10000.0,   # 10kW
                'high': 50000.0,       # 50kW
                'critical': 100000.0   # 100kW
            },
            'damage_thresholds': {
                'minimal': 10.0,       # 10%毁伤
                'low': 25.0,           # 25%毁伤
                'moderate': 50.0,      # 50%毁伤
                'high': 75.0,          # 75%毁伤
                'critical': 90.0       # 90%毁伤
            },
            'distance_factors': {
                'close': 1.0,          # <1km
                'medium': 0.7,         # 1-5km
                'long': 0.4,           # 5-20km
                'extreme': 0.1         # >20km
            }
        }
    
    def evaluate_threat(self, laser_params: Dict, target_params: Dict, 
                       damage_results: Dict, scenario_params: Dict) -> ThreatAssessment:
        """评估激光威胁"""
        try:
            # 计算威胁评分
            threat_score = self._calculate_threat_score(
                laser_params, target_params, damage_results, scenario_params
            )
            
            # 确定威胁等级
            threat_level = self._score_to_threat_level(threat_score)
            
            # 分析易损性因子
            vulnerability_factors = self._analyze_vulnerability_factors(
                target_params, damage_results
            )
            
            # 评估防护效果
            protection_effectiveness = self._evaluate_protection_effectiveness(
                target_params, laser_params
            )
            
            # 生成对抗措施建议
            countermeasure_requirements = self._generate_countermeasure_requirements(
                threat_level, laser_params
            )
            
            # 生成风险缓解策略
            risk_mitigation_strategies = self._generate_risk_mitigation_strategies(
                threat_level, vulnerability_factors
            )
            
            return ThreatAssessment(
                threat_level=threat_level,
                threat_score=threat_score,
                vulnerability_factors=vulnerability_factors,
                protection_effectiveness=protection_effectiveness,
                countermeasure_requirements=countermeasure_requirements,
                risk_mitigation_strategies=risk_mitigation_strategies
            )
            
        except Exception as e:
            self.logger.error(f"威胁评估失败: {e}")
            return ThreatAssessment(
                threat_level=ThreatLevel.MINIMAL,
                threat_score=0.0,
                vulnerability_factors={},
                protection_effectiveness=100.0,
                countermeasure_requirements=[],
                risk_mitigation_strategies=[]
            )
    
    def _calculate_threat_score(self, laser_params: Dict, target_params: Dict,
                               damage_results: Dict, scenario_params: Dict) -> float:
        """计算威胁评分"""
        try:
            score_components = []
            
            # 1. 激光功率威胁评分
            laser_power = laser_params.get('power', 1000.0)
            power_score = self._evaluate_power_threat(laser_power)
            score_components.append(power_score * 0.3)
            
            # 2. 毁伤效果威胁评分
            damage_score = damage_results.get('damage_score', 0.0)
            damage_threat_score = min(100.0, damage_score * 1.2)
            score_components.append(damage_threat_score * 0.4)
            
            # 3. 目标易损性评分
            vulnerability_score = self._evaluate_target_vulnerability(target_params)
            score_components.append(vulnerability_score * 0.2)
            
            # 4. 场景因子评分
            scenario_score = self._evaluate_scenario_factors(scenario_params)
            score_components.append(scenario_score * 0.1)
            
            total_score = sum(score_components)
            return min(100.0, total_score)
            
        except Exception as e:
            self.logger.warning(f"威胁评分计算失败: {e}")
            return 0.0
    
    def _evaluate_power_threat(self, laser_power: float) -> float:
        """评估激光功率威胁"""
        thresholds = self.threat_criteria['laser_power_thresholds']
        
        if laser_power >= thresholds['critical']:
            return 95.0
        elif laser_power >= thresholds['high']:
            return 80.0
        elif laser_power >= thresholds['moderate']:
            return 60.0
        elif laser_power >= thresholds['low']:
            return 35.0
        elif laser_power >= thresholds['minimal']:
            return 15.0
        else:
            return 5.0
    
    def _evaluate_target_vulnerability(self, target_params: Dict) -> float:
        """评估目标易损性"""
        try:
            vulnerability_score = 50.0  # 基础分数
            
            # 材料因子
            melting_point = target_params.get('melting_point', 1000.0)
            if melting_point < 500:
                vulnerability_score += 30
            elif melting_point < 1000:
                vulnerability_score += 15
            elif melting_point > 2000:
                vulnerability_score -= 20
            
            # 热导率因子
            thermal_conductivity = target_params.get('thermal_conductivity', 100.0)
            if thermal_conductivity < 50:
                vulnerability_score += 20
            elif thermal_conductivity > 200:
                vulnerability_score -= 15
            
            # 厚度因子
            thickness = target_params.get('thickness', 0.02)
            if thickness < 0.01:
                vulnerability_score += 25
            elif thickness > 0.05:
                vulnerability_score -= 20
            
            return max(0.0, min(100.0, vulnerability_score))
            
        except Exception as e:
            self.logger.warning(f"目标易损性评估失败: {e}")
            return 50.0
    
    def _evaluate_scenario_factors(self, scenario_params: Dict) -> float:
        """评估场景因子"""
        try:
            scenario_score = 50.0
            
            # 距离因子
            distance = scenario_params.get('engagement_distance', 5000.0)  # 默认5km
            if distance < 1000:
                scenario_score += 30
            elif distance < 5000:
                scenario_score += 10
            elif distance > 20000:
                scenario_score -= 30
            
            # 大气条件因子
            atmospheric_transmission = scenario_params.get('atmospheric_transmission', 0.8)
            transmission_factor = (atmospheric_transmission - 0.5) * 40
            scenario_score += transmission_factor
            
            # 目标运动因子
            target_speed = scenario_params.get('target_speed', 0.0)  # m/s
            if target_speed > 100:
                scenario_score -= 20
            elif target_speed > 50:
                scenario_score -= 10
            
            return max(0.0, min(100.0, scenario_score))
            
        except Exception as e:
            self.logger.warning(f"场景因子评估失败: {e}")
            return 50.0
    
    def _score_to_threat_level(self, score: float) -> ThreatLevel:
        """将评分转换为威胁等级"""
        if score >= 80:
            return ThreatLevel.CRITICAL
        elif score >= 60:
            return ThreatLevel.HIGH
        elif score >= 40:
            return ThreatLevel.MODERATE
        elif score >= 20:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.MINIMAL
    
    def _analyze_vulnerability_factors(self, target_params: Dict, damage_results: Dict) -> Dict[str, float]:
        """分析易损性因子"""
        try:
            factors = {}
            
            # 材料易损性
            melting_point = target_params.get('melting_point', 1000.0)
            factors['material_vulnerability'] = max(0, 100 - melting_point / 20)
            
            # 结构易损性
            thickness = target_params.get('thickness', 0.02)
            factors['structural_vulnerability'] = max(0, 100 - thickness * 2000)
            
            # 热学易损性
            thermal_conductivity = target_params.get('thermal_conductivity', 100.0)
            factors['thermal_vulnerability'] = max(0, 100 - thermal_conductivity / 2)
            
            # 实际毁伤易损性
            damage_score = damage_results.get('damage_score', 0.0)
            factors['actual_vulnerability'] = damage_score
            
            return factors
            
        except Exception as e:
            self.logger.warning(f"易损性因子分析失败: {e}")
            return {}
    
    def _evaluate_protection_effectiveness(self, target_params: Dict, laser_params: Dict) -> float:
        """评估防护效果"""
        try:
            protection_score = 0.0
            
            # 材料防护
            melting_point = target_params.get('melting_point', 1000.0)
            if melting_point > 1500:
                protection_score += 30
            
            # 厚度防护
            thickness = target_params.get('thickness', 0.02)
            if thickness > 0.05:
                protection_score += 25
            
            # 热导率防护
            thermal_conductivity = target_params.get('thermal_conductivity', 100.0)
            if thermal_conductivity > 200:
                protection_score += 20
            
            # 反射率防护
            reflectivity = target_params.get('reflectivity', 0.1)
            protection_score += reflectivity * 25
            
            return min(100.0, protection_score)
            
        except Exception as e:
            self.logger.warning(f"防护效果评估失败: {e}")
            return 0.0
    
    def _generate_countermeasure_requirements(self, threat_level: ThreatLevel, laser_params: Dict) -> List[str]:
        """生成对抗措施需求"""
        requirements = []
        
        if threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            requirements.extend([
                "部署高功率激光干扰系统",
                "安装反射式装甲防护",
                "配置烟雾/气溶胶对抗系统"
            ])
        
        if threat_level in [ThreatLevel.MODERATE, ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            requirements.extend([
                "增强目标机动能力",
                "部署红外诱饵系统",
                "实施电子对抗措施"
            ])
        
        if threat_level != ThreatLevel.MINIMAL:
            requirements.extend([
                "提高态势感知能力",
                "优化飞行路径规划"
            ])
        
        return requirements
    
    def _generate_risk_mitigation_strategies(self, threat_level: ThreatLevel, 
                                           vulnerability_factors: Dict[str, float]) -> List[str]:
        """生成风险缓解策略"""
        strategies = []
        
        # 基于威胁等级的策略
        if threat_level == ThreatLevel.CRITICAL:
            strategies.extend([
                "立即实施最高级别防护措施",
                "避免进入激光武器射程",
                "部署多层防护系统"
            ])
        elif threat_level == ThreatLevel.HIGH:
            strategies.extend([
                "加强防护措施",
                "限制暴露时间",
                "使用间接接近路径"
            ])
        
        # 基于易损性因子的策略
        if vulnerability_factors.get('material_vulnerability', 0) > 70:
            strategies.append("考虑更换耐高温材料")
        
        if vulnerability_factors.get('structural_vulnerability', 0) > 70:
            strategies.append("增加结构厚度或多层防护")
        
        if vulnerability_factors.get('thermal_vulnerability', 0) > 70:
            strategies.append("改善热管理和散热设计")
        
        return strategies
    
    def generate_threat_report(self, assessment: ThreatAssessment) -> str:
        """生成威胁评估报告"""
        try:
            report = []
            report.append("=" * 60)
            report.append("激光武器威胁评估报告")
            report.append("=" * 60)
            
            report.append(f"\n威胁等级: {assessment.threat_level.value}")
            report.append(f"威胁评分: {assessment.threat_score:.1f}/100")
            report.append(f"防护效果: {assessment.protection_effectiveness:.1f}%")
            
            report.append(f"\n易损性因子:")
            for factor, value in assessment.vulnerability_factors.items():
                report.append(f"  {factor}: {value:.1f}%")
            
            report.append(f"\n对抗措施需求:")
            for requirement in assessment.countermeasure_requirements:
                report.append(f"  • {requirement}")
            
            report.append(f"\n风险缓解策略:")
            for strategy in assessment.risk_mitigation_strategies:
                report.append(f"  • {strategy}")
            
            report.append("=" * 60)
            
            return "\n".join(report)
            
        except Exception as e:
            self.logger.error(f"威胁报告生成失败: {e}")
            return "威胁报告生成失败"

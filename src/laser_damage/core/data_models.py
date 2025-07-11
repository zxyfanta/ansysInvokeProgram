"""
数据模型定义

定义系统中使用的各种数据结构和配置类。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import numpy as np
from datetime import datetime


class DamageLevel(Enum):
    """毁伤等级枚举"""
    MINIMAL = "轻微毁伤"
    MODERATE = "中等毁伤" 
    SEVERE = "严重毁伤"
    CRITICAL = "致命毁伤"


class SimulationStatus(Enum):
    """仿真状态枚举"""
    PENDING = "等待中"
    RUNNING = "运行中"
    COMPLETED = "已完成"
    FAILED = "失败"
    CANCELLED = "已取消"


@dataclass
class LaserConfiguration:
    """激光参数配置类"""
    power: float                    # 激光功率 (W)
    wavelength: float              # 波长 (nm)
    beam_diameter: float           # 光斑直径 (mm)
    pulse_duration: float = 0.001  # 脉冲持续时间 (s)
    repetition_rate: float = 1.0   # 重复频率 (Hz)
    beam_profile: str = "gaussian" # 光束轮廓类型
    divergence_angle: float = 0.0  # 发散角 (mrad)
    
    def validate(self) -> bool:
        """验证激光参数的有效性"""
        if self.power <= 0:
            raise ValueError("激光功率必须大于0")
        if self.wavelength <= 0:
            raise ValueError("波长必须大于0")
        if self.beam_diameter <= 0:
            raise ValueError("光斑直径必须大于0")
        if self.pulse_duration <= 0:
            raise ValueError("脉冲持续时间必须大于0")
        return True


@dataclass
class MaterialConfiguration:
    """材料参数配置类"""
    name: str                           # 材料名称
    thermal_conductivity: float         # 热导率 (W/m·K)
    specific_heat: float               # 比热容 (J/kg·K)
    density: float                     # 密度 (kg/m³)
    melting_point: float               # 熔点 (K)
    absorption_coefficient: float       # 吸收系数
    thermal_expansion: float = 0.0     # 热膨胀系数 (1/K)
    youngs_modulus: float = 0.0        # 杨氏模量 (Pa)
    poissons_ratio: float = 0.3        # 泊松比
    
    def validate(self) -> bool:
        """验证材料参数的有效性"""
        if self.thermal_conductivity <= 0:
            raise ValueError("热导率必须大于0")
        if self.specific_heat <= 0:
            raise ValueError("比热容必须大于0")
        if self.density <= 0:
            raise ValueError("密度必须大于0")
        return True


@dataclass
class EnvironmentConfiguration:
    """环境参数配置类"""
    ambient_temperature: float = 293.15  # 环境温度 (K)
    pressure: float = 101325.0           # 压力 (Pa)
    humidity: float = 0.5                # 相对湿度
    wind_speed: float = 0.0              # 风速 (m/s)
    atmospheric_transmission: float = 0.8 # 大气透过率


@dataclass
class FlightConfiguration:
    """飞行状态配置类"""
    altitude: float                # 飞行高度 (m)
    mach_number: float            # 马赫数
    angle_of_attack: float        # 攻角 (度)
    sideslip_angle: float = 0.0   # 侧滑角 (度)
    atmospheric_model: str = "standard"  # 大气模型


@dataclass
class SimulationResult:
    """仿真结果数据类"""
    simulation_id: str
    timestamp: datetime
    status: SimulationStatus
    
    # 温度场数据
    temperature_field: Optional[np.ndarray] = None
    max_temperature: Optional[float] = None
    min_temperature: Optional[float] = None
    
    # 应力场数据
    stress_field: Optional[np.ndarray] = None
    max_stress: Optional[float] = None
    von_mises_stress: Optional[np.ndarray] = None
    
    # 位移场数据
    displacement_field: Optional[np.ndarray] = None
    max_displacement: Optional[float] = None
    
    # 流场数据 (用于后效分析)
    velocity_field: Optional[np.ndarray] = None
    pressure_field: Optional[np.ndarray] = None
    
    # 元数据
    mesh_info: Dict[str, Any] = field(default_factory=dict)
    solver_info: Dict[str, Any] = field(default_factory=dict)
    computation_time: Optional[float] = None
    
    # 文件路径
    result_files: List[str] = field(default_factory=list)
    
    def get_summary(self) -> Dict[str, Any]:
        """获取结果摘要"""
        return {
            "simulation_id": self.simulation_id,
            "status": self.status.value,
            "max_temperature": self.max_temperature,
            "max_stress": self.max_stress,
            "max_displacement": self.max_displacement,
            "computation_time": self.computation_time,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class DamageMetrics:
    """毁伤指标类"""
    thermal_damage_area: float = 0.0      # 热损伤面积 (mm²)
    melting_volume: float = 0.0           # 熔化体积 (mm³)
    stress_concentration: float = 0.0      # 应力集中系数
    structural_integrity: float = 1.0      # 结构完整性指数 (0-1)
    aerodynamic_impact: float = 0.0        # 气动性能影响系数
    
    # 详细损伤信息
    damage_depth: float = 0.0             # 损伤深度 (mm)
    affected_components: List[str] = field(default_factory=list)
    critical_stress_points: List[Dict] = field(default_factory=list)
    
    def calculate_overall_damage(self) -> float:
        """计算综合毁伤程度 (0-1)"""
        # 简化的综合评估算法
        thermal_factor = min(self.thermal_damage_area / 1000.0, 1.0)
        stress_factor = min(self.stress_concentration / 10.0, 1.0)
        integrity_factor = 1.0 - self.structural_integrity
        
        return (thermal_factor + stress_factor + integrity_factor) / 3.0


@dataclass
class ProcessedData:
    """处理后的数据类"""
    raw_data: Dict[str, Any]
    processed_data: Dict[str, Any]
    statistics: Dict[str, float] = field(default_factory=dict)
    charts: List[str] = field(default_factory=list)  # 图表文件路径
    
    # 特定数据字段
    temperature_field: Optional[np.ndarray] = None
    stress_field: Optional[np.ndarray] = None
    damage_contour: Optional[np.ndarray] = None


@dataclass
class AssessmentReport:
    """评估报告类"""
    report_id: str
    timestamp: datetime
    damage_level: DamageLevel
    damage_metrics: DamageMetrics
    
    # 报告内容
    executive_summary: str = ""
    detailed_analysis: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # 附件
    charts: List[str] = field(default_factory=list)
    data_files: List[str] = field(default_factory=list)
    
    # 报告文件
    report_file_path: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "report_id": self.report_id,
            "timestamp": self.timestamp.isoformat(),
            "damage_level": self.damage_level.value,
            "damage_metrics": {
                "thermal_damage_area": self.damage_metrics.thermal_damage_area,
                "melting_volume": self.damage_metrics.melting_volume,
                "stress_concentration": self.damage_metrics.stress_concentration,
                "structural_integrity": self.damage_metrics.structural_integrity,
                "aerodynamic_impact": self.damage_metrics.aerodynamic_impact,
            },
            "executive_summary": self.executive_summary,
            "recommendations": self.recommendations,
            "charts": self.charts,
            "report_file_path": self.report_file_path,
        }

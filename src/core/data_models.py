"""
激光毁伤效能分析软件 - 数据模型

定义仿真中使用的数据结构。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import numpy as np
from datetime import datetime

class LaserType(Enum):
    """激光类型"""
    CONTINUOUS = "continuous"      # 连续激光
    PULSED = "pulsed"             # 脉冲激光
    QUASI_CONTINUOUS = "quasi_continuous"  # 准连续激光

class DamageMode(Enum):
    """毁伤模式"""
    THERMAL = "thermal"           # 热毁伤
    MECHANICAL = "mechanical"     # 机械毁伤
    COMBINED = "combined"         # 复合毁伤

class SimulationStatus(Enum):
    """仿真状态"""
    PENDING = "pending"           # 等待中
    RUNNING = "running"           # 运行中
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"            # 失败
    CANCELLED = "cancelled"       # 已取消

@dataclass
class LaserParameters:
    """激光参数"""
    power: float                  # 激光功率 (W)
    wavelength: float            # 波长 (nm)
    beam_diameter: float         # 光斑直径 (m)
    laser_type: LaserType         # 激光类型
    pulse_duration: float = 0.0  # 脉冲持续时间 (s)
    pulse_frequency: float = 0.0 # 脉冲频率 (Hz)
    beam_quality: float = 1.0    # 光束质量因子
    divergence_angle: float = 0.0 # 发散角 (mrad)
    
    @property
    def power_density(self) -> float:
        """功率密度 (W/m²)"""
        area = np.pi * (self.beam_diameter / 2) ** 2
        return self.power / area
    
    @property
    def energy_per_pulse(self) -> float:
        """单脉冲能量 (J)"""
        if self.laser_type == LaserType.PULSED:
            return self.power * self.pulse_duration
        return 0.0

@dataclass
class MaterialData:
    """材料数据"""
    name: str
    density: float               # 密度 (kg/m³)
    thermal_conductivity: float  # 热导率 (W/(m·K))
    specific_heat: float         # 比热容 (J/(kg·K))
    melting_point: float         # 熔点 (K)
    boiling_point: float         # 沸点 (K)
    absorptivity: float          # 吸收率
    youngs_modulus: float        # 杨氏模量 (Pa)
    poissons_ratio: float        # 泊松比
    thermal_expansion: float     # 热膨胀系数 (1/K)
    yield_strength: float        # 屈服强度 (Pa)

@dataclass
class GeometryData:
    """几何数据"""
    model_file: str              # 模型文件路径
    dimensions: Tuple[float, float, float]  # 尺寸 (长,宽,高)
    volume: float                # 体积 (m³)
    surface_area: float          # 表面积 (m²)
    mesh_size: float = 0.001     # 网格尺寸 (m)
    element_type: str = "SOLID70" # 单元类型

@dataclass
class BoundaryConditions:
    """边界条件"""
    ambient_temperature: float = 293.15  # 环境温度 (K)
    convection_coefficient: float = 10.0 # 对流换热系数 (W/(m²·K))
    radiation_emissivity: float = 0.8    # 辐射发射率
    fixed_constraints: List[str] = field(default_factory=list)  # 固定约束
    pressure_loads: Dict[str, float] = field(default_factory=dict)  # 压力载荷

@dataclass
class SimulationSettings:
    """仿真设置"""
    analysis_type: str = "transient"     # 分析类型
    time_step: float = 0.001            # 时间步长 (s)
    total_time: float = 1.0             # 总时间 (s)
    max_iterations: int = 1000          # 最大迭代次数
    convergence_tolerance: float = 1e-6  # 收敛容差
    solver_type: str = "direct"         # 求解器类型
    parallel_cores: int = 4             # 并行核心数

@dataclass
class SimulationResults:
    """仿真结果"""
    temperature_field: Optional[np.ndarray] = None    # 温度场
    stress_field: Optional[np.ndarray] = None         # 应力场
    displacement_field: Optional[np.ndarray] = None   # 位移场
    damage_region: Optional[np.ndarray] = None        # 毁伤区域
    max_temperature: float = 0.0                      # 最高温度 (K)
    max_stress: float = 0.0                          # 最大应力 (Pa)
    damage_volume: float = 0.0                       # 毁伤体积 (m³)
    damage_depth: float = 0.0                        # 毁伤深度 (m)
    computation_time: float = 0.0                    # 计算时间 (s)

@dataclass
class PostDamageResults:
    """毁伤后效结果"""
    aerodynamic_coefficients: Dict[str, float] = field(default_factory=dict)
    flight_trajectory: Optional[np.ndarray] = None
    stability_analysis: Dict[str, Any] = field(default_factory=dict)
    performance_degradation: float = 0.0

@dataclass
class SimulationData:
    """完整仿真数据"""
    # 基本信息
    simulation_id: str
    name: str
    laser_params: LaserParameters
    material_data: MaterialData
    geometry_data: GeometryData
    boundary_conditions: BoundaryConditions
    simulation_settings: SimulationSettings
    description: str = ""
    created_time: datetime = field(default_factory=datetime.now)
    status: SimulationStatus = SimulationStatus.PENDING
    
    # 结果数据
    laser_damage_results: Optional[SimulationResults] = None
    post_damage_results: Optional[PostDamageResults] = None
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        from dataclasses import asdict
        return {
            'simulation_id': self.simulation_id,
            'name': self.name,
            'description': self.description,
            'created_time': self.created_time.isoformat(),
            'status': self.status.value,
            'laser_params': asdict(self.laser_params),
            'material_data': asdict(self.material_data),
            'geometry_data': asdict(self.geometry_data),
            'boundary_conditions': asdict(self.boundary_conditions),
            'simulation_settings': asdict(self.simulation_settings),
            'metadata': self.metadata
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """获取仿真摘要"""
        summary = {
            'id': self.simulation_id,
            'name': self.name,
            'status': self.status.value,
            'laser_power': self.laser_params.power,
            'material': self.material_data.name,
            'created_time': self.created_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if self.laser_damage_results:
            summary.update({
                'max_temperature': self.laser_damage_results.max_temperature,
                'max_stress': self.laser_damage_results.max_stress,
                'damage_volume': self.laser_damage_results.damage_volume
            })
        
        return summary

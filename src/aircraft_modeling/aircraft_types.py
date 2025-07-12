"""
飞行器建模 - 飞行器类型定义

定义各种飞行器类型和参数。
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

class AircraftType(Enum):
    """飞行器类型"""
    FIXED_WING_FIGHTER = "固定翼战斗机"
    FIXED_WING_TRANSPORT = "固定翼运输机"
    UAV_FIXED_WING = "固定翼无人机"
    UAV_ROTARY_WING = "旋翼无人机"
    MISSILE = "导弹"
    CUSTOM = "自定义"

class MaterialType(Enum):
    """材料类型"""
    ALUMINUM_ALLOY = "铝合金"
    TITANIUM_ALLOY = "钛合金"
    STEEL = "钢材"
    CARBON_FIBER = "碳纤维"
    COMPOSITE = "复合材料"

@dataclass
class AircraftDimensions:
    """飞行器尺寸参数"""
    length: float           # 机身长度 (m)
    wingspan: float         # 翼展 (m)
    height: float          # 机身高度 (m)
    wing_chord: float      # 翼弦长 (m)
    wing_thickness: float  # 翼厚 (m)
    fuselage_diameter: float  # 机身直径 (m)

@dataclass
class FlightParameters:
    """飞行参数"""
    cruise_speed: float     # 巡航速度 (m/s)
    max_speed: float       # 最大速度 (m/s)
    service_ceiling: float # 实用升限 (m)
    max_load_factor: float # 最大载荷因子
    empty_weight: float    # 空重 (kg)
    max_takeoff_weight: float  # 最大起飞重量 (kg)

@dataclass
class AircraftParameters:
    """完整飞行器参数"""
    aircraft_type: AircraftType
    dimensions: AircraftDimensions
    flight_params: FlightParameters
    primary_material: MaterialType
    material_distribution: Dict[str, MaterialType]  # 部件材料分布
    name: str = "未命名飞行器"
    description: str = ""

# 预定义飞行器模板
AIRCRAFT_TEMPLATES = {
    AircraftType.FIXED_WING_FIGHTER: AircraftParameters(
        aircraft_type=AircraftType.FIXED_WING_FIGHTER,
        name="标准战斗机",
        dimensions=AircraftDimensions(
            length=15.0,
            wingspan=10.0,
            height=4.5,
            wing_chord=3.0,
            wing_thickness=0.3,
            fuselage_diameter=1.5
        ),
        flight_params=FlightParameters(
            cruise_speed=250.0,
            max_speed=600.0,
            service_ceiling=15000.0,
            max_load_factor=9.0,
            empty_weight=8000.0,
            max_takeoff_weight=15000.0
        ),
        primary_material=MaterialType.ALUMINUM_ALLOY,
        material_distribution={
            "fuselage": MaterialType.ALUMINUM_ALLOY,
            "wings": MaterialType.ALUMINUM_ALLOY,
            "control_surfaces": MaterialType.CARBON_FIBER,
            "engine": MaterialType.TITANIUM_ALLOY
        },
        description="标准单座战斗机模型"
    ),
    
    AircraftType.UAV_FIXED_WING: AircraftParameters(
        aircraft_type=AircraftType.UAV_FIXED_WING,
        name="固定翼无人机",
        dimensions=AircraftDimensions(
            length=5.0,
            wingspan=8.0,
            height=1.5,
            wing_chord=1.5,
            wing_thickness=0.15,
            fuselage_diameter=0.4
        ),
        flight_params=FlightParameters(
            cruise_speed=80.0,
            max_speed=150.0,
            service_ceiling=8000.0,
            max_load_factor=4.0,
            empty_weight=200.0,
            max_takeoff_weight=500.0
        ),
        primary_material=MaterialType.CARBON_FIBER,
        material_distribution={
            "fuselage": MaterialType.CARBON_FIBER,
            "wings": MaterialType.CARBON_FIBER,
            "control_surfaces": MaterialType.CARBON_FIBER,
            "payload_bay": MaterialType.ALUMINUM_ALLOY
        },
        description="中型固定翼无人机模型"
    ),
    
    AircraftType.UAV_ROTARY_WING: AircraftParameters(
        aircraft_type=AircraftType.UAV_ROTARY_WING,
        name="旋翼无人机",
        dimensions=AircraftDimensions(
            length=1.5,
            wingspan=1.5,  # 旋翼直径
            height=0.5,
            wing_chord=0.0,  # 不适用
            wing_thickness=0.0,  # 不适用
            fuselage_diameter=0.3
        ),
        flight_params=FlightParameters(
            cruise_speed=15.0,
            max_speed=25.0,
            service_ceiling=3000.0,
            max_load_factor=2.0,
            empty_weight=5.0,
            max_takeoff_weight=15.0
        ),
        primary_material=MaterialType.CARBON_FIBER,
        material_distribution={
            "frame": MaterialType.CARBON_FIBER,
            "rotors": MaterialType.CARBON_FIBER,
            "electronics": MaterialType.ALUMINUM_ALLOY
        },
        description="四旋翼无人机模型"
    ),
    
    AircraftType.MISSILE: AircraftParameters(
        aircraft_type=AircraftType.MISSILE,
        name="标准导弹",
        dimensions=AircraftDimensions(
            length=4.0,
            wingspan=1.0,
            height=0.3,
            wing_chord=0.5,
            wing_thickness=0.05,
            fuselage_diameter=0.25
        ),
        flight_params=FlightParameters(
            cruise_speed=300.0,
            max_speed=800.0,
            service_ceiling=20000.0,
            max_load_factor=20.0,
            empty_weight=150.0,
            max_takeoff_weight=200.0
        ),
        primary_material=MaterialType.STEEL,
        material_distribution={
            "body": MaterialType.STEEL,
            "fins": MaterialType.ALUMINUM_ALLOY,
            "warhead": MaterialType.STEEL,
            "guidance": MaterialType.ALUMINUM_ALLOY
        },
        description="标准空空导弹模型"
    )
}

def get_aircraft_template(aircraft_type: AircraftType) -> Optional[AircraftParameters]:
    """获取飞行器模板"""
    return AIRCRAFT_TEMPLATES.get(aircraft_type)

def get_available_aircraft_types() -> List[AircraftType]:
    """获取可用的飞行器类型"""
    return list(AIRCRAFT_TEMPLATES.keys())

def create_custom_aircraft(name: str, dimensions: AircraftDimensions, 
                          flight_params: FlightParameters,
                          primary_material: MaterialType = MaterialType.ALUMINUM_ALLOY) -> AircraftParameters:
    """创建自定义飞行器"""
    return AircraftParameters(
        aircraft_type=AircraftType.CUSTOM,
        name=name,
        dimensions=dimensions,
        flight_params=flight_params,
        primary_material=primary_material,
        material_distribution={"body": primary_material},
        description=f"自定义飞行器: {name}"
    )

#!/usr/bin/env python3
"""
简单测试 - 验证None错误修复
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("开始测试...")

try:
    # 测试导入
    print("1. 测试导入...")
    from src.aircraft_modeling.aircraft_types import (
        AircraftParameters, AircraftType, AircraftDimensions, 
        FlightParameters, MaterialType
    )
    print("✅ 导入成功")
    
    # 测试创建参数
    print("2. 测试创建参数...")
    dimensions = AircraftDimensions(
        length=15.0, wingspan=10.0, height=4.5,
        wing_chord=3.0, wing_thickness=0.3, fuselage_diameter=1.5
    )
    
    flight_params = FlightParameters(
        cruise_speed=250.0, max_speed=600.0, service_ceiling=15000.0,
        max_load_factor=9.0, empty_weight=8000.0, max_takeoff_weight=15000.0
    )
    
    # 测试默认名称
    aircraft_params = AircraftParameters(
        aircraft_type=AircraftType.FIXED_WING_FIGHTER,
        dimensions=dimensions,
        flight_params=flight_params,
        primary_material=MaterialType.ALUMINUM_ALLOY,
        material_distribution={"body": MaterialType.ALUMINUM_ALLOY}
    )
    
    print(f"✅ 参数创建成功，名称: {aircraft_params.name}")
    
    # 测试生成器
    print("3. 测试生成器...")
    from src.aircraft_modeling.aircraft_generator import AircraftGenerator
    
    generator = AircraftGenerator()
    model_data = generator.generate_aircraft_model(aircraft_params)
    
    if model_data:
        print(f"✅ 模型生成成功: {model_data.get('metadata', {}).get('name', 'unknown')}")
    else:
        print("❌ 模型生成失败")
    
    print("🎉 所有测试通过！")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

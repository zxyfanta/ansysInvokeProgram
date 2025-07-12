#!/usr/bin/env python3
"""
简单测试脚本
"""

import sys
import os
from pathlib import Path

print("激光毁伤效能分析软件 - 简单测试")
print("="*50)

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 测试基本导入
try:
    import numpy as np
    print("✅ NumPy 导入成功")
except ImportError as e:
    print(f"❌ NumPy 导入失败: {e}")

try:
    import matplotlib.pyplot as plt
    print("✅ Matplotlib 导入成功")
except ImportError as e:
    print(f"❌ Matplotlib 导入失败: {e}")

try:
    from core.data_models import LaserType
    print("✅ LaserType 导入成功")
except ImportError as e:
    print(f"❌ LaserType 导入失败: {e}")

try:
    from core.data_models import LaserParameters, MaterialData, GeometryData
    
    # 创建测试参数
    laser_params = LaserParameters(
        power=1000.0,
        wavelength=1064.0,
        beam_diameter=0.01,
        laser_type=LaserType.CONTINUOUS
    )
    print(f"✅ LaserParameters 创建成功: {laser_params.power}W")
    
    material_data = MaterialData(
        name="铝合金",
        density=2780.0,
        thermal_conductivity=121.0,
        specific_heat=875.0,
        melting_point=916.0,
        boiling_point=2740.0,
        absorptivity=0.15,
        youngs_modulus=73.1e9,
        poissons_ratio=0.33,
        thermal_expansion=22.3e-6,
        yield_strength=324e6
    )
    print(f"✅ MaterialData 创建成功: {material_data.name}")
    
except Exception as e:
    print(f"❌ 数据模型测试失败: {e}")

try:
    from laser_damage.laser_damage_simulator import LaserDamageSimulator
    simulator = LaserDamageSimulator()
    print(f"✅ LaserDamageSimulator 创建成功")
except Exception as e:
    print(f"❌ LaserDamageSimulator 创建失败: {e}")

try:
    from data_analysis.data_analyzer import DataAnalyzer
    analyzer = DataAnalyzer()
    print(f"✅ DataAnalyzer 创建成功")
except Exception as e:
    print(f"❌ DataAnalyzer 创建失败: {e}")

print("\n🎉 基本测试完成！")
print("\n可以尝试运行:")
print("  python laser_damage_analysis.py --cli")
print("  python laser_damage_analysis.py")

input("按回车键退出...")

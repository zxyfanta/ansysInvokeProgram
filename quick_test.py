#!/usr/bin/env python3
"""
快速测试修复
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

print("开始快速测试...")

try:
    # 测试导入
    from src.aircraft_modeling.aircraft_generator import AircraftGenerator
    print("✅ 导入成功")
    
    # 创建生成器
    generator = AircraftGenerator()
    print("✅ 生成器创建成功")
    
    # 创建简单测试模型
    test_model = {
        'components': {
            'box': {
                'type': 'simple_body',
                'shape': 'box',
                'size': [1.0, 1.0, 1.0],
                'position': [0, 0, 0]
            }
        },
        'metadata': {'name': '快速测试'}
    }
    
    # 生成网格
    mesh_data = generator._generate_mesh_from_model(test_model)
    print(f"✅ 网格生成: {mesh_data.get('triangle_count', 0)} 三角形")
    
    # 保存STL
    stl_path = Path("models/quick_test.stl")
    generator._export_to_stl(test_model, stl_path)
    
    if stl_path.exists():
        size = stl_path.stat().st_size
        print(f"✅ STL保存成功: {size} 字节")
    else:
        print("❌ STL保存失败")
    
    print("🎉 快速测试完成")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

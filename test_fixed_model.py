#!/usr/bin/env python3
"""
测试修复后的模型生成
"""

import sys
import struct
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_fixed_model():
    """测试修复后的模型生成"""
    print("🔧 测试修复后的模型生成...")
    
    try:
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        from src.aircraft_modeling.aircraft_types import (
            AircraftParameters, AircraftType, AircraftDimensions, 
            FlightParameters, MaterialType
        )
        
        # 创建生成器
        generator = AircraftGenerator()
        
        # 创建参数
        dimensions = AircraftDimensions(
            length=12.0,
            wingspan=10.0,
            height=3.5,
            wing_chord=2.5,
            wing_thickness=0.25,
            fuselage_diameter=1.2
        )
        
        flight_params = FlightParameters(
            cruise_speed=250.0,
            max_speed=500.0,
            service_ceiling=12000.0,
            max_load_factor=8.0,
            empty_weight=6000.0,
            max_takeoff_weight=10000.0
        )
        
        aircraft_params = AircraftParameters(
            aircraft_type=AircraftType.FIXED_WING_FIGHTER,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=MaterialType.ALUMINUM_ALLOY,
            material_distribution={"body": MaterialType.ALUMINUM_ALLOY},
            name="修复测试飞机"
        )
        
        print("✅ 参数创建成功")
        
        # 生成模型数据
        model_data = generator.generate_aircraft_model(aircraft_params)
        
        if not model_data:
            print("❌ 模型生成失败")
            return False
        
        print("✅ 模型数据生成成功")
        
        # 检查组件数据
        components = model_data.get('components', {})
        for comp_name, comp_data in components.items():
            print(f"   {comp_name}: {comp_data.get('type', 'unknown')}")
            if comp_data.get('type') == 'wing':
                print(f"     弦长: {comp_data.get('chord_root', 0):.3f} -> {comp_data.get('chord_tip', 0):.3f}")
        
        # 生成网格
        mesh_data = generator._generate_mesh_from_model(model_data)
        
        if not mesh_data:
            print("❌ 网格生成失败")
            return False
        
        print(f"✅ 网格生成成功:")
        print(f"   顶点数: {mesh_data.get('vertex_count', 0)}")
        print(f"   三角形数: {mesh_data.get('triangle_count', 0)}")
        
        # 保存为STL
        stl_path = Path("models/fixed_test.stl")
        generator._export_to_stl(model_data, stl_path)
        
        if stl_path.exists():
            print(f"✅ STL文件已保存: {stl_path}")
            
            # 验证STL文件
            with open(stl_path, 'rb') as f:
                # 跳过文件头
                f.read(80)
                
                # 读取三角形数量
                triangle_count_bytes = f.read(4)
                triangle_count = struct.unpack('<I', triangle_count_bytes)[0]
                
                print(f"   STL三角形数量: {triangle_count}")
                print(f"   文件大小: {stl_path.stat().st_size} 字节")
                
                if triangle_count > 0:
                    print("✅ STL文件格式正确")
                    
                    # 读取第一个三角形验证
                    normal = struct.unpack('<fff', f.read(12))
                    v1 = struct.unpack('<fff', f.read(12))
                    v2 = struct.unpack('<fff', f.read(12))
                    v3 = struct.unpack('<fff', f.read(12))
                    f.read(2)  # 属性
                    
                    print(f"   第一个三角形顶点:")
                    print(f"     ({v1[0]:.3f}, {v1[1]:.3f}, {v1[2]:.3f})")
                    print(f"     ({v2[0]:.3f}, {v2[1]:.3f}, {v2[2]:.3f})")
                    print(f"     ({v3[0]:.3f}, {v3[1]:.3f}, {v3[2]:.3f})")
                    
                    return True
                else:
                    print("❌ STL文件无三角形数据")
                    return False
        else:
            print("❌ STL文件未创建")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_shapes():
    """测试简单形状"""
    print("📐 测试简单形状...")
    
    try:
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        
        generator = AircraftGenerator()
        
        # 测试立方体
        box_model = {
            'components': {
                'box': {
                    'type': 'simple_body',
                    'shape': 'box',
                    'size': [2.0, 1.0, 1.0],
                    'position': [0, 0, 0]
                }
            },
            'metadata': {'name': '测试立方体'}
        }
        
        mesh_data = generator._generate_mesh_from_model(box_model)
        if mesh_data and mesh_data.get('triangle_count', 0) > 0:
            print("✅ 立方体网格生成成功")
            
            # 保存立方体STL
            generator._export_to_stl(box_model, Path("models/test_box.stl"))
            print("✅ 立方体STL已保存")
        else:
            print("❌ 立方体网格生成失败")
            return False
        
        # 测试圆柱体
        cylinder_model = {
            'components': {
                'cylinder': {
                    'type': 'simple_body',
                    'shape': 'cylinder',
                    'radius': 0.5,
                    'height': 2.0,
                    'position': [0, 0, 0]
                }
            },
            'metadata': {'name': '测试圆柱体'}
        }
        
        mesh_data = generator._generate_mesh_from_model(cylinder_model)
        if mesh_data and mesh_data.get('triangle_count', 0) > 0:
            print("✅ 圆柱体网格生成成功")
            
            # 保存圆柱体STL
            generator._export_to_stl(cylinder_model, Path("models/test_cylinder.stl"))
            print("✅ 圆柱体STL已保存")
        else:
            print("❌ 圆柱体网格生成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 简单形状测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("="*60)
    print("修复后模型生成测试")
    print("="*60)
    
    tests = [
        ("简单形状测试", test_simple_shapes),
        ("完整飞机模型测试", test_fixed_model)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过")
        else:
            print(f"❌ {test_name} 失败")
    
    print("\n" + "="*60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！模型生成已修复。")
        
        # 显示生成的文件
        models_dir = Path("models")
        if models_dir.exists():
            print(f"\n📁 生成的文件:")
            for file in models_dir.glob("*.stl"):
                size = file.stat().st_size
                print(f"   {file.name}: {size} 字节")
        
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
        return 1

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
测试STL导出功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_stl_export():
    """测试STL导出功能"""
    print("🧪 测试STL导出功能...")
    
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
            length=15.0,
            wingspan=10.0,
            height=4.5,
            wing_chord=3.0,
            wing_thickness=0.3,
            fuselage_diameter=1.5
        )
        
        flight_params = FlightParameters(
            cruise_speed=250.0,
            max_speed=600.0,
            service_ceiling=15000.0,
            max_load_factor=9.0,
            empty_weight=8000.0,
            max_takeoff_weight=15000.0
        )
        
        aircraft_params = AircraftParameters(
            aircraft_type=AircraftType.FIXED_WING_FIGHTER,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=MaterialType.ALUMINUM_ALLOY,
            material_distribution={"body": MaterialType.ALUMINUM_ALLOY},
            name="测试战斗机"
        )
        
        print("✅ 参数创建成功")
        
        # 测试JSON保存
        print("📄 测试JSON保存...")
        model_data = generator.generate_aircraft_model(aircraft_params, "test_aircraft.json")
        if model_data:
            print("✅ JSON保存成功")
        else:
            print("❌ JSON保存失败")
            return False
        
        # 测试STL保存
        print("🔺 测试STL保存...")
        model_data = generator.generate_aircraft_model(aircraft_params, "test_aircraft.stl")
        if model_data:
            print("✅ STL保存成功")
            
            # 检查文件是否存在
            stl_file = Path("models/test_aircraft.stl")
            if stl_file.exists():
                file_size = stl_file.stat().st_size
                print(f"✅ STL文件已创建: {stl_file} ({file_size} 字节)")
            else:
                print("❌ STL文件未找到")
                return False
        else:
            print("❌ STL保存失败")
            return False
        
        # 测试OBJ保存
        print("📐 测试OBJ保存...")
        model_data = generator.generate_aircraft_model(aircraft_params, "test_aircraft.obj")
        if model_data:
            print("✅ OBJ保存成功")
            
            # 检查文件是否存在
            obj_file = Path("models/test_aircraft.obj")
            if obj_file.exists():
                file_size = obj_file.stat().st_size
                print(f"✅ OBJ文件已创建: {obj_file} ({file_size} 字节)")
            else:
                print("❌ OBJ文件未找到")
                return False
        else:
            print("❌ OBJ保存失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mesh_generation():
    """测试网格生成"""
    print("🕸️ 测试网格生成...")
    
    try:
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        
        generator = AircraftGenerator()
        
        # 创建测试模型数据
        test_model = {
            'components': {
                'fuselage': {
                    'type': 'fuselage',
                    'stations': [
                        {'x': 0, 'radius': 0.1},
                        {'x': 1, 'radius': 0.5},
                        {'x': 2, 'radius': 0.5},
                        {'x': 3, 'radius': 0.1}
                    ]
                },
                'test_box': {
                    'type': 'simple_body',
                    'shape': 'box',
                    'size': [1.0, 1.0, 1.0],
                    'position': [0, 0, 0]
                }
            }
        }
        
        # 生成网格
        mesh_data = generator._generate_mesh_from_model(test_model)
        
        if mesh_data:
            print(f"✅ 网格生成成功:")
            print(f"   顶点数: {mesh_data.get('vertex_count', 0)}")
            print(f"   面数: {mesh_data.get('face_count', 0)}")
            print(f"   三角形数: {mesh_data.get('triangle_count', 0)}")
            return True
        else:
            print("❌ 网格生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 网格生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("STL导出功能测试")
    print("="*60)
    
    tests = [
        ("网格生成", test_mesh_generation),
        ("STL导出", test_stl_export)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print("\n" + "="*60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！STL导出功能正常。")
        
        # 显示生成的文件
        models_dir = Path("models")
        if models_dir.exists():
            print(f"\n📁 生成的文件:")
            for file in models_dir.glob("test_aircraft.*"):
                print(f"   {file}")
        
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        sys.exit(1)

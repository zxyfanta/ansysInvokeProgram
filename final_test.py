#!/usr/bin/env python3
"""
最终测试 - 验证STL导出修复
"""

import sys
import struct
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("🔧 最终STL导出测试")
    print("="*50)
    
    try:
        # 导入模块
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        from src.aircraft_modeling.aircraft_types import (
            AircraftParameters, AircraftType, AircraftDimensions, 
            FlightParameters, MaterialType
        )
        
        print("✅ 模块导入成功")
        
        # 创建生成器
        generator = AircraftGenerator()
        print("✅ 生成器创建成功")
        
        # 创建飞机参数
        dimensions = AircraftDimensions(
            length=10.0,
            wingspan=8.0,
            height=3.0,
            wing_chord=2.0,
            wing_thickness=0.2,
            fuselage_diameter=1.0
        )
        
        flight_params = FlightParameters(
            cruise_speed=200.0,
            max_speed=400.0,
            service_ceiling=10000.0,
            max_load_factor=6.0,
            empty_weight=5000.0,
            max_takeoff_weight=8000.0
        )
        
        aircraft_params = AircraftParameters(
            aircraft_type=AircraftType.FIXED_WING_FIGHTER,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=MaterialType.ALUMINUM_ALLOY,
            material_distribution={"body": MaterialType.ALUMINUM_ALLOY},
            name="最终测试飞机"
        )
        
        print("✅ 飞机参数创建成功")
        
        # 生成并保存STL
        output_file = "final_test_aircraft.stl"
        model_data = generator.generate_aircraft_model(aircraft_params, output_file)
        
        if model_data:
            print("✅ 模型生成成功")
            
            # 检查STL文件
            stl_path = Path(f"models/{output_file}")
            if stl_path.exists():
                print(f"✅ STL文件已创建: {stl_path}")
                
                # 验证STL文件内容
                with open(stl_path, 'rb') as f:
                    # 读取文件头
                    header = f.read(80)
                    print(f"📄 文件头: {header[:50].decode('ascii', errors='ignore')}...")
                    
                    # 读取三角形数量
                    triangle_count_bytes = f.read(4)
                    triangle_count = struct.unpack('<I', triangle_count_bytes)[0]
                    print(f"🔺 三角形数量: {triangle_count}")
                    
                    # 验证文件大小
                    expected_size = 80 + 4 + triangle_count * 50
                    actual_size = stl_path.stat().st_size
                    print(f"📏 期望大小: {expected_size} 字节")
                    print(f"📏 实际大小: {actual_size} 字节")
                    
                    if expected_size == actual_size and triangle_count > 0:
                        print("🎉 STL文件格式完全正确！")
                        
                        # 读取第一个三角形
                        normal = struct.unpack('<fff', f.read(12))
                        v1 = struct.unpack('<fff', f.read(12))
                        v2 = struct.unpack('<fff', f.read(12))
                        v3 = struct.unpack('<fff', f.read(12))
                        f.read(2)  # 属性
                        
                        print(f"🔺 第一个三角形:")
                        print(f"   法向量: ({normal[0]:.3f}, {normal[1]:.3f}, {normal[2]:.3f})")
                        print(f"   顶点1: ({v1[0]:.3f}, {v1[1]:.3f}, {v1[2]:.3f})")
                        print(f"   顶点2: ({v2[0]:.3f}, {v2[1]:.3f}, {v2[2]:.3f})")
                        print(f"   顶点3: ({v3[0]:.3f}, {v3[1]:.3f}, {v3[2]:.3f})")
                        
                        return True
                    else:
                        print("❌ STL文件格式有问题")
                        return False
            else:
                print("❌ STL文件未创建")
                return False
        else:
            print("❌ 模型生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 所有测试通过！STL导出功能已修复。")
        print("现在您可以正常生成和预览3D模型了。")
    else:
        print("\n❌ 测试失败，请检查错误信息。")

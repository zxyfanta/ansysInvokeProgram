#!/usr/bin/env python3
"""
诊断模型生成问题
"""

import sys
import json
import numpy as np
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def analyze_model_data():
    """分析模型数据"""
    print("🔍 分析模型数据...")
    
    try:
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        from src.aircraft_modeling.aircraft_types import (
            AircraftParameters, AircraftType, AircraftDimensions, 
            FlightParameters, MaterialType
        )
        
        # 创建生成器
        generator = AircraftGenerator()
        
        # 创建简单的测试参数
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
            name="诊断测试飞机"
        )
        
        # 生成模型数据
        model_data = generator.generate_aircraft_model(aircraft_params)
        
        if not model_data:
            print("❌ 模型生成失败")
            return False
        
        print("✅ 模型生成成功")
        print(f"📊 模型组件: {list(model_data.get('components', {}).keys())}")
        
        # 分析各个组件
        components = model_data.get('components', {})
        for comp_name, comp_data in components.items():
            print(f"\n🔧 分析组件: {comp_name}")
            print(f"   类型: {comp_data.get('type', 'unknown')}")
            
            if comp_data.get('type') == 'fuselage':
                stations = comp_data.get('stations', [])
                print(f"   站位数: {len(stations)}")
                if stations:
                    print(f"   第一站位: x={stations[0].get('x', 0)}, r={stations[0].get('radius', 0)}")
                    print(f"   最后站位: x={stations[-1].get('x', 0)}, r={stations[-1].get('radius', 0)}")
            
            elif comp_data.get('type') == 'wing':
                print(f"   展长: {comp_data.get('span', 0)}")
                print(f"   根弦长: {comp_data.get('chord_root', 0)}")
                print(f"   梢弦长: {comp_data.get('chord_tip', 0)}")
                print(f"   位置: {comp_data.get('position', [0,0,0])}")
        
        # 生成网格并分析
        print(f"\n🕸️ 生成网格...")
        mesh_data = generator._generate_mesh_from_model(model_data)
        
        if mesh_data:
            vertices = mesh_data.get('vertices', [])
            faces = mesh_data.get('faces', [])
            triangles = mesh_data.get('triangles', [])
            
            print(f"✅ 网格生成成功")
            print(f"   顶点数: {len(vertices)}")
            print(f"   面数: {len(faces)}")
            print(f"   三角形数: {len(triangles)}")
            
            # 检查顶点范围
            if vertices:
                vertices_array = np.array(vertices)
                min_coords = np.min(vertices_array, axis=0)
                max_coords = np.max(vertices_array, axis=0)
                print(f"   X范围: {min_coords[0]:.3f} ~ {max_coords[0]:.3f}")
                print(f"   Y范围: {min_coords[1]:.3f} ~ {max_coords[1]:.3f}")
                print(f"   Z范围: {min_coords[2]:.3f} ~ {max_coords[2]:.3f}")
                
                # 检查是否有无效顶点
                invalid_vertices = []
                for i, vertex in enumerate(vertices):
                    if any(not np.isfinite(coord) for coord in vertex):
                        invalid_vertices.append(i)
                
                if invalid_vertices:
                    print(f"⚠️ 发现 {len(invalid_vertices)} 个无效顶点")
                else:
                    print("✅ 所有顶点都有效")
            
            # 检查面的有效性
            if faces:
                invalid_faces = []
                for i, face in enumerate(faces):
                    if len(face) < 3:
                        invalid_faces.append(i)
                    elif any(idx < 0 or idx >= len(vertices) for idx in face):
                        invalid_faces.append(i)
                
                if invalid_faces:
                    print(f"⚠️ 发现 {len(invalid_faces)} 个无效面")
                else:
                    print("✅ 所有面都有效")
            
            return True
        else:
            print("❌ 网格生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_test_model():
    """创建简单的测试模型"""
    print("🔧 创建简单测试模型...")
    
    try:
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        
        generator = AircraftGenerator()
        
        # 创建一个简单的立方体模型用于测试
        test_model = {
            'components': {
                'test_box': {
                    'type': 'simple_body',
                    'shape': 'box',
                    'size': [2.0, 1.0, 1.0],
                    'position': [0, 0, 0]
                }
            },
            'metadata': {
                'name': '简单测试立方体',
                'aircraft_type': 'test'
            }
        }
        
        # 生成网格
        mesh_data = generator._generate_mesh_from_model(test_model)
        
        if mesh_data:
            print("✅ 简单模型网格生成成功")
            print(f"   顶点数: {mesh_data.get('vertex_count', 0)}")
            print(f"   三角形数: {mesh_data.get('triangle_count', 0)}")
            
            # 保存为STL
            generator._export_to_stl(test_model, Path("models/simple_test.stl"))
            print("✅ 简单测试STL已保存")
            
            return True
        else:
            print("❌ 简单模型网格生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 简单测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_existing_stl():
    """检查现有的STL文件"""
    print("📁 检查现有STL文件...")
    
    stl_files = list(Path("models").glob("*.stl"))
    
    for stl_file in stl_files:
        print(f"\n🔺 检查文件: {stl_file.name}")
        
        try:
            import struct
            
            with open(stl_file, 'rb') as f:
                # 读取文件头
                header = f.read(80)
                
                # 读取三角形数量
                triangle_count_bytes = f.read(4)
                triangle_count = struct.unpack('<I', triangle_count_bytes)[0]
                
                print(f"   三角形数量: {triangle_count}")
                print(f"   文件大小: {stl_file.stat().st_size} 字节")
                
                # 检查前几个三角形
                valid_triangles = 0
                for i in range(min(5, triangle_count)):
                    # 法向量 (12字节)
                    normal = struct.unpack('<fff', f.read(12))
                    
                    # 三个顶点 (36字节)
                    v1 = struct.unpack('<fff', f.read(12))
                    v2 = struct.unpack('<fff', f.read(12))
                    v3 = struct.unpack('<fff', f.read(12))
                    
                    # 属性 (2字节)
                    f.read(2)
                    
                    # 检查顶点是否有效
                    if all(np.isfinite(coord) for coord in v1 + v2 + v3):
                        valid_triangles += 1
                    
                    if i == 0:  # 显示第一个三角形
                        print(f"   第一个三角形:")
                        print(f"     顶点1: ({v1[0]:.3f}, {v1[1]:.3f}, {v1[2]:.3f})")
                        print(f"     顶点2: ({v2[0]:.3f}, {v2[1]:.3f}, {v2[2]:.3f})")
                        print(f"     顶点3: ({v3[0]:.3f}, {v3[1]:.3f}, {v3[2]:.3f})")
                
                print(f"   有效三角形: {valid_triangles}/5")
                
        except Exception as e:
            print(f"   ❌ 文件检查失败: {e}")

def main():
    """主函数"""
    print("="*60)
    print("模型生成问题诊断")
    print("="*60)
    
    tests = [
        ("检查现有STL文件", check_existing_stl),
        ("分析模型数据", analyze_model_data),
        ("创建简单测试模型", create_simple_test_model)
    ]
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        test_func()

if __name__ == "__main__":
    main()

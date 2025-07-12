#!/usr/bin/env python3
"""
验证STL文件
"""

import struct
from pathlib import Path

def verify_stl_file(stl_path):
    """验证STL文件格式"""
    try:
        with open(stl_path, 'rb') as f:
            # 读取文件头（80字节）
            header = f.read(80)
            print(f"STL文件头: {header[:50].decode('ascii', errors='ignore')}...")
            
            # 读取三角形数量（4字节）
            triangle_count_bytes = f.read(4)
            triangle_count = struct.unpack('<I', triangle_count_bytes)[0]
            print(f"三角形数量: {triangle_count}")
            
            # 验证文件大小
            expected_size = 80 + 4 + triangle_count * 50  # 每个三角形50字节
            actual_size = Path(stl_path).stat().st_size
            print(f"期望文件大小: {expected_size} 字节")
            print(f"实际文件大小: {actual_size} 字节")
            
            if expected_size == actual_size:
                print("✅ STL文件格式正确")
                return True
            else:
                print("❌ STL文件格式错误")
                return False
                
    except Exception as e:
        print(f"❌ STL验证失败: {e}")
        return False

def verify_obj_file(obj_path):
    """验证OBJ文件格式"""
    try:
        with open(obj_path, 'r') as f:
            lines = f.readlines()
        
        vertex_count = 0
        face_count = 0
        
        for line in lines:
            line = line.strip()
            if line.startswith('v '):
                vertex_count += 1
            elif line.startswith('f '):
                face_count += 1
        
        print(f"OBJ顶点数: {vertex_count}")
        print(f"OBJ面数: {face_count}")
        
        if vertex_count > 0 and face_count > 0:
            print("✅ OBJ文件格式正确")
            return True
        else:
            print("❌ OBJ文件格式错误")
            return False
            
    except Exception as e:
        print(f"❌ OBJ验证失败: {e}")
        return False

def main():
    """主函数"""
    print("="*50)
    print("3D文件格式验证")
    print("="*50)
    
    # 验证STL文件
    stl_file = Path("models/test_aircraft.stl")
    if stl_file.exists():
        print(f"\n🔺 验证STL文件: {stl_file}")
        verify_stl_file(stl_file)
    else:
        print("❌ STL文件不存在")
    
    # 验证OBJ文件
    obj_file = Path("models/test_aircraft.obj")
    if obj_file.exists():
        print(f"\n📐 验证OBJ文件: {obj_file}")
        verify_obj_file(obj_file)
    else:
        print("❌ OBJ文件不存在")
    
    # 显示所有模型文件
    models_dir = Path("models")
    if models_dir.exists():
        print(f"\n📁 所有模型文件:")
        for file in models_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size
                print(f"   {file.name}: {size} 字节")

if __name__ == "__main__":
    main()

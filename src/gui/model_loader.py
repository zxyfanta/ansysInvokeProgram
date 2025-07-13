"""
3D模型文件加载器 - 支持STL、OBJ等格式
"""

import struct
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class ModelLoader:
    """3D模型文件加载器"""
    
    @staticmethod
    def load_stl_file(file_path: str) -> Optional[Dict[str, Any]]:
        """加载STL文件"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"文件不存在: {file_path}")
                return None
            
            # 判断是二进制还是ASCII格式
            with open(file_path, 'rb') as f:
                header = f.read(80)
                if header.startswith(b'solid'):
                    # 可能是ASCII格式，需要进一步检查
                    f.seek(0)
                    try:
                        content = f.read(1024).decode('ascii')
                        if 'facet normal' in content:
                            return ModelLoader._load_stl_ascii(file_path)
                    except:
                        pass
                
                # 默认按二进制格式处理
                return ModelLoader._load_stl_binary(file_path)
        
        except Exception as e:
            print(f"加载STL文件失败: {e}")
            return None
    
    @staticmethod
    def _load_stl_binary(file_path: Path) -> Optional[Dict[str, Any]]:
        """加载二进制STL文件"""
        try:
            with open(file_path, 'rb') as f:
                # 跳过文件头（80字节）
                header = f.read(80)
                
                # 读取三角形数量
                triangle_count_bytes = f.read(4)
                triangle_count = struct.unpack('<I', triangle_count_bytes)[0]
                
                print(f"STL文件: {triangle_count} 个三角形")
                
                vertices = []
                triangles = []
                vertex_map = {}
                vertex_index = 0
                
                for i in range(triangle_count):
                    # 读取法向量（12字节）
                    normal_data = f.read(12)
                    normal = struct.unpack('<fff', normal_data)
                    
                    # 读取三个顶点（36字节）
                    triangle_vertices = []
                    triangle_coords = []
                    
                    for j in range(3):
                        vertex_data = f.read(12)
                        vertex = struct.unpack('<fff', vertex_data)
                        vertex_key = tuple(vertex)
                        
                        # 检查顶点是否已存在（去重）
                        if vertex_key not in vertex_map:
                            vertices.append(list(vertex))
                            vertex_map[vertex_key] = vertex_index
                            vertex_index += 1
                        
                        triangle_vertices.append(vertex_map[vertex_key])
                        triangle_coords.append(list(vertex))
                    
                    triangles.append(triangle_coords)
                    
                    # 跳过属性字节（2字节）
                    f.read(2)
                
                return {
                    'vertices': vertices,
                    'triangles': triangles,
                    'triangle_count': len(triangles),
                    'vertex_count': len(vertices),
                    'format': 'stl_binary'
                }
        
        except Exception as e:
            print(f"加载二进制STL失败: {e}")
            return None
    
    @staticmethod
    def _load_stl_ascii(file_path: Path) -> Optional[Dict[str, Any]]:
        """加载ASCII STL文件"""
        try:
            vertices = []
            triangles = []
            vertex_map = {}
            vertex_index = 0
            
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            i = 0
            triangle_count = 0
            
            while i < len(lines):
                line = lines[i].strip()
                
                if line.startswith('facet normal'):
                    # 开始一个新的三角形
                    triangle_vertices = []
                    triangle_coords = []
                    i += 1  # 跳到 outer loop
                    
                    # 读取三个顶点
                    for j in range(3):
                        i += 1
                        vertex_line = lines[i].strip()
                        if vertex_line.startswith('vertex'):
                            coords = vertex_line.split()[1:4]
                            vertex = [float(x) for x in coords]
                            vertex_key = tuple(vertex)
                            
                            # 检查顶点是否已存在
                            if vertex_key not in vertex_map:
                                vertices.append(vertex)
                                vertex_map[vertex_key] = vertex_index
                                vertex_index += 1
                            
                            triangle_vertices.append(vertex_map[vertex_key])
                            triangle_coords.append(vertex)
                    
                    triangles.append(triangle_coords)
                    triangle_count += 1
                
                i += 1
            
            print(f"ASCII STL文件: {triangle_count} 个三角形")
            
            return {
                'vertices': vertices,
                'triangles': triangles,
                'triangle_count': len(triangles),
                'vertex_count': len(vertices),
                'format': 'stl_ascii'
            }
        
        except Exception as e:
            print(f"加载ASCII STL失败: {e}")
            return None
    
    @staticmethod
    def load_obj_file(file_path: str) -> Optional[Dict[str, Any]]:
        """加载OBJ文件"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                print(f"文件不存在: {file_path}")
                return None
            
            vertices = []
            faces = []
            triangles = []
            
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if not parts:
                        continue
                    
                    if parts[0] == 'v':
                        # 顶点
                        vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                        vertices.append(vertex)
                    
                    elif parts[0] == 'f':
                        # 面
                        face_vertices = []
                        face_coords = []
                        
                        for i in range(1, len(parts)):
                            # OBJ索引从1开始
                            vertex_index = int(parts[i].split('/')[0]) - 1
                            if 0 <= vertex_index < len(vertices):
                                face_vertices.append(vertex_index)
                                face_coords.append(vertices[vertex_index])
                        
                        faces.append(face_vertices)
                        
                        # 将面转换为三角形
                        if len(face_coords) == 3:
                            triangles.append(face_coords)
                        elif len(face_coords) == 4:
                            # 四边形分解为两个三角形
                            triangles.append([face_coords[0], face_coords[1], face_coords[2]])
                            triangles.append([face_coords[0], face_coords[2], face_coords[3]])
            
            print(f"OBJ文件: {len(vertices)} 个顶点, {len(faces)} 个面, {len(triangles)} 个三角形")
            
            return {
                'vertices': vertices,
                'faces': faces,
                'triangles': triangles,
                'triangle_count': len(triangles),
                'vertex_count': len(vertices),
                'format': 'obj'
            }
        
        except Exception as e:
            print(f"加载OBJ文件失败: {e}")
            return None
    
    @staticmethod
    def load_model_file(file_path: str) -> Optional[Dict[str, Any]]:
        """根据文件扩展名自动选择加载器"""
        file_path = Path(file_path)
        suffix = file_path.suffix.lower()
        
        if suffix == '.stl':
            return ModelLoader.load_stl_file(str(file_path))
        elif suffix == '.obj':
            return ModelLoader.load_obj_file(str(file_path))
        else:
            print(f"不支持的文件格式: {suffix}")
            return None
    
    @staticmethod
    def get_model_info(model_data: Dict[str, Any]) -> str:
        """获取模型信息字符串"""
        if not model_data:
            return "无模型数据"
        
        info_lines = []
        info_lines.append(f"格式: {model_data.get('format', 'unknown')}")
        info_lines.append(f"顶点数: {model_data.get('vertex_count', 0)}")
        info_lines.append(f"三角形数: {model_data.get('triangle_count', 0)}")
        
        # 计算边界框
        vertices = model_data.get('vertices', [])
        if vertices:
            vertices_array = np.array(vertices)
            min_coords = np.min(vertices_array, axis=0)
            max_coords = np.max(vertices_array, axis=0)
            size = max_coords - min_coords
            
            info_lines.append(f"尺寸: {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f}")
            info_lines.append(f"边界框:")
            info_lines.append(f"  X: {min_coords[0]:.2f} ~ {max_coords[0]:.2f}")
            info_lines.append(f"  Y: {min_coords[1]:.2f} ~ {max_coords[1]:.2f}")
            info_lines.append(f"  Z: {min_coords[2]:.2f} ~ {max_coords[2]:.2f}")
        
        return "\n".join(info_lines)

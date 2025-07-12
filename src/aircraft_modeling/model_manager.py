"""
飞行器建模 - 模型管理器

实现飞行器模型的导入、验证、管理和转换功能。
"""

import sys
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

from .aircraft_types import AircraftParameters, AircraftType, MaterialType
from core.base_simulator import BaseSimulator

# 支持的文件格式
SUPPORTED_CAD_FORMATS = ['.step', '.stp', '.iges', '.igs', '.stl', '.obj']
SUPPORTED_DATA_FORMATS = ['.json', '.xml', '.yaml', '.yml']

class ModelManager(BaseSimulator):
    """模型管理器"""
    
    def __init__(self):
        super().__init__("ModelManager")
        
        # 模型库
        self.model_library: Dict[str, Dict[str, Any]] = {}
        
        # 模型目录
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
        # 导入的模型缓存
        self.imported_models: Dict[str, Any] = {}
        
        # 加载现有模型库
        self._load_model_library()
    
    def import_cad_model(self, file_path: str, model_name: str = None, 
                        aircraft_type: AircraftType = AircraftType.CUSTOM) -> Dict[str, Any]:
        """导入CAD模型"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"模型文件不存在: {file_path}")
            
            if file_path.suffix.lower() not in SUPPORTED_CAD_FORMATS:
                raise ValueError(f"不支持的文件格式: {file_path.suffix}")
            
            model_name = model_name or file_path.stem
            
            self.log_info(f"开始导入CAD模型: {file_path}")
            
            # 根据文件格式选择导入方法
            if file_path.suffix.lower() in ['.step', '.stp']:
                model_data = self._import_step_file(file_path)
            elif file_path.suffix.lower() in ['.iges', '.igs']:
                model_data = self._import_iges_file(file_path)
            elif file_path.suffix.lower() == '.stl':
                model_data = self._import_stl_file(file_path)
            elif file_path.suffix.lower() == '.obj':
                model_data = self._import_obj_file(file_path)
            else:
                raise ValueError(f"暂不支持的格式: {file_path.suffix}")
            
            # 添加元数据
            model_data['metadata'] = {
                'name': model_name,
                'source_file': str(file_path),
                'aircraft_type': aircraft_type.value,
                'import_time': self.get_current_time(),
                'file_format': file_path.suffix.lower()
            }
            
            # 验证模型
            validation_result = self._validate_model(model_data)
            model_data['validation'] = validation_result
            
            # 存储模型
            self.imported_models[model_name] = model_data
            
            # 添加到模型库
            self._add_to_library(model_name, model_data)
            
            self.log_info(f"CAD模型导入完成: {model_name}")
            return model_data
            
        except Exception as e:
            self.log_error(f"CAD模型导入失败: {e}")
            return {}
    
    def import_data_model(self, file_path: str, model_name: str = None) -> Dict[str, Any]:
        """导入数据模型（JSON/XML等）"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"数据文件不存在: {file_path}")
            
            if file_path.suffix.lower() not in SUPPORTED_DATA_FORMATS:
                raise ValueError(f"不支持的数据格式: {file_path.suffix}")
            
            model_name = model_name or file_path.stem
            
            self.log_info(f"开始导入数据模型: {file_path}")
            
            # 根据文件格式读取数据
            if file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
            elif file_path.suffix.lower() == '.xml':
                model_data = self._import_xml_file(file_path)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                model_data = self._import_yaml_file(file_path)
            else:
                raise ValueError(f"暂不支持的格式: {file_path.suffix}")
            
            # 验证数据结构
            if not self._validate_data_structure(model_data):
                self.log_warning("数据结构验证失败，尝试自动修复")
                model_data = self._repair_data_structure(model_data)
            
            # 存储模型
            self.imported_models[model_name] = model_data
            
            self.log_info(f"数据模型导入完成: {model_name}")
            return model_data
            
        except Exception as e:
            self.log_error(f"数据模型导入失败: {e}")
            return {}
    
    def _import_step_file(self, file_path: Path) -> Dict[str, Any]:
        """导入STEP文件"""
        try:
            # 这里需要CAD库支持，如FreeCAD、OpenCASCADE等
            # 简化实现：读取文件信息并创建基本几何描述
            
            file_size = file_path.stat().st_size
            
            # 基本几何信息（需要实际CAD库解析）
            model_data = {
                'type': 'imported_cad',
                'format': 'step',
                'file_size': file_size,
                'geometry': {
                    'bounding_box': self._estimate_bounding_box(file_path),
                    'surface_count': self._estimate_surface_count(file_path),
                    'volume': self._estimate_volume(file_path)
                },
                'components': self._extract_components(file_path)
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"STEP文件导入失败: {e}")
            return {'type': 'import_failed', 'error': str(e)}
    
    def _import_iges_file(self, file_path: Path) -> Dict[str, Any]:
        """导入IGES文件"""
        # 类似STEP文件的处理
        return self._import_step_file(file_path)
    
    def _import_stl_file(self, file_path: Path) -> Dict[str, Any]:
        """导入STL文件"""
        try:
            # STL文件是三角网格格式，相对简单
            triangles = self._read_stl_triangles(file_path)
            
            model_data = {
                'type': 'mesh_model',
                'format': 'stl',
                'triangle_count': len(triangles),
                'vertices': self._extract_vertices(triangles),
                'triangles': triangles,
                'bounding_box': self._calculate_mesh_bounds(triangles)
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"STL文件导入失败: {e}")
            return {'type': 'import_failed', 'error': str(e)}
    
    def _import_obj_file(self, file_path: Path) -> Dict[str, Any]:
        """导入OBJ文件"""
        try:
            vertices = []
            faces = []
            
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('v '):
                        # 顶点
                        coords = [float(x) for x in line.split()[1:4]]
                        vertices.append(coords)
                    elif line.startswith('f '):
                        # 面
                        face_indices = [int(x.split('/')[0]) - 1 for x in line.split()[1:]]
                        faces.append(face_indices)
            
            model_data = {
                'type': 'mesh_model',
                'format': 'obj',
                'vertex_count': len(vertices),
                'face_count': len(faces),
                'vertices': vertices,
                'faces': faces,
                'bounding_box': self._calculate_vertex_bounds(vertices)
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"OBJ文件导入失败: {e}")
            return {'type': 'import_failed', 'error': str(e)}
    
    def _import_xml_file(self, file_path: Path) -> Dict[str, Any]:
        """导入XML文件"""
        try:
            import xml.etree.ElementTree as ET
            
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 简化的XML解析
            model_data = self._xml_to_dict(root)
            
            return model_data
            
        except Exception as e:
            self.log_error(f"XML文件导入失败: {e}")
            return {'type': 'import_failed', 'error': str(e)}
    
    def _import_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """导入YAML文件"""
        try:
            import yaml
            
            with open(file_path, 'r', encoding='utf-8') as f:
                model_data = yaml.safe_load(f)
            
            return model_data
            
        except ImportError:
            self.log_error("PyYAML未安装，无法导入YAML文件")
            return {'type': 'import_failed', 'error': 'PyYAML not installed'}
        except Exception as e:
            self.log_error(f"YAML文件导入失败: {e}")
            return {'type': 'import_failed', 'error': str(e)}
    
    def _validate_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """验证模型数据"""
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'suggestions': []
        }
        
        try:
            # 检查基本结构
            if 'type' not in model_data:
                validation_result['warnings'].append("缺少模型类型信息")
            
            # 检查几何信息
            if 'geometry' in model_data or 'vertices' in model_data:
                geometry_check = self._validate_geometry(model_data)
                validation_result['warnings'].extend(geometry_check.get('warnings', []))
                validation_result['errors'].extend(geometry_check.get('errors', []))
            
            # 检查尺寸合理性
            bounds_check = self._validate_dimensions(model_data)
            validation_result['suggestions'].extend(bounds_check.get('suggestions', []))
            
            # 如果有错误，标记为无效
            if validation_result['errors']:
                validation_result['is_valid'] = False
            
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"验证过程出错: {e}")
        
        return validation_result
    
    def _validate_geometry(self, model_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证几何数据"""
        result = {'warnings': [], 'errors': []}
        
        # 检查边界框
        if 'bounding_box' in model_data.get('geometry', {}):
            bbox = model_data['geometry']['bounding_box']
            if any(dim <= 0 for dim in bbox.values() if isinstance(dim, (int, float))):
                result['errors'].append("边界框尺寸无效")
        
        # 检查网格数据
        if 'vertices' in model_data and 'triangles' in model_data:
            vertices = model_data['vertices']
            triangles = model_data['triangles']
            
            if len(vertices) < 3:
                result['errors'].append("顶点数量不足")
            
            if len(triangles) < 1:
                result['errors'].append("三角形数量不足")
        
        return result
    
    def _validate_dimensions(self, model_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """验证尺寸合理性"""
        result = {'suggestions': []}
        
        # 获取模型尺寸
        dimensions = self._extract_model_dimensions(model_data)
        
        if dimensions:
            length, width, height = dimensions
            
            # 检查尺寸合理性
            if length > 100:  # 超过100米
                result['suggestions'].append("模型长度较大，请确认单位是否正确")
            
            if any(dim < 0.01 for dim in dimensions):  # 小于1厘米
                result['suggestions'].append("模型尺寸较小，请确认单位是否正确")
            
            # 检查长宽比
            if length > 0 and width > 0:
                aspect_ratio = length / width
                if aspect_ratio > 20:
                    result['suggestions'].append("长宽比较大，可能是细长型飞行器")
                elif aspect_ratio < 0.5:
                    result['suggestions'].append("长宽比较小，可能是宽体型飞行器")
        
        return result
    
    def _validate_data_structure(self, data: Dict[str, Any]) -> bool:
        """验证数据结构"""
        # 检查是否包含必要的字段
        required_fields = ['type']

        for field in required_fields:
            if field not in data:
                return False

        return True
    
    def _repair_data_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """修复数据结构"""
        repaired_data = data.copy()
        
        # 添加缺失的必要字段
        if 'type' not in repaired_data:
            repaired_data['type'] = 'unknown'
        
        if 'metadata' not in repaired_data:
            repaired_data['metadata'] = {
                'name': 'imported_model',
                'import_time': self.get_current_time()
            }
        
        return repaired_data
    
    def _estimate_bounding_box(self, file_path: Path) -> Dict[str, float]:
        """估算边界框（简化实现）"""
        # 实际需要CAD库解析
        return {
            'min_x': 0.0, 'max_x': 10.0,
            'min_y': -5.0, 'max_y': 5.0,
            'min_z': -2.0, 'max_z': 2.0,
            'length': 10.0,
            'width': 10.0,
            'height': 4.0
        }
    
    def _estimate_surface_count(self, file_path: Path) -> int:
        """估算表面数量"""
        # 基于文件大小的粗略估算
        file_size = file_path.stat().st_size
        return max(10, file_size // 1000)  # 简化估算
    
    def _estimate_volume(self, file_path: Path) -> float:
        """估算体积"""
        bbox = self._estimate_bounding_box(file_path)
        return bbox['length'] * bbox['width'] * bbox['height'] * 0.3  # 假设30%填充率
    
    def _extract_components(self, file_path: Path) -> List[Dict[str, Any]]:
        """提取组件信息"""
        # 简化实现，实际需要CAD库解析
        return [
            {'name': 'fuselage', 'type': 'body'},
            {'name': 'wing', 'type': 'lifting_surface'},
            {'name': 'tail', 'type': 'control_surface'}
        ]
    
    def _read_stl_triangles(self, file_path: Path) -> List[List[List[float]]]:
        """读取STL三角形数据"""
        triangles = []
        
        try:
            with open(file_path, 'rb') as f:
                # 检查是否为二进制STL
                header = f.read(80)
                if b'solid' in header[:5]:
                    # ASCII STL
                    f.seek(0)
                    triangles = self._read_ascii_stl(f)
                else:
                    # Binary STL
                    triangles = self._read_binary_stl(f)
        
        except Exception as e:
            self.log_error(f"STL文件读取失败: {e}")
        
        return triangles
    
    def _read_ascii_stl(self, file_obj) -> List[List[List[float]]]:
        """读取ASCII格式STL"""
        triangles = []
        current_triangle = []
        
        for line in file_obj:
            line = line.decode('utf-8').strip()
            
            if line.startswith('vertex'):
                coords = [float(x) for x in line.split()[1:4]]
                current_triangle.append(coords)
                
                if len(current_triangle) == 3:
                    triangles.append(current_triangle)
                    current_triangle = []
        
        return triangles
    
    def _read_binary_stl(self, file_obj) -> List[List[List[float]]]:
        """读取二进制格式STL"""
        import struct
        
        triangles = []
        
        # 跳过头部
        file_obj.seek(80)
        
        # 读取三角形数量
        triangle_count = struct.unpack('<I', file_obj.read(4))[0]
        
        for _ in range(triangle_count):
            # 跳过法向量
            file_obj.read(12)
            
            # 读取三个顶点
            triangle = []
            for _ in range(3):
                vertex = struct.unpack('<fff', file_obj.read(12))
                triangle.append(list(vertex))
            
            triangles.append(triangle)
            
            # 跳过属性字节
            file_obj.read(2)
        
        return triangles
    
    def _extract_vertices(self, triangles: List[List[List[float]]]) -> List[List[float]]:
        """从三角形中提取唯一顶点"""
        vertices = []
        vertex_set = set()
        
        for triangle in triangles:
            for vertex in triangle:
                vertex_tuple = tuple(vertex)
                if vertex_tuple not in vertex_set:
                    vertices.append(vertex)
                    vertex_set.add(vertex_tuple)
        
        return vertices
    
    def _calculate_mesh_bounds(self, triangles: List[List[List[float]]]) -> Dict[str, float]:
        """计算网格边界"""
        if not triangles:
            return {}
        
        all_coords = []
        for triangle in triangles:
            all_coords.extend(triangle)
        
        return self._calculate_vertex_bounds(all_coords)
    
    def _calculate_vertex_bounds(self, vertices: List[List[float]]) -> Dict[str, float]:
        """计算顶点边界"""
        if not vertices:
            return {}
        
        vertices_array = np.array(vertices)
        
        min_coords = np.min(vertices_array, axis=0)
        max_coords = np.max(vertices_array, axis=0)
        
        return {
            'min_x': float(min_coords[0]), 'max_x': float(max_coords[0]),
            'min_y': float(min_coords[1]), 'max_y': float(max_coords[1]),
            'min_z': float(min_coords[2]), 'max_z': float(max_coords[2]),
            'length': float(max_coords[0] - min_coords[0]),
            'width': float(max_coords[1] - min_coords[1]),
            'height': float(max_coords[2] - min_coords[2])
        }
    
    def _extract_model_dimensions(self, model_data: Dict[str, Any]) -> Optional[Tuple[float, float, float]]:
        """提取模型尺寸"""
        # 从边界框提取
        if 'geometry' in model_data and 'bounding_box' in model_data['geometry']:
            bbox = model_data['geometry']['bounding_box']
            return (bbox.get('length', 0), bbox.get('width', 0), bbox.get('height', 0))
        
        # 从边界框直接提取
        if 'bounding_box' in model_data:
            bbox = model_data['bounding_box']
            return (bbox.get('length', 0), bbox.get('width', 0), bbox.get('height', 0))
        
        return None
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """XML元素转字典"""
        result = {}
        
        # 添加属性
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # 添加文本内容
        if element.text and element.text.strip():
            result['text'] = element.text.strip()
        
        # 添加子元素
        for child in element:
            child_data = self._xml_to_dict(child)
            
            if child.tag in result:
                # 如果已存在，转为列表
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data
        
        return result
    
    def _load_model_library(self):
        """加载模型库"""
        library_file = self.models_dir / "model_library.json"
        
        if library_file.exists():
            try:
                with open(library_file, 'r', encoding='utf-8') as f:
                    self.model_library = json.load(f)
                self.log_info(f"已加载模型库: {len(self.model_library)} 个模型")
            except Exception as e:
                self.log_error(f"模型库加载失败: {e}")
    
    def _add_to_library(self, model_name: str, model_data: Dict[str, Any]):
        """添加到模型库"""
        self.model_library[model_name] = {
            'metadata': model_data.get('metadata', {}),
            'validation': model_data.get('validation', {}),
            'file_path': model_data.get('metadata', {}).get('source_file', ''),
            'added_time': self.get_current_time()
        }
        
        # 保存模型库
        self._save_model_library()
    
    def _save_model_library(self):
        """保存模型库"""
        library_file = self.models_dir / "model_library.json"
        
        try:
            with open(library_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_library, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            self.log_error(f"模型库保存失败: {e}")
    
    def get_model_library(self) -> Dict[str, Any]:
        """获取模型库"""
        return self.model_library.copy()
    
    def get_imported_models(self) -> Dict[str, Any]:
        """获取导入的模型"""
        return self.imported_models.copy()
    
    def get_model(self, model_name: str) -> Optional[Dict[str, Any]]:
        """获取指定模型"""
        return self.imported_models.get(model_name)
    
    def remove_model(self, model_name: str) -> bool:
        """移除模型"""
        if model_name in self.imported_models:
            del self.imported_models[model_name]
            
            if model_name in self.model_library:
                del self.model_library[model_name]
                self._save_model_library()
            
            self.log_info(f"已移除模型: {model_name}")
            return True
        
        return False

    # 实现BaseSimulator的抽象方法
    def setup_simulation(self, **kwargs) -> bool:
        """设置仿真参数"""
        return True

    def run_simulation(self) -> bool:
        """运行仿真"""
        return True

    def get_results(self) -> Dict[str, Any]:
        """获取仿真结果"""
        return self.imported_models

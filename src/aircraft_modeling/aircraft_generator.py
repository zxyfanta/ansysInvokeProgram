"""
飞行器建模 - 飞行器模型生成器

实现各种飞行器模型的自动生成功能。
"""

import sys
import logging
import struct
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import json

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

from .aircraft_types import AircraftType, AircraftParameters, AircraftDimensions
from core.base_simulator import BaseSimulator

# 尝试导入CAD库
try:
    import FreeCAD
    import Part
    FREECAD_AVAILABLE = True
except ImportError:
    FREECAD_AVAILABLE = False

class AircraftGenerator(BaseSimulator):
    """飞行器模型生成器"""

    def __init__(self):
        super().__init__("AircraftGenerator")
        
        # 生成的模型存储
        self.generated_models: Dict[str, Any] = {}
        
        # 输出目录
        self.output_dir = Path("models")
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_aircraft_model(self, aircraft_params: AircraftParameters, 
                               output_file: str = None) -> Dict[str, Any]:
        """生成飞行器模型"""
        try:
            model_name = aircraft_params.name if aircraft_params.name else "未命名飞行器"
            self.log_info(f"开始生成飞行器模型: {model_name}")
            
            # 根据飞行器类型选择生成方法
            if aircraft_params.aircraft_type == AircraftType.FIXED_WING_FIGHTER:
                model_data = self._generate_fighter_model(aircraft_params)
            elif aircraft_params.aircraft_type == AircraftType.UAV_FIXED_WING:
                model_data = self._generate_fixed_wing_uav_model(aircraft_params)
            elif aircraft_params.aircraft_type == AircraftType.UAV_ROTARY_WING:
                model_data = self._generate_rotary_wing_uav_model(aircraft_params)
            elif aircraft_params.aircraft_type == AircraftType.MISSILE:
                model_data = self._generate_missile_model(aircraft_params)
            else:
                model_data = self._generate_generic_model(aircraft_params)
            
            # 添加元数据
            model_data['metadata'] = {
                'aircraft_type': aircraft_params.aircraft_type.value,
                'name': model_name,
                'generated_time': self.get_current_time(),
                'generator_version': '1.0.0'
            }

            # 保存模型
            if output_file:
                self._save_model(model_data, output_file)

            # 存储到内存
            self.generated_models[model_name] = model_data

            self.log_info(f"飞行器模型生成完成: {model_name}")
            return model_data
            
        except Exception as e:
            self.log_error(f"飞行器模型生成失败: {e}")
            return {}
    
    def _generate_fighter_model(self, params: AircraftParameters) -> Dict[str, Any]:
        """生成战斗机模型"""
        try:
            dims = params.dimensions
            
            # 机身几何
            fuselage = self._create_fuselage_geometry(
                length=dims.length,
                diameter=dims.fuselage_diameter,
                nose_length=dims.length * 0.2,
                tail_length=dims.length * 0.3
            )
            
            # 主翼几何
            main_wing = self._create_wing_geometry(
                span=dims.wingspan,
                chord_root=dims.wing_chord,
                chord_tip=dims.wing_chord * 0.6,
                thickness=dims.wing_thickness,
                sweep_angle=25.0,  # 后掠角
                position=(dims.length * 0.4, 0, 0)
            )
            
            # 垂直尾翼
            vertical_tail = self._create_wing_geometry(
                span=dims.height * 0.8,
                chord_root=dims.wing_chord * 0.4,
                chord_tip=dims.wing_chord * 0.2,
                thickness=dims.wing_thickness * 0.8,
                sweep_angle=35.0,
                position=(dims.length * 0.85, 0, 0),
                vertical=True
            )
            
            # 水平尾翼
            horizontal_tail = self._create_wing_geometry(
                span=dims.wingspan * 0.4,
                chord_root=dims.wing_chord * 0.3,
                chord_tip=dims.wing_chord * 0.2,
                thickness=dims.wing_thickness * 0.6,
                sweep_angle=20.0,
                position=(dims.length * 0.9, 0, dims.height * 0.1)
            )
            
            # 组装模型
            model_data = {
                'type': 'fighter_aircraft',
                'components': {
                    'fuselage': fuselage,
                    'main_wing': main_wing,
                    'vertical_tail': vertical_tail,
                    'horizontal_tail': horizontal_tail
                },
                'materials': params.material_distribution,
                'dimensions': dims.__dict__,
                'flight_parameters': params.flight_params.__dict__
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"战斗机模型生成失败: {e}")
            return {}
    
    def _generate_fixed_wing_uav_model(self, params: AircraftParameters) -> Dict[str, Any]:
        """生成固定翼无人机模型"""
        try:
            dims = params.dimensions
            
            # 简化的机身（更细长）
            fuselage = self._create_fuselage_geometry(
                length=dims.length,
                diameter=dims.fuselage_diameter,
                nose_length=dims.length * 0.15,
                tail_length=dims.length * 0.25
            )
            
            # 高展弦比主翼
            main_wing = self._create_wing_geometry(
                span=dims.wingspan,
                chord_root=dims.wing_chord,
                chord_tip=dims.wing_chord * 0.8,
                thickness=dims.wing_thickness,
                sweep_angle=5.0,  # 小后掠角
                position=(dims.length * 0.3, 0, 0)
            )
            
            # 简单的尾翼
            tail_assembly = self._create_simple_tail(
                position=(dims.length * 0.9, 0, 0),
                v_tail_span=dims.height * 0.6,
                h_tail_span=dims.wingspan * 0.3,
                chord=dims.wing_chord * 0.25
            )
            
            model_data = {
                'type': 'fixed_wing_uav',
                'components': {
                    'fuselage': fuselage,
                    'main_wing': main_wing,
                    'tail_assembly': tail_assembly
                },
                'materials': params.material_distribution,
                'dimensions': dims.__dict__,
                'flight_parameters': params.flight_params.__dict__
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"固定翼无人机模型生成失败: {e}")
            return {}
    
    def _generate_rotary_wing_uav_model(self, params: AircraftParameters) -> Dict[str, Any]:
        """生成旋翼无人机模型"""
        try:
            dims = params.dimensions
            
            # 中心机身
            fuselage = self._create_simple_body(
                length=dims.length,
                width=dims.fuselage_diameter,
                height=dims.height
            )
            
            # 旋翼系统（四旋翼）
            rotor_positions = [
                (dims.wingspan/2, dims.wingspan/2, dims.height),
                (-dims.wingspan/2, dims.wingspan/2, dims.height),
                (-dims.wingspan/2, -dims.wingspan/2, dims.height),
                (dims.wingspan/2, -dims.wingspan/2, dims.height)
            ]
            
            rotors = []
            for i, pos in enumerate(rotor_positions):
                rotor = self._create_rotor_assembly(
                    position=pos,
                    diameter=dims.wingspan * 0.4,
                    blade_count=2
                )
                rotors.append(rotor)
            
            model_data = {
                'type': 'rotary_wing_uav',
                'components': {
                    'fuselage': fuselage,
                    'rotors': rotors
                },
                'materials': params.material_distribution,
                'dimensions': dims.__dict__,
                'flight_parameters': params.flight_params.__dict__
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"旋翼无人机模型生成失败: {e}")
            return {}
    
    def _generate_missile_model(self, params: AircraftParameters) -> Dict[str, Any]:
        """生成导弹模型"""
        try:
            dims = params.dimensions
            
            # 圆柱形弹体
            body = self._create_cylindrical_body(
                length=dims.length,
                diameter=dims.fuselage_diameter,
                nose_cone_length=dims.length * 0.2
            )
            
            # 控制翼面
            control_fins = []
            fin_positions = [0, 90, 180, 270]  # 四片翼面
            
            for angle in fin_positions:
                fin = self._create_control_fin(
                    position=(dims.length * 0.8, 0, 0),
                    span=dims.wingspan / 2,
                    chord=dims.wing_chord,
                    thickness=dims.wing_thickness,
                    angle=angle
                )
                control_fins.append(fin)
            
            model_data = {
                'type': 'missile',
                'components': {
                    'body': body,
                    'control_fins': control_fins
                },
                'materials': params.material_distribution,
                'dimensions': dims.__dict__,
                'flight_parameters': params.flight_params.__dict__
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"导弹模型生成失败: {e}")
            return {}
    
    def _generate_generic_model(self, params: AircraftParameters) -> Dict[str, Any]:
        """生成通用模型"""
        try:
            dims = params.dimensions
            
            # 简单的盒状模型
            body = self._create_simple_body(
                length=dims.length,
                width=dims.fuselage_diameter,
                height=dims.height
            )
            
            model_data = {
                'type': 'generic_aircraft',
                'components': {
                    'body': body
                },
                'materials': params.material_distribution,
                'dimensions': dims.__dict__,
                'flight_parameters': params.flight_params.__dict__
            }
            
            return model_data
            
        except Exception as e:
            self.log_error(f"通用模型生成失败: {e}")
            return {}
    
    def _create_fuselage_geometry(self, length: float, diameter: float, 
                                 nose_length: float, tail_length: float) -> Dict[str, Any]:
        """创建机身几何"""
        # 使用参数化描述机身几何
        stations = []
        
        # 机头段
        for i in range(10):
            x = (i / 9) * nose_length
            r = diameter / 2 * (i / 9) ** 0.5  # 椭圆形机头
            stations.append({'x': x, 'radius': r})
        
        # 中段（等直径）
        mid_length = length - nose_length - tail_length
        for i in range(20):
            x = nose_length + (i / 19) * mid_length
            r = diameter / 2
            stations.append({'x': x, 'radius': r})
        
        # 尾段
        for i in range(10):
            x = nose_length + mid_length + (i / 9) * tail_length
            r = diameter / 2 * (1 - (i / 9) ** 2)  # 收缩尾部
            stations.append({'x': x, 'radius': r})
        
        return {
            'type': 'fuselage',
            'stations': stations,
            'length': length,
            'max_diameter': diameter
        }
    
    def _create_wing_geometry(self, span: float, chord_root: float, chord_tip: float,
                             thickness: float, sweep_angle: float, position: Tuple[float, float, float],
                             vertical: bool = False) -> Dict[str, Any]:
        """创建机翼几何"""
        # 翼型截面（简化为对称翼型）
        airfoil_points = self._generate_naca_airfoil("0012", 50)  # NACA 0012翼型
        
        # 翼根和翼尖截面
        root_section = {
            'position': position,
            'chord': chord_root,
            'thickness': thickness,
            'airfoil': airfoil_points
        }
        
        tip_position = list(position)
        if vertical:
            tip_position[2] += span  # Z方向
        else:
            tip_position[1] += span / 2  # Y方向
            tip_position[0] += span / 2 * np.tan(np.radians(sweep_angle))  # 后掠
        
        tip_section = {
            'position': tip_position,
            'chord': chord_tip,
            'thickness': thickness * 0.8,
            'airfoil': airfoil_points
        }
        
        return {
            'type': 'wing',
            'span': span,
            'sweep_angle': sweep_angle,
            'vertical': vertical,
            'root_section': root_section,
            'tip_section': tip_section
        }
    
    def _create_simple_tail(self, position: Tuple[float, float, float],
                           v_tail_span: float, h_tail_span: float, chord: float) -> Dict[str, Any]:
        """创建简单尾翼组合"""
        return {
            'type': 'tail_assembly',
            'position': position,
            'vertical_tail': {
                'span': v_tail_span,
                'chord': chord,
                'thickness': chord * 0.1
            },
            'horizontal_tail': {
                'span': h_tail_span,
                'chord': chord,
                'thickness': chord * 0.08
            }
        }
    
    def _create_simple_body(self, length: float, width: float, height: float) -> Dict[str, Any]:
        """创建简单机身"""
        return {
            'type': 'simple_body',
            'length': length,
            'width': width,
            'height': height,
            'shape': 'box'
        }
    
    def _create_cylindrical_body(self, length: float, diameter: float, nose_cone_length: float) -> Dict[str, Any]:
        """创建圆柱形弹体"""
        return {
            'type': 'cylindrical_body',
            'length': length,
            'diameter': diameter,
            'nose_cone_length': nose_cone_length,
            'shape': 'cylinder'
        }
    
    def _create_rotor_assembly(self, position: Tuple[float, float, float],
                              diameter: float, blade_count: int) -> Dict[str, Any]:
        """创建旋翼组件"""
        return {
            'type': 'rotor',
            'position': position,
            'diameter': diameter,
            'blade_count': blade_count,
            'blade_chord': diameter * 0.05,
            'blade_twist': 10.0  # 度
        }
    
    def _create_control_fin(self, position: Tuple[float, float, float],
                           span: float, chord: float, thickness: float, angle: float) -> Dict[str, Any]:
        """创建控制翼面"""
        return {
            'type': 'control_fin',
            'position': position,
            'span': span,
            'chord': chord,
            'thickness': thickness,
            'rotation_angle': angle
        }
    
    def _generate_naca_airfoil(self, naca_code: str, num_points: int) -> List[Tuple[float, float]]:
        """生成NACA翼型坐标"""
        # 简化的NACA翼型生成（仅支持4位对称翼型）
        if len(naca_code) != 4 or naca_code[:2] != "00":
            # 默认使用对称翼型
            thickness = 0.12
        else:
            thickness = int(naca_code[2:]) / 100.0
        
        points = []
        
        # 上表面
        for i in range(num_points // 2 + 1):
            x = i / (num_points // 2)
            y = thickness / 0.2 * (0.2969 * np.sqrt(x) - 0.1260 * x - 
                                   0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
            points.append((x, y))
        
        # 下表面
        for i in range(num_points // 2 - 1, -1, -1):
            x = i / (num_points // 2)
            y = -thickness / 0.2 * (0.2969 * np.sqrt(x) - 0.1260 * x - 
                                    0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
            points.append((x, y))
        
        return points
    
    def _save_model(self, model_data: Dict[str, Any], output_file: str):
        """保存模型数据"""
        try:
            output_path = self.output_dir / output_file

            # 保存为JSON格式
            if output_path.suffix.lower() == '.json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(model_data, f, indent=2, ensure_ascii=False, default=str)

            # 保存为STL格式
            elif output_path.suffix.lower() == '.stl':
                self._export_to_stl(model_data, output_path)

            # 保存为OBJ格式
            elif output_path.suffix.lower() == '.obj':
                self._export_to_obj(model_data, output_path)

            # 如果有FreeCAD，也可以保存为CAD格式
            elif FREECAD_AVAILABLE and output_path.suffix.lower() in ['.step', '.stp']:
                self._export_to_cad(model_data, output_path)

            else:
                # 默认保存为JSON
                json_path = output_path.with_suffix('.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(model_data, f, indent=2, ensure_ascii=False, default=str)
                self.log_info(f"不支持的格式，已保存为JSON: {json_path}")
                return

            self.log_info(f"模型已保存: {output_path}")

        except Exception as e:
            self.log_error(f"模型保存失败: {e}")
    
    def _export_to_cad(self, model_data: Dict[str, Any], output_path: Path):
        """导出为CAD格式（需要FreeCAD）"""
        if not FREECAD_AVAILABLE:
            self.log_warning("FreeCAD不可用，无法导出CAD格式")
            return
        
        try:
            # 这里可以实现FreeCAD的CAD文件生成
            # 由于FreeCAD集成较复杂，这里仅作为接口预留
            self.log_info("CAD导出功能需要进一步实现")
            
        except Exception as e:
            self.log_error(f"CAD导出失败: {e}")
    
    def get_generated_models(self) -> Dict[str, Any]:
        """获取已生成的模型"""
        return self.generated_models.copy()
    
    def clear_models(self):
        """清空已生成的模型"""
        self.generated_models.clear()
        self.log_info("已清空生成的模型")

    # 实现BaseSimulator的抽象方法
    def setup_simulation(self, **kwargs) -> bool:
        """设置仿真参数"""
        return True

    def run_simulation(self) -> bool:
        """运行仿真"""
        return True

    def get_results(self) -> Dict[str, Any]:
        """获取仿真结果"""
        return self.generated_models

    def _export_to_stl(self, model_data: Dict[str, Any], output_path: Path):
        """导出为STL格式"""
        try:
            # 生成3D网格数据
            mesh_data = self._generate_mesh_from_model(model_data)

            if not mesh_data or 'triangles' not in mesh_data:
                self.log_error("无法生成网格数据")
                return

            triangles = mesh_data['triangles']

            # 写入STL文件（二进制格式）
            with open(output_path, 'wb') as f:
                # STL文件头（80字节）
                header = f"Generated by Aircraft Modeling System - {model_data.get('metadata', {}).get('name', 'Unknown')}"
                header = header[:80].ljust(80, '\0')
                f.write(header.encode('ascii', errors='ignore'))

                # 三角形数量（4字节）
                f.write(struct.pack('<I', len(triangles)))

                # 写入每个三角形
                for triangle in triangles:
                    # 计算法向量
                    v1 = np.array(triangle[1]) - np.array(triangle[0])
                    v2 = np.array(triangle[2]) - np.array(triangle[0])
                    normal = np.cross(v1, v2)
                    normal = normal / np.linalg.norm(normal) if np.linalg.norm(normal) > 0 else [0, 0, 1]

                    # 法向量（12字节）
                    f.write(struct.pack('<fff', *normal))

                    # 三个顶点（36字节）
                    for vertex in triangle:
                        f.write(struct.pack('<fff', *vertex))

                    # 属性字节计数（2字节）
                    f.write(struct.pack('<H', 0))

            self.log_info(f"STL文件已保存: {output_path}")

        except Exception as e:
            self.log_error(f"STL导出失败: {e}")

    def _export_to_obj(self, model_data: Dict[str, Any], output_path: Path):
        """导出为OBJ格式"""
        try:
            # 生成3D网格数据
            mesh_data = self._generate_mesh_from_model(model_data)

            if not mesh_data or 'vertices' not in mesh_data or 'faces' not in mesh_data:
                self.log_error("无法生成网格数据")
                return

            vertices = mesh_data['vertices']
            faces = mesh_data['faces']

            # 写入OBJ文件
            with open(output_path, 'w') as f:
                # 文件头
                f.write(f"# Generated by Aircraft Modeling System\n")
                f.write(f"# Model: {model_data.get('metadata', {}).get('name', 'Unknown')}\n")
                f.write(f"# Vertices: {len(vertices)}\n")
                f.write(f"# Faces: {len(faces)}\n\n")

                # 写入顶点
                for vertex in vertices:
                    f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")

                f.write("\n")

                # 写入面（OBJ格式索引从1开始）
                for face in faces:
                    if len(face) == 3:  # 三角形
                        f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")
                    elif len(face) == 4:  # 四边形
                        f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1} {face[3]+1}\n")

            self.log_info(f"OBJ文件已保存: {output_path}")

        except Exception as e:
            self.log_error(f"OBJ导出失败: {e}")

    def _generate_mesh_from_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """从模型数据生成3D网格"""
        try:
            vertices = []
            faces = []
            triangles = []

            # 处理各个组件
            components = model_data.get('components', {})

            for comp_name, comp_data in components.items():
                comp_vertices, comp_faces = self._generate_component_mesh(comp_data)

                # 添加顶点（调整索引）
                vertex_offset = len(vertices)
                vertices.extend(comp_vertices)

                # 添加面（调整索引）
                for face in comp_faces:
                    adjusted_face = [idx + vertex_offset for idx in face]
                    faces.append(adjusted_face)

                    # 如果是三角形，直接添加到triangles
                    if len(adjusted_face) == 3:
                        triangle_vertices = [vertices[idx] for idx in adjusted_face]
                        triangles.append(triangle_vertices)
                    # 如果是四边形，分解为两个三角形
                    elif len(adjusted_face) == 4:
                        # 三角形1: 0,1,2
                        triangle1 = [vertices[adjusted_face[0]], vertices[adjusted_face[1]], vertices[adjusted_face[2]]]
                        triangles.append(triangle1)
                        # 三角形2: 0,2,3
                        triangle2 = [vertices[adjusted_face[0]], vertices[adjusted_face[2]], vertices[adjusted_face[3]]]
                        triangles.append(triangle2)

            return {
                'vertices': vertices,
                'faces': faces,
                'triangles': triangles,
                'vertex_count': len(vertices),
                'face_count': len(faces),
                'triangle_count': len(triangles)
            }

        except Exception as e:
            self.log_error(f"网格生成失败: {e}")
            return {}

    def _generate_component_mesh(self, comp_data: Dict[str, Any]) -> Tuple[List[List[float]], List[List[int]]]:
        """生成组件网格"""
        comp_type = comp_data.get('type', '')

        if comp_type == 'fuselage':
            return self._generate_fuselage_mesh(comp_data)
        elif comp_type == 'wing':
            return self._generate_wing_mesh(comp_data)
        elif comp_type in ['simple_body', 'cylindrical_body']:
            return self._generate_simple_body_mesh(comp_data)
        else:
            self.log_warning(f"未知组件类型: {comp_type}")
            return [], []

    def _generate_fuselage_mesh(self, fuselage_data: Dict[str, Any]) -> Tuple[List[List[float]], List[List[int]]]:
        """生成机身网格"""
        stations = fuselage_data.get('stations', [])
        if len(stations) < 2:
            return [], []

        vertices = []
        faces = []

        # 为每个站位生成圆形截面
        sections = []
        for station in stations:
            x = station['x']
            radius = station['radius']

            # 生成圆形截面点（16个点）
            section_points = []
            for i in range(16):
                angle = 2 * np.pi * i / 16
                y = radius * np.cos(angle)
                z = radius * np.sin(angle)
                section_points.append([x, y, z])

            sections.append(section_points)
            vertices.extend(section_points)

        # 连接相邻截面生成面
        for i in range(len(sections) - 1):
            for j in range(16):
                next_j = (j + 1) % 16

                # 当前截面的索引
                curr_base = i * 16
                next_base = (i + 1) * 16

                # 生成四边形面（两个三角形）
                v1 = curr_base + j
                v2 = curr_base + next_j
                v3 = next_base + next_j
                v4 = next_base + j

                # 添加两个三角形
                faces.append([v1, v2, v3])
                faces.append([v1, v3, v4])

        return vertices, faces

    def _generate_wing_mesh(self, wing_data: Dict[str, Any]) -> Tuple[List[List[float]], List[List[int]]]:
        """生成机翼网格"""
        span = wing_data.get('span', 10.0)
        chord_root = wing_data.get('chord_root', 3.0)
        chord_tip = wing_data.get('chord_tip', 1.5)
        thickness = wing_data.get('thickness', 0.3)
        position = wing_data.get('position', [0, 0, 0])
        vertical = wing_data.get('vertical', False)

        vertices = []
        faces = []

        # 生成翼型截面点
        airfoil_points = wing_data.get('airfoil_points', [])
        if not airfoil_points:
            # 使用简单的对称翼型
            airfoil_points = []
            for i in range(21):
                x = i / 20.0
                if x <= 0.5:
                    y = thickness * (0.5 - x) * 2
                else:
                    y = thickness * (x - 0.5) * 2
                airfoil_points.append([x, y])
                if i > 0 and i < 20:  # 添加下表面点
                    airfoil_points.append([x, -y])

        # 生成翼根和翼尖截面
        sections = []

        # 翼根截面
        root_section = []
        for point in airfoil_points:
            x = point[0] * chord_root + position[0]
            y = position[1] if not vertical else point[1] * chord_root + position[1]
            z = point[1] * chord_root + position[2] if not vertical else position[2]
            root_section.append([x, y, z])

        # 翼尖截面
        tip_section = []
        for point in airfoil_points:
            x = point[0] * chord_tip + position[0]
            y = position[1] + span if not vertical else point[1] * chord_tip + position[1]
            z = point[1] * chord_tip + position[2] if not vertical else position[2] + span
            tip_section.append([x, y, z])

        sections = [root_section, tip_section]

        # 添加顶点
        for section in sections:
            vertices.extend(section)

        # 生成面
        n_points = len(airfoil_points)
        for i in range(n_points - 1):
            # 连接翼根和翼尖对应点
            v1 = i
            v2 = i + 1
            v3 = n_points + i + 1
            v4 = n_points + i

            # 添加四边形面（两个三角形）
            faces.append([v1, v2, v3])
            faces.append([v1, v3, v4])

        return vertices, faces

    def _generate_simple_body_mesh(self, body_data: Dict[str, Any]) -> Tuple[List[List[float]], List[List[int]]]:
        """生成简单体网格"""
        shape = body_data.get('shape', 'box')

        if shape == 'box':
            return self._generate_box_mesh(body_data)
        elif shape == 'cylinder':
            return self._generate_cylinder_mesh(body_data)
        else:
            return [], []

    def _generate_box_mesh(self, box_data: Dict[str, Any]) -> Tuple[List[List[float]], List[List[int]]]:
        """生成立方体网格"""
        size = box_data.get('size', [1.0, 1.0, 1.0])
        position = box_data.get('position', [0, 0, 0])

        # 立方体的8个顶点
        vertices = [
            [position[0] - size[0]/2, position[1] - size[1]/2, position[2] - size[2]/2],  # 0
            [position[0] + size[0]/2, position[1] - size[1]/2, position[2] - size[2]/2],  # 1
            [position[0] + size[0]/2, position[1] + size[1]/2, position[2] - size[2]/2],  # 2
            [position[0] - size[0]/2, position[1] + size[1]/2, position[2] - size[2]/2],  # 3
            [position[0] - size[0]/2, position[1] - size[1]/2, position[2] + size[2]/2],  # 4
            [position[0] + size[0]/2, position[1] - size[1]/2, position[2] + size[2]/2],  # 5
            [position[0] + size[0]/2, position[1] + size[1]/2, position[2] + size[2]/2],  # 6
            [position[0] - size[0]/2, position[1] + size[1]/2, position[2] + size[2]/2],  # 7
        ]

        # 立方体的12个三角形面
        faces = [
            # 底面
            [0, 1, 2], [0, 2, 3],
            # 顶面
            [4, 7, 6], [4, 6, 5],
            # 前面
            [0, 4, 5], [0, 5, 1],
            # 后面
            [2, 6, 7], [2, 7, 3],
            # 左面
            [0, 3, 7], [0, 7, 4],
            # 右面
            [1, 5, 6], [1, 6, 2],
        ]

        return vertices, faces

    def _generate_cylinder_mesh(self, cylinder_data: Dict[str, Any]) -> Tuple[List[List[float]], List[List[int]]]:
        """生成圆柱体网格"""
        radius = cylinder_data.get('radius', 0.5)
        height = cylinder_data.get('height', 2.0)
        position = cylinder_data.get('position', [0, 0, 0])
        segments = 16  # 圆周分段数

        vertices = []
        faces = []

        # 生成底面和顶面的圆周点
        for level in [0, 1]:  # 0=底面, 1=顶面
            z = position[2] + (level * height - height/2)
            for i in range(segments):
                angle = 2 * np.pi * i / segments
                x = position[0] + radius * np.cos(angle)
                y = position[1] + radius * np.sin(angle)
                vertices.append([x, y, z])

        # 添加中心点
        vertices.append([position[0], position[1], position[2] - height/2])  # 底面中心
        vertices.append([position[0], position[1], position[2] + height/2])  # 顶面中心

        # 生成侧面
        for i in range(segments):
            next_i = (i + 1) % segments

            # 底面到顶面的四边形（两个三角形）
            v1 = i                    # 底面当前点
            v2 = next_i               # 底面下一点
            v3 = segments + next_i    # 顶面下一点
            v4 = segments + i         # 顶面当前点

            faces.append([v1, v2, v3])
            faces.append([v1, v3, v4])

        # 生成底面和顶面
        bottom_center = len(vertices) - 2
        top_center = len(vertices) - 1

        for i in range(segments):
            next_i = (i + 1) % segments

            # 底面三角形
            faces.append([bottom_center, next_i, i])

            # 顶面三角形
            faces.append([top_center, segments + i, segments + next_i])

        return vertices, faces

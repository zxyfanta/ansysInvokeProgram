"""
激光毁伤效能分析软件 - 材料数据库

管理仿真中使用的材料属性数据。
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class ThermalProperties:
    """热学属性"""
    thermal_conductivity: float  # 热导率 W/(m·K)
    specific_heat: float         # 比热容 J/(kg·K)
    density: float              # 密度 kg/m³
    thermal_expansion: float    # 热膨胀系数 1/K
    melting_point: float        # 熔点 K
    boiling_point: float        # 沸点 K

@dataclass
class MechanicalProperties:
    """力学属性"""
    youngs_modulus: float       # 杨氏模量 Pa
    poissons_ratio: float       # 泊松比
    yield_strength: float       # 屈服强度 Pa
    ultimate_strength: float    # 极限强度 Pa
    fracture_toughness: float   # 断裂韧性 Pa·m^0.5

@dataclass
class OpticalProperties:
    """光学属性"""
    absorptivity: float         # 吸收率
    reflectivity: float         # 反射率
    transmissivity: float       # 透射率
    refractive_index: float     # 折射率

@dataclass
class Material:
    """材料定义"""
    name: str
    category: str
    description: str
    thermal: ThermalProperties
    mechanical: MechanicalProperties
    optical: OpticalProperties
    temperature_dependent: bool = False
    custom_properties: Dict[str, Any] = None

class MaterialDatabase:
    """材料数据库管理器"""
    
    def __init__(self, database_file: str = "materials.yml"):
        self.logger = logging.getLogger(__name__)
        self.database_file = database_file
        self.materials: Dict[str, Material] = {}
        
        # 加载默认材料
        self._load_default_materials()
        
        # 加载用户材料数据库
        self.load_database()
    
    def _load_default_materials(self):
        """加载默认材料数据"""
        # 铝合金 2024-T3
        aluminum_2024 = Material(
            name="铝合金2024-T3",
            category="金属",
            description="航空用铝合金",
            thermal=ThermalProperties(
                thermal_conductivity=121.0,
                specific_heat=875.0,
                density=2780.0,
                thermal_expansion=22.3e-6,
                melting_point=916.0,
                boiling_point=2740.0
            ),
            mechanical=MechanicalProperties(
                youngs_modulus=73.1e9,
                poissons_ratio=0.33,
                yield_strength=324e6,
                ultimate_strength=469e6,
                fracture_toughness=26e6
            ),
            optical=OpticalProperties(
                absorptivity=0.15,
                reflectivity=0.85,
                transmissivity=0.0,
                refractive_index=1.44
            )
        )
        
        # 钛合金 Ti-6Al-4V
        titanium_6al4v = Material(
            name="钛合金Ti-6Al-4V",
            category="金属",
            description="航空用钛合金",
            thermal=ThermalProperties(
                thermal_conductivity=6.7,
                specific_heat=526.0,
                density=4430.0,
                thermal_expansion=8.6e-6,
                melting_point=1933.0,
                boiling_point=3560.0
            ),
            mechanical=MechanicalProperties(
                youngs_modulus=113.8e9,
                poissons_ratio=0.342,
                yield_strength=880e6,
                ultimate_strength=950e6,
                fracture_toughness=75e6
            ),
            optical=OpticalProperties(
                absorptivity=0.25,
                reflectivity=0.75,
                transmissivity=0.0,
                refractive_index=2.49
            )
        )
        
        # 碳纤维复合材料
        carbon_fiber = Material(
            name="碳纤维复合材料",
            category="复合材料",
            description="T300/5208碳纤维复合材料",
            thermal=ThermalProperties(
                thermal_conductivity=0.87,
                specific_heat=1050.0,
                density=1600.0,
                thermal_expansion=0.02e-6,
                melting_point=3773.0,
                boiling_point=4273.0
            ),
            mechanical=MechanicalProperties(
                youngs_modulus=181e9,
                poissons_ratio=0.28,
                yield_strength=1500e6,
                ultimate_strength=1500e6,
                fracture_toughness=45e6
            ),
            optical=OpticalProperties(
                absorptivity=0.95,
                reflectivity=0.05,
                transmissivity=0.0,
                refractive_index=1.7
            )
        )
        
        # 添加到数据库
        self.materials[aluminum_2024.name] = aluminum_2024
        self.materials[titanium_6al4v.name] = titanium_6al4v
        self.materials[carbon_fiber.name] = carbon_fiber
    
    def load_database(self):
        """加载材料数据库文件"""
        db_path = Path(self.database_file)
        
        if not db_path.exists():
            self.logger.info("材料数据库文件不存在，使用默认材料")
            return
        
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data or 'materials' not in data:
                self.logger.warning("材料数据库格式错误")
                return
            
            for mat_data in data['materials']:
                material = self._dict_to_material(mat_data)
                if material:
                    self.materials[material.name] = material
                    
            self.logger.info(f"加载了 {len(data['materials'])} 个材料")
            
        except Exception as e:
            self.logger.error(f"加载材料数据库失败: {e}")
    
    def save_database(self):
        """保存材料数据库"""
        try:
            materials_data = []
            for material in self.materials.values():
                materials_data.append(self._material_to_dict(material))
            
            data = {'materials': materials_data}
            
            with open(self.database_file, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
                         
            self.logger.info("材料数据库保存成功")
            
        except Exception as e:
            self.logger.error(f"保存材料数据库失败: {e}")
    
    def _dict_to_material(self, data: Dict) -> Optional[Material]:
        """字典转材料对象"""
        try:
            return Material(
                name=data['name'],
                category=data['category'],
                description=data['description'],
                thermal=ThermalProperties(**data['thermal']),
                mechanical=MechanicalProperties(**data['mechanical']),
                optical=OpticalProperties(**data['optical']),
                temperature_dependent=data.get('temperature_dependent', False),
                custom_properties=data.get('custom_properties')
            )
        except Exception as e:
            self.logger.error(f"材料数据转换失败: {e}")
            return None
    
    def _material_to_dict(self, material: Material) -> Dict:
        """材料对象转字典"""
        return {
            'name': material.name,
            'category': material.category,
            'description': material.description,
            'thermal': asdict(material.thermal),
            'mechanical': asdict(material.mechanical),
            'optical': asdict(material.optical),
            'temperature_dependent': material.temperature_dependent,
            'custom_properties': material.custom_properties
        }
    
    def get_material(self, name: str) -> Optional[Material]:
        """获取材料"""
        return self.materials.get(name)
    
    def get_materials_by_category(self, category: str) -> List[Material]:
        """按类别获取材料"""
        return [mat for mat in self.materials.values() 
                if mat.category == category]
    
    def get_all_materials(self) -> List[Material]:
        """获取所有材料"""
        return list(self.materials.values())
    
    def add_material(self, material: Material):
        """添加材料"""
        self.materials[material.name] = material
    
    def remove_material(self, name: str) -> bool:
        """删除材料"""
        if name in self.materials:
            del self.materials[name]
            return True
        return False
    
    def get_material_names(self) -> List[str]:
        """获取所有材料名称"""
        return list(self.materials.keys())
    
    def get_categories(self) -> List[str]:
        """获取所有材料类别"""
        categories = set(mat.category for mat in self.materials.values())
        return sorted(list(categories))

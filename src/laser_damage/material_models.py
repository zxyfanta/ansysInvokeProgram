"""
激光毁伤仿真 - 材料模型

定义材料属性和温度相关的材料行为。
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

class MaterialModel:
    """材料模型类"""
    
    def __init__(self, material_data):
        """初始化材料模型"""
        self.name = material_data.name
        self.density = material_data.density
        self.thermal_conductivity = material_data.thermal_conductivity
        self.specific_heat = material_data.specific_heat
        self.melting_point = material_data.melting_point
        self.boiling_point = material_data.boiling_point
        self.absorptivity = material_data.absorptivity
        self.youngs_modulus = material_data.youngs_modulus
        self.poissons_ratio = material_data.poissons_ratio
        self.thermal_expansion = material_data.thermal_expansion
        self.yield_strength = material_data.yield_strength
        
        # 温度相关属性表
        self.temperature_dependent_properties = {}
        self._initialize_temperature_dependencies()
    
    def _initialize_temperature_dependencies(self):
        """初始化温度相关属性"""
        # 定义温度点
        temperatures = np.array([273, 373, 573, 773, 973, 1173, 1373, 1573])
        
        # 热导率随温度变化（一般随温度升高而降低）
        k_factors = np.array([1.0, 0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35])
        thermal_conductivity_curve = self.thermal_conductivity * k_factors
        
        # 比热容随温度变化（一般随温度升高而增加）
        c_factors = np.array([1.0, 1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65])
        specific_heat_curve = self.specific_heat * c_factors
        
        # 杨氏模量随温度变化（随温度升高而降低）
        e_factors = np.array([1.0, 0.98, 0.92, 0.85, 0.75, 0.60, 0.40, 0.20])
        youngs_modulus_curve = self.youngs_modulus * e_factors
        
        # 屈服强度随温度变化（随温度升高而降低）
        y_factors = np.array([1.0, 0.95, 0.85, 0.70, 0.50, 0.30, 0.15, 0.05])
        yield_strength_curve = self.yield_strength * y_factors
        
        # 存储温度相关属性
        self.temperature_dependent_properties = {
            'temperature': temperatures,
            'thermal_conductivity': thermal_conductivity_curve,
            'specific_heat': specific_heat_curve,
            'youngs_modulus': youngs_modulus_curve,
            'yield_strength': yield_strength_curve
        }
    
    def get_thermal_conductivity(self, temperature: float) -> float:
        """获取指定温度下的热导率"""
        return self._interpolate_property('thermal_conductivity', temperature)
    
    def get_specific_heat(self, temperature: float) -> float:
        """获取指定温度下的比热容"""
        return self._interpolate_property('specific_heat', temperature)
    
    def get_youngs_modulus(self, temperature: float) -> float:
        """获取指定温度下的杨氏模量"""
        return self._interpolate_property('youngs_modulus', temperature)
    
    def get_yield_strength(self, temperature: float) -> float:
        """获取指定温度下的屈服强度"""
        return self._interpolate_property('yield_strength', temperature)
    
    def _interpolate_property(self, property_name: str, temperature: float) -> float:
        """插值计算材料属性"""
        if property_name not in self.temperature_dependent_properties:
            # 如果没有温度相关数据，返回常温值
            return getattr(self, property_name, 0.0)
        
        temps = self.temperature_dependent_properties['temperature']
        values = self.temperature_dependent_properties[property_name]
        
        # 线性插值
        return np.interp(temperature, temps, values)
    
    def is_melted(self, temperature: float) -> bool:
        """判断材料是否熔化"""
        return temperature >= self.melting_point
    
    def is_vaporized(self, temperature: float) -> bool:
        """判断材料是否汽化"""
        return temperature >= self.boiling_point
    
    def get_phase_state(self, temperature: float) -> str:
        """获取材料相态"""
        if temperature < self.melting_point:
            return "solid"
        elif temperature < self.boiling_point:
            return "liquid"
        else:
            return "gas"
    
    def get_damage_threshold(self, damage_type: str = "thermal") -> float:
        """获取毁伤阈值"""
        if damage_type == "thermal":
            return self.melting_point
        elif damage_type == "mechanical":
            return self.yield_strength
        else:
            return 0.0
    
    def calculate_thermal_diffusivity(self, temperature: float) -> float:
        """计算热扩散率"""
        k = self.get_thermal_conductivity(temperature)
        c = self.get_specific_heat(temperature)
        rho = self.density
        
        return k / (rho * c)
    
    def calculate_thermal_shock_resistance(self, temperature: float) -> float:
        """计算热冲击阻力"""
        sigma_y = self.get_yield_strength(temperature)
        k = self.get_thermal_conductivity(temperature)
        alpha = self.thermal_expansion
        E = self.get_youngs_modulus(temperature)
        
        # 热冲击阻力参数
        if alpha > 0 and E > 0:
            return sigma_y * k / (alpha * E)
        else:
            return 0.0
    
    def get_material_properties_at_temperature(self, temperature: float) -> Dict[str, float]:
        """获取指定温度下的所有材料属性"""
        return {
            'temperature': temperature,
            'density': self.density,
            'thermal_conductivity': self.get_thermal_conductivity(temperature),
            'specific_heat': self.get_specific_heat(temperature),
            'youngs_modulus': self.get_youngs_modulus(temperature),
            'poissons_ratio': self.poissons_ratio,
            'thermal_expansion': self.thermal_expansion,
            'yield_strength': self.get_yield_strength(temperature),
            'melting_point': self.melting_point,
            'boiling_point': self.boiling_point,
            'absorptivity': self.absorptivity,
            'phase_state': self.get_phase_state(temperature),
            'thermal_diffusivity': self.calculate_thermal_diffusivity(temperature),
            'thermal_shock_resistance': self.calculate_thermal_shock_resistance(temperature)
        }
    
    def export_temperature_table(self, temp_range: Tuple[float, float], num_points: int = 50) -> Dict[str, np.ndarray]:
        """导出温度-属性对照表"""
        temp_min, temp_max = temp_range
        temperatures = np.linspace(temp_min, temp_max, num_points)
        
        table = {
            'temperature': temperatures,
            'thermal_conductivity': np.array([self.get_thermal_conductivity(T) for T in temperatures]),
            'specific_heat': np.array([self.get_specific_heat(T) for T in temperatures]),
            'youngs_modulus': np.array([self.get_youngs_modulus(T) for T in temperatures]),
            'yield_strength': np.array([self.get_yield_strength(T) for T in temperatures]),
            'thermal_diffusivity': np.array([self.calculate_thermal_diffusivity(T) for T in temperatures])
        }
        
        return table
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"MaterialModel({self.name})"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"MaterialModel(name='{self.name}', "
                f"density={self.density}, "
                f"thermal_conductivity={self.thermal_conductivity}, "
                f"melting_point={self.melting_point})")


class CompositeMaterialModel(MaterialModel):
    """复合材料模型"""
    
    def __init__(self, material_data, fiber_volume_fraction: float = 0.6):
        super().__init__(material_data)
        self.fiber_volume_fraction = fiber_volume_fraction
        self.matrix_volume_fraction = 1.0 - fiber_volume_fraction
        
        # 复合材料特有属性
        self.fiber_properties = {}
        self.matrix_properties = {}
        self._initialize_composite_properties()
    
    def _initialize_composite_properties(self):
        """初始化复合材料属性"""
        # 这里可以根据具体的复合材料类型设置纤维和基体的属性
        # 简化处理，使用混合法则
        pass
    
    def calculate_effective_properties(self) -> Dict[str, float]:
        """计算有效属性（混合法则）"""
        # 简化的混合法则计算
        Vf = self.fiber_volume_fraction
        Vm = self.matrix_volume_fraction
        
        # 这里需要根据具体的纤维和基体属性计算
        # 简化处理，返回当前属性
        return self.get_material_properties_at_temperature(293.15)

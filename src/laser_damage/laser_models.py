"""
激光毁伤仿真 - 激光模型

定义激光参数和激光束特性。
"""

import numpy as np
import math
from typing import Dict, List, Optional, Tuple
from enum import Enum

class BeamProfile(Enum):
    """光束轮廓类型"""
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    SUPER_GAUSSIAN = "super_gaussian"
    DONUT = "donut"

class LaserModel:
    """激光模型类"""
    
    def __init__(self, laser_params):
        """初始化激光模型"""
        self.power = laser_params.power
        self.wavelength = laser_params.wavelength
        self.beam_diameter = laser_params.beam_diameter
        self.pulse_duration = laser_params.pulse_duration
        self.pulse_frequency = laser_params.pulse_frequency
        self.laser_type = laser_params.laser_type
        self.beam_quality = laser_params.beam_quality
        self.divergence_angle = laser_params.divergence_angle
        
        # 光束轮廓参数
        self.beam_profile = BeamProfile.GAUSSIAN
        self.super_gaussian_order = 2
        
        # 计算派生参数
        self.beam_radius = self.beam_diameter / 2
        self.beam_area = math.pi * self.beam_radius ** 2
        self.power_density = self.power / self.beam_area
        
        # 时间相关参数
        self.duty_cycle = 1.0  # 连续激光的占空比为1
        if self.laser_type.value == "pulsed" and self.pulse_frequency > 0:
            self.duty_cycle = self.pulse_duration * self.pulse_frequency
    
    def get_power_density(self, r: float = 0.0) -> float:
        """获取指定半径处的功率密度"""
        if self.beam_profile == BeamProfile.GAUSSIAN:
            return self._gaussian_power_density(r)
        elif self.beam_profile == BeamProfile.UNIFORM:
            return self._uniform_power_density(r)
        elif self.beam_profile == BeamProfile.SUPER_GAUSSIAN:
            return self._super_gaussian_power_density(r)
        else:
            return self.power_density
    
    def _gaussian_power_density(self, r: float) -> float:
        """高斯光束功率密度分布"""
        # 高斯光束：I(r) = I0 * exp(-2*r^2/w^2)
        # 其中w是光束腰半径，I0是中心功率密度
        w = self.beam_radius / math.sqrt(2)  # 1/e^2半径转换为光束腰半径
        I0 = 2 * self.power / (math.pi * w**2)
        
        return I0 * math.exp(-2 * r**2 / w**2)
    
    def _uniform_power_density(self, r: float) -> float:
        """均匀光束功率密度分布"""
        if r <= self.beam_radius:
            return self.power_density
        else:
            return 0.0
    
    def _super_gaussian_power_density(self, r: float) -> float:
        """超高斯光束功率密度分布"""
        # 超高斯：I(r) = I0 * exp(-(r/w)^(2*n))
        w = self.beam_radius
        n = self.super_gaussian_order
        
        # 归一化常数
        from scipy.special import gamma
        I0 = self.power * n / (math.pi * w**2 * gamma(1/n))
        
        return I0 * math.exp(-(r/w)**(2*n))
    
    def get_temporal_profile(self, t: float) -> float:
        """获取时间轮廓"""
        if self.laser_type.value == "continuous":
            return 1.0
        elif self.laser_type.value == "pulsed":
            return self._pulsed_temporal_profile(t)
        elif self.laser_type.value == "quasi_continuous":
            return self._quasi_continuous_temporal_profile(t)
        else:
            return 1.0
    
    def _pulsed_temporal_profile(self, t: float) -> float:
        """脉冲激光时间轮廓"""
        if self.pulse_frequency <= 0:
            return 0.0
        
        period = 1.0 / self.pulse_frequency
        t_mod = t % period
        
        if t_mod <= self.pulse_duration:
            # 简化为矩形脉冲
            return 1.0
        else:
            return 0.0
    
    def _quasi_continuous_temporal_profile(self, t: float) -> float:
        """准连续激光时间轮廓"""
        # 简化处理，类似脉冲但占空比更高
        return self._pulsed_temporal_profile(t)
    
    def get_power_at_time_and_position(self, t: float, r: float) -> float:
        """获取指定时间和位置的功率密度"""
        spatial_factor = self.get_power_density(r) / self.power_density
        temporal_factor = self.get_temporal_profile(t)
        
        return self.power_density * spatial_factor * temporal_factor
    
    def calculate_energy_density(self, exposure_time: float, r: float = 0.0) -> float:
        """计算能量密度"""
        if self.laser_type.value == "continuous":
            return self.get_power_density(r) * exposure_time
        elif self.laser_type.value == "pulsed":
            # 计算在曝光时间内的脉冲数
            num_pulses = int(exposure_time * self.pulse_frequency)
            energy_per_pulse = self.power * self.pulse_duration
            total_energy = num_pulses * energy_per_pulse
            
            # 考虑空间分布
            spatial_factor = self.get_power_density(r) / self.power_density
            return (total_energy / self.beam_area) * spatial_factor
        else:
            return self.get_power_density(r) * exposure_time * self.duty_cycle
    
    def get_beam_parameters(self) -> Dict[str, float]:
        """获取光束参数"""
        return {
            'power': self.power,
            'wavelength': self.wavelength,
            'beam_diameter': self.beam_diameter,
            'beam_radius': self.beam_radius,
            'beam_area': self.beam_area,
            'power_density': self.power_density,
            'beam_quality': self.beam_quality,
            'divergence_angle': self.divergence_angle,
            'duty_cycle': self.duty_cycle
        }
    
    def calculate_rayleigh_range(self) -> float:
        """计算瑞利长度"""
        # 瑞利长度：zR = π*w0^2/λ
        w0 = self.beam_radius / math.sqrt(2)  # 光束腰半径
        wavelength_m = self.wavelength * 1e-9  # 转换为米
        
        return math.pi * w0**2 / wavelength_m
    
    def calculate_beam_divergence(self) -> float:
        """计算光束发散角"""
        if self.divergence_angle > 0:
            return self.divergence_angle
        else:
            # 根据衍射极限计算
            wavelength_m = self.wavelength * 1e-9
            return wavelength_m / (math.pi * self.beam_radius) * 1000  # 转换为mrad
    
    def calculate_focused_spot_size(self, focal_length: float, input_beam_diameter: float = None) -> float:
        """计算聚焦光斑尺寸"""
        if input_beam_diameter is None:
            input_beam_diameter = self.beam_diameter
        
        wavelength_m = self.wavelength * 1e-9
        
        # 衍射极限光斑尺寸
        spot_diameter = 4 * wavelength_m * focal_length / (math.pi * input_beam_diameter)
        
        # 考虑光束质量因子
        return spot_diameter * self.beam_quality
    
    def get_power_distribution_2d(self, x_range: Tuple[float, float], y_range: Tuple[float, float], 
                                 resolution: int = 100) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """获取2D功率密度分布"""
        x_min, x_max = x_range
        y_min, y_max = y_range
        
        x = np.linspace(x_min, x_max, resolution)
        y = np.linspace(y_min, y_max, resolution)
        X, Y = np.meshgrid(x, y)
        
        # 计算每个点到中心的距离
        R = np.sqrt(X**2 + Y**2)
        
        # 计算功率密度分布
        Z = np.zeros_like(R)
        for i in range(resolution):
            for j in range(resolution):
                Z[i, j] = self.get_power_density(R[i, j])
        
        return X, Y, Z
    
    def calculate_absorption_efficiency(self, material_absorptivity: float, 
                                      incident_angle: float = 0.0) -> float:
        """计算吸收效率"""
        # 考虑入射角的影响
        angle_factor = math.cos(math.radians(incident_angle))
        
        # 简化的吸收效率计算
        return material_absorptivity * angle_factor
    
    def estimate_damage_threshold(self, material_properties: Dict) -> Dict[str, float]:
        """估算毁伤阈值"""
        thresholds = {}
        
        # 热毁伤阈值（基于熔点）
        if 'melting_point' in material_properties and 'absorptivity' in material_properties:
            melting_point = material_properties['melting_point']
            absorptivity = material_properties['absorptivity']
            
            # 简化的热毁伤阈值计算
            # 假设材料从室温加热到熔点所需的能量密度
            if 'specific_heat' in material_properties and 'density' in material_properties:
                c = material_properties['specific_heat']
                rho = material_properties['density']
                delta_T = melting_point - 293.15  # 温升
                
                energy_density_threshold = rho * c * delta_T / absorptivity
                thresholds['thermal_damage'] = energy_density_threshold
        
        # 机械毁伤阈值（基于热应力）
        if 'yield_strength' in material_properties:
            thresholds['mechanical_damage'] = material_properties['yield_strength']
        
        return thresholds
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"LaserModel(power={self.power}W, wavelength={self.wavelength}nm)"
    
    def __repr__(self) -> str:
        """详细字符串表示"""
        return (f"LaserModel(power={self.power}, wavelength={self.wavelength}, "
                f"beam_diameter={self.beam_diameter}, type={self.laser_type.value})")

"""
激光配置模块

定义激光参数配置类。
"""

from typing import Dict, Any, Optional
from ..core.data_models import LaserConfiguration


class LaserConfig:
    """激光配置管理类"""
    
    def __init__(self):
        """初始化激光配置"""
        self.config = LaserConfiguration()
    
    def set_power(self, power: float) -> None:
        """设置激光功率"""
        self.config.power = power
    
    def set_wavelength(self, wavelength: float) -> None:
        """设置激光波长"""
        self.config.wavelength = wavelength
    
    def set_beam_diameter(self, diameter: float) -> None:
        """设置光斑直径"""
        self.config.beam_diameter = diameter
    
    def get_config(self) -> LaserConfiguration:
        """获取配置"""
        return self.config
    
    def validate(self) -> bool:
        """验证配置"""
        return self.config.validate()

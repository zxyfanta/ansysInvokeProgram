"""
激光毁伤效能分析软件 - 异常定义

定义软件中使用的各种异常类型。
"""

class LaserDamageError(Exception):
    """激光毁伤分析基础异常"""
    pass

class ANSYSConnectionError(LaserDamageError):
    """ANSYS连接异常"""
    pass

class SimulationError(LaserDamageError):
    """仿真计算异常"""
    pass

class DataProcessingError(LaserDamageError):
    """数据处理异常"""
    pass

class MaterialError(LaserDamageError):
    """材料数据异常"""
    pass

class GeometryError(LaserDamageError):
    """几何模型异常"""
    pass

class ConvergenceError(SimulationError):
    """收敛性异常"""
    pass

class LicenseError(ANSYSConnectionError):
    """许可证异常"""
    pass

class ConfigurationError(LaserDamageError):
    """配置异常"""
    pass

class ValidationError(LaserDamageError):
    """验证异常"""
    pass

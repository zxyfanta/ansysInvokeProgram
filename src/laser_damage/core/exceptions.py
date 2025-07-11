"""
自定义异常类

定义系统中使用的各种异常类型。
"""

from typing import Optional


class LaserSimulationError(Exception):
    """激光仿真系统基础异常类"""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class SimulationError(LaserSimulationError):
    """仿真执行异常"""
    pass


class LicenseError(LaserSimulationError):
    """ANSYS许可证相关异常"""
    pass


class ModelError(LaserSimulationError):
    """模型加载和处理异常"""
    pass


class ConfigurationError(LaserSimulationError):
    """配置参数异常"""
    pass


class DataProcessingError(LaserSimulationError):
    """数据处理异常"""
    pass


class AnsysIntegrationError(LaserSimulationError):
    """ANSYS集成异常"""
    pass


class ValidationError(LaserSimulationError):
    """参数验证异常"""
    pass


class FileOperationError(LaserSimulationError):
    """文件操作异常"""
    pass


class DatabaseError(LaserSimulationError):
    """数据库操作异常"""
    pass


class ReportGenerationError(LaserSimulationError):
    """报告生成异常"""
    pass


# 异常映射字典，用于错误码到异常类的映射
EXCEPTION_MAP = {
    "SIM_001": SimulationError,
    "LIC_001": LicenseError,
    "MOD_001": ModelError,
    "CFG_001": ConfigurationError,
    "DAT_001": DataProcessingError,
    "ANS_001": AnsysIntegrationError,
    "VAL_001": ValidationError,
    "FIL_001": FileOperationError,
    "DB_001": DatabaseError,
    "RPT_001": ReportGenerationError,
}


def create_exception(error_code: str, message: str) -> LaserSimulationError:
    """
    根据错误码创建对应的异常实例
    
    Args:
        error_code: 错误码
        message: 错误消息
        
    Returns:
        对应的异常实例
    """
    exception_class = EXCEPTION_MAP.get(error_code, LaserSimulationError)
    return exception_class(message, error_code)

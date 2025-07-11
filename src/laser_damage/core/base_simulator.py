"""
基础仿真器类

提供所有仿真模块的基础功能和通用接口。
"""

import os
import uuid
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from .data_models import SimulationResult, SimulationStatus
from .exceptions import SimulationError, ModelError, ConfigurationError


class BaseSimulator(ABC):
    """基础仿真器抽象类"""
    
    def __init__(self, working_directory: Optional[str] = None):
        """
        初始化基础仿真器
        
        Args:
            working_directory: 工作目录路径
        """
        self.simulation_id = str(uuid.uuid4())
        self.working_directory = Path(working_directory or "./simulation_work")
        self.working_directory.mkdir(parents=True, exist_ok=True)
        
        # 设置日志
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # 仿真状态
        self.status = SimulationStatus.PENDING
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # 配置和结果
        self.configuration: Dict[str, Any] = {}
        self.result: Optional[SimulationResult] = None
        
        # 文件管理
        self.input_files: List[str] = []
        self.output_files: List[str] = []
        self.temp_files: List[str] = []
        
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        验证配置参数
        
        Args:
            config: 配置参数字典
            
        Returns:
            验证是否通过
            
        Raises:
            ConfigurationError: 配置参数无效
        """
        pass
    
    @abstractmethod
    def prepare_simulation(self) -> bool:
        """
        准备仿真环境
        
        Returns:
            准备是否成功
            
        Raises:
            SimulationError: 准备失败
        """
        pass
    
    @abstractmethod
    def execute_simulation(self) -> SimulationResult:
        """
        执行仿真计算
        
        Returns:
            仿真结果
            
        Raises:
            SimulationError: 仿真执行失败
        """
        pass
    
    @abstractmethod
    def post_process_results(self) -> bool:
        """
        后处理仿真结果
        
        Returns:
            后处理是否成功
        """
        pass
    
    def run_simulation(self, config: Dict[str, Any]) -> SimulationResult:
        """
        运行完整仿真流程
        
        Args:
            config: 仿真配置参数
            
        Returns:
            仿真结果
            
        Raises:
            SimulationError: 仿真失败
        """
        try:
            self.logger.info(f"开始仿真 {self.simulation_id}")
            self.start_time = datetime.now()
            self.status = SimulationStatus.RUNNING
            
            # 1. 验证配置
            self.logger.info("验证配置参数...")
            if not self.validate_configuration(config):
                raise ConfigurationError("配置参数验证失败")
            self.configuration = config.copy()
            
            # 2. 准备仿真
            self.logger.info("准备仿真环境...")
            if not self.prepare_simulation():
                raise SimulationError("仿真环境准备失败")
            
            # 3. 执行仿真
            self.logger.info("执行仿真计算...")
            self.result = self.execute_simulation()
            
            # 4. 后处理
            self.logger.info("后处理结果...")
            if not self.post_process_results():
                self.logger.warning("后处理失败，但仿真结果可用")
            
            # 5. 完成
            self.end_time = datetime.now()
            self.status = SimulationStatus.COMPLETED
            
            if self.result:
                self.result.status = self.status
                self.result.computation_time = (
                    self.end_time - self.start_time
                ).total_seconds()
            
            self.logger.info(f"仿真完成 {self.simulation_id}")
            return self.result
            
        except Exception as e:
            self.status = SimulationStatus.FAILED
            self.end_time = datetime.now()
            self.logger.error(f"仿真失败: {str(e)}")
            raise SimulationError(f"仿真执行失败: {str(e)}")
    
    def load_model(self, model_path: str) -> bool:
        """
        加载3D模型
        
        Args:
            model_path: 模型文件路径
            
        Returns:
            加载是否成功
            
        Raises:
            ModelError: 模型加载失败
        """
        model_file = Path(model_path)
        if not model_file.exists():
            raise ModelError(f"模型文件不存在: {model_path}")
        
        # 检查文件格式
        supported_formats = ['.step', '.stp', '.iges', '.igs', '.sat', '.x_t']
        if model_file.suffix.lower() not in supported_formats:
            raise ModelError(f"不支持的模型格式: {model_file.suffix}")
        
        self.input_files.append(str(model_file.absolute()))
        self.logger.info(f"模型加载成功: {model_path}")
        return True
    
    def cleanup_temp_files(self) -> None:
        """清理临时文件"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    self.logger.debug(f"删除临时文件: {temp_file}")
            except Exception as e:
                self.logger.warning(f"删除临时文件失败 {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def get_simulation_info(self) -> Dict[str, Any]:
        """
        获取仿真信息
        
        Returns:
            仿真信息字典
        """
        return {
            "simulation_id": self.simulation_id,
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "working_directory": str(self.working_directory),
            "input_files": self.input_files,
            "output_files": self.output_files,
            "configuration": self.configuration,
        }
    
    def save_configuration(self, config_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径
        """
        import json
        
        config_data = {
            "simulation_info": self.get_simulation_info(),
            "configuration": self.configuration,
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"配置已保存到: {config_path}")
    
    def load_configuration(self, config_path: str) -> Dict[str, Any]:
        """
        从文件加载配置
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置参数字典
        """
        import json
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        self.configuration = config_data.get("configuration", {})
        self.logger.info(f"配置已从文件加载: {config_path}")
        
        return self.configuration
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口，自动清理资源"""
        self.cleanup_temp_files()
        
        if exc_type is not None:
            self.status = SimulationStatus.FAILED
            self.logger.error(f"仿真异常退出: {exc_val}")
        
        return False  # 不抑制异常

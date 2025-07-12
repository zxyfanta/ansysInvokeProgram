"""
激光毁伤效能分析软件 - 基础仿真器

提供所有仿真模块的基础类和通用功能。
"""

import os
import sys
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pathlib import Path
import uuid
from datetime import datetime

# 添加配置路径
sys.path.append(str(Path(__file__).parent.parent.parent))
from config import get_ansys_config, get_system_config

from .data_models import SimulationData, SimulationStatus
from .exceptions import (
    LaserDamageError, ANSYSConnectionError, 
    SimulationError, ConfigurationError
)

class BaseSimulator(ABC):
    """基础仿真器抽象类"""
    
    def __init__(self, name: str = "BaseSimulator"):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # 配置管理
        self.system_config = get_system_config()
        self.ansys_config = get_ansys_config()
        
        # 仿真状态
        self.is_initialized = False
        self.is_running = False
        self.current_simulation: Optional[SimulationData] = None
        
        # 工作目录
        self.working_directory = self.system_config.get_working_directory()
        self.temp_directory = self.system_config.get_temp_directory()
        
        # 初始化
        self._initialize()
    
    def _initialize(self):
        """初始化仿真器"""
        try:
            # 检查ANSYS可用性
            if not self.ansys_config.ansys_path:
                raise ANSYSConnectionError("ANSYS未正确安装或配置")
            
            # 设置ANSYS环境
            self.ansys_config.setup_environment()
            
            # 创建工作目录
            Path(self.working_directory).mkdir(parents=True, exist_ok=True)
            Path(self.temp_directory).mkdir(parents=True, exist_ok=True)
            
            self.is_initialized = True
            self.logger.info(f"{self.name} 初始化成功")
            
        except Exception as e:
            self.logger.error(f"{self.name} 初始化失败: {e}")
            raise ConfigurationError(f"仿真器初始化失败: {e}")
    
    @abstractmethod
    def setup_simulation(self, simulation_data: SimulationData) -> bool:
        """设置仿真参数"""
        pass
    
    @abstractmethod
    def run_simulation(self) -> bool:
        """运行仿真"""
        pass
    
    @abstractmethod
    def get_results(self) -> Dict[str, Any]:
        """获取仿真结果"""
        pass
    
    def validate_input(self, simulation_data: SimulationData) -> bool:
        """验证输入数据"""
        try:
            # 基础验证
            if not simulation_data.laser_params:
                raise ValueError("激光参数不能为空")
            
            if not simulation_data.material_data:
                raise ValueError("材料数据不能为空")
            
            if not simulation_data.geometry_data:
                raise ValueError("几何数据不能为空")
            
            # 激光参数验证
            if simulation_data.laser_params.power <= 0:
                raise ValueError("激光功率必须大于0")
            
            if simulation_data.laser_params.beam_diameter <= 0:
                raise ValueError("光斑直径必须大于0")
            
            # 材料参数验证
            if simulation_data.material_data.density <= 0:
                raise ValueError("材料密度必须大于0")
            
            if simulation_data.material_data.thermal_conductivity <= 0:
                raise ValueError("热导率必须大于0")
            
            return True
            
        except Exception as e:
            self.logger.error(f"输入验证失败: {e}")
            return False
    
    def create_simulation(self, **kwargs) -> SimulationData:
        """创建新的仿真数据"""
        simulation_id = str(uuid.uuid4())
        
        # 从kwargs中提取参数，这里需要根据实际需求完善
        simulation_data = SimulationData(
            simulation_id=simulation_id,
            name=kwargs.get('name', f'Simulation_{simulation_id[:8]}'),
            description=kwargs.get('description', ''),
            laser_params=kwargs['laser_params'],
            material_data=kwargs['material_data'],
            geometry_data=kwargs['geometry_data'],
            boundary_conditions=kwargs['boundary_conditions'],
            simulation_settings=kwargs['simulation_settings']
        )
        
        return simulation_data
    
    def start_simulation(self, simulation_data: SimulationData) -> bool:
        """启动仿真"""
        if not self.is_initialized:
            raise SimulationError("仿真器未初始化")
        
        if self.is_running:
            raise SimulationError("仿真正在运行中")
        
        try:
            # 验证输入
            if not self.validate_input(simulation_data):
                raise SimulationError("输入数据验证失败")
            
            # 设置当前仿真
            self.current_simulation = simulation_data
            self.current_simulation.status = SimulationStatus.RUNNING
            
            # 设置仿真
            if not self.setup_simulation(simulation_data):
                raise SimulationError("仿真设置失败")
            
            # 运行仿真
            self.is_running = True
            success = self.run_simulation()
            
            if success:
                self.current_simulation.status = SimulationStatus.COMPLETED
                self.logger.info("仿真完成")
            else:
                self.current_simulation.status = SimulationStatus.FAILED
                self.logger.error("仿真失败")
            
            return success
            
        except Exception as e:
            self.logger.error(f"仿真执行失败: {e}")
            if self.current_simulation:
                self.current_simulation.status = SimulationStatus.FAILED
            return False
        
        finally:
            self.is_running = False
    
    def stop_simulation(self):
        """停止仿真"""
        if self.is_running and self.current_simulation:
            self.current_simulation.status = SimulationStatus.CANCELLED
            self.is_running = False
            self.logger.info("仿真已停止")
    
    def get_simulation_status(self) -> SimulationStatus:
        """获取仿真状态"""
        if self.current_simulation:
            return self.current_simulation.status
        return SimulationStatus.PENDING
    
    def cleanup(self):
        """清理资源"""
        try:
            # 清理临时文件
            temp_path = Path(self.temp_directory)
            if temp_path.exists():
                for file in temp_path.glob("*"):
                    if file.is_file():
                        file.unlink()
            
            self.logger.info("资源清理完成")
            
        except Exception as e:
            self.logger.warning(f"资源清理失败: {e}")
    
    def save_results(self, output_path: str) -> bool:
        """保存仿真结果"""
        if not self.current_simulation:
            return False
        
        try:
            import json
            
            # 获取结果
            results = self.get_results()
            
            # 保存到文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"结果已保存到: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存结果失败: {e}")
            return False
    
    def get_working_file_path(self, filename: str) -> str:
        """获取工作文件路径"""
        return str(Path(self.working_directory) / filename)
    
    def get_temp_file_path(self, filename: str) -> str:
        """获取临时文件路径"""
        return str(Path(self.temp_directory) / filename)
    
    def log_info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def log_warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def log_error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)

    def get_current_time(self) -> str:
        """获取当前时间字符串"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()

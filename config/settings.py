"""
激光毁伤效能分析软件 - 系统配置

管理软件的全局配置参数。
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

# 默认配置
DEFAULT_CONFIG = {
    "system": {
        "name": "激光毁伤效能分析软件",
        "version": "1.0.0",
        "author": "激光毁伤效能分析软件开发团队",
        "debug": False,
        "log_level": "INFO"
    },
    "ansys": {
        "version": "2021R1",
        "install_path": "D:/Program Files/ANSYS Inc/v211",
        "license_server": "",
        "working_directory": "./ansys_work",
        "temp_directory": "./temp"
    },
    "simulation": {
        "default_solver": "thermal",
        "max_iterations": 1000,
        "convergence_tolerance": 1e-6,
        "parallel_cores": 4
    },
    "gui": {
        "theme": "default",
        "language": "zh_CN",
        "window_size": [1400, 900],
        "auto_save": True,
        "auto_save_interval": 300  # 秒
    },
    "output": {
        "default_format": "pdf",
        "image_dpi": 300,
        "chart_style": "professional",
        "report_template": "standard"
    }
}

class SystemConfig:
    """系统配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "config.yml"
        self.config = DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    if user_config:
                        self._merge_config(self.config, user_config)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                print("使用默认配置")
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def _merge_config(self, base: Dict, update: Dict):
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def get_ansys_path(self) -> str:
        """获取ANSYS安装路径"""
        return self.get('ansys.install_path', '')
    
    def get_working_directory(self) -> str:
        """获取工作目录"""
        work_dir = self.get('ansys.working_directory', './ansys_work')
        Path(work_dir).mkdir(parents=True, exist_ok=True)
        return work_dir
    
    def get_temp_directory(self) -> str:
        """获取临时目录"""
        temp_dir = self.get('ansys.temp_directory', './temp')
        Path(temp_dir).mkdir(parents=True, exist_ok=True)
        return temp_dir
    
    def is_debug_mode(self) -> bool:
        """是否调试模式"""
        return self.get('system.debug', False)
    
    def get_log_level(self) -> str:
        """获取日志级别"""
        return self.get('system.log_level', 'INFO')


# 全局配置实例
_system_config = None

def get_system_config() -> SystemConfig:
    """获取系统配置实例"""
    global _system_config
    if _system_config is None:
        _system_config = SystemConfig()
    return _system_config

def reload_config():
    """重新加载配置"""
    global _system_config
    _system_config = None
    return get_system_config()

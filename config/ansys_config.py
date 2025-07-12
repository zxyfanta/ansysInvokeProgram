"""
激光毁伤效能分析软件 - ANSYS配置

管理ANSYS 2021 R1的配置和连接。
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

# ANSYS 2021 R1 默认安装路径
DEFAULT_ANSYS_PATHS = [
    "D:/Program Files/ANSYS Inc/v211",
    "C:/Program Files/ANSYS Inc/v211", 
    "D:/ANSYS Inc/v211",
    "C:/ANSYS Inc/v211"
]

class ANSYSConfig:
    """ANSYS配置管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ansys_path = None
        self.version = "2021R1"
        self.license_server = None
        self.working_directory = "./ansys_work"
        
        # 自动检测ANSYS安装
        self.detect_ansys_installation()
    
    def detect_ansys_installation(self) -> bool:
        """自动检测ANSYS安装"""
        self.logger.info("检测ANSYS 2021 R1安装...")
        
        # 检查默认路径
        for path in DEFAULT_ANSYS_PATHS:
            if self.validate_ansys_path(path):
                self.ansys_path = path
                self.logger.info(f"找到ANSYS安装: {path}")
                return True
        
        # 检查环境变量
        ansys_env = os.environ.get('ANSYS211_DIR')
        if ansys_env and self.validate_ansys_path(ansys_env):
            self.ansys_path = ansys_env
            self.logger.info(f"从环境变量找到ANSYS: {ansys_env}")
            return True
        
        self.logger.warning("未找到ANSYS 2021 R1安装")
        return False
    
    def validate_ansys_path(self, path: str) -> bool:
        """验证ANSYS安装路径"""
        if not path or not os.path.exists(path):
            return False
        
        # 检查关键文件
        key_files = [
            "ansys/bin/winx64/ansys211.exe",
            "fluent/bin/fluent.exe", 
            "Framework/bin/Linux64/runwb2"
        ]
        
        for file_path in key_files:
            full_path = Path(path) / file_path
            if full_path.exists():
                return True
        
        return False
    
    def get_ansys_executable(self, product: str = "mechanical") -> Optional[str]:
        """获取ANSYS产品可执行文件路径"""
        if not self.ansys_path:
            return None
        
        executables = {
            "mechanical": "ansys/bin/winx64/ansys211.exe",
            "fluent": "fluent/bin/fluent.exe",
            "workbench": "Framework/bin/Linux64/runwb2",
            "cfx": "CFX/bin/cfx5solve.exe"
        }
        
        if product not in executables:
            return None
        
        exe_path = Path(self.ansys_path) / executables[product]
        return str(exe_path) if exe_path.exists() else None
    
    def setup_environment(self):
        """设置ANSYS环境变量"""
        if not self.ansys_path:
            return False
        
        # 设置环境变量
        os.environ['ANSYS211_DIR'] = self.ansys_path
        os.environ['AWP_ROOT211'] = self.ansys_path
        
        # 添加到PATH
        ansys_bin = str(Path(self.ansys_path) / "ansys" / "bin" / "winx64")
        fluent_bin = str(Path(self.ansys_path) / "fluent" / "bin")
        
        current_path = os.environ.get('PATH', '')
        if ansys_bin not in current_path:
            os.environ['PATH'] = f"{ansys_bin};{current_path}"
        if fluent_bin not in current_path:
            os.environ['PATH'] = f"{fluent_bin};{os.environ['PATH']}"
        
        return True
    
    def get_pyansys_config(self) -> Dict:
        """获取PyANSYS配置"""
        config = {
            'ansys_path': self.ansys_path,
            'version': self.version,
            'working_directory': self.working_directory
        }
        
        if self.license_server:
            config['license_server'] = self.license_server
        
        return config
    
    def test_connection(self, product: str = "mechanical") -> Tuple[bool, str]:
        """测试ANSYS连接"""
        try:
            if product == "fluent":
                return self._test_fluent_connection()
            elif product == "mechanical":
                return self._test_mechanical_connection()
            else:
                return False, f"不支持的产品: {product}"
        except Exception as e:
            return False, f"连接测试失败: {str(e)}"
    
    def _test_fluent_connection(self) -> Tuple[bool, str]:
        """测试Fluent连接"""
        try:
            import ansys.fluent.core as pyfluent
            
            # 尝试启动Fluent会话
            session = pyfluent.launch_fluent(
                precision='double',
                processor_count=1,
                show_gui=False,
                mode='solver'
            )
            
            if session:
                session.exit()
                return True, "Fluent连接成功"
            else:
                return False, "Fluent会话启动失败"
                
        except ImportError:
            return False, "PyFluent未安装"
        except Exception as e:
            return False, f"Fluent连接失败: {str(e)}"
    
    def _test_mechanical_connection(self) -> Tuple[bool, str]:
        """测试Mechanical连接"""
        try:
            import ansys.mapdl.core as pymapdl
            
            # 尝试启动MAPDL会话
            mapdl = pymapdl.launch_mapdl(
                run_location=self.working_directory,
                nproc=1,
                override=True
            )
            
            if mapdl:
                mapdl.exit()
                return True, "Mechanical连接成功"
            else:
                return False, "MAPDL会话启动失败"
                
        except ImportError:
            return False, "PyMAPDL未安装"
        except Exception as e:
            return False, f"Mechanical连接失败: {str(e)}"


# 全局ANSYS配置实例
_ansys_config = None

def get_ansys_config() -> ANSYSConfig:
    """获取ANSYS配置实例"""
    global _ansys_config
    if _ansys_config is None:
        _ansys_config = ANSYSConfig()
    return _ansys_config

def is_ansys_available() -> bool:
    """检查ANSYS是否可用"""
    config = get_ansys_config()
    return config.ansys_path is not None

def setup_ansys_environment():
    """设置ANSYS环境"""
    config = get_ansys_config()
    return config.setup_environment()

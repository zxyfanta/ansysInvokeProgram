"""
ANSYS集成工具类

提供与ANSYS软件集成的各种工具函数和连接器。
"""

import os
import subprocess
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

# 暂时禁用ANSYS集成，用于界面测试
ANSYS_AVAILABLE = False
Mapdl = None

# try:
#     from ansys.mapdl.core import launch_mapdl, Mapdl
#     ANSYS_AVAILABLE = True
# except ImportError:
#     ANSYS_AVAILABLE = False
#     Mapdl = None

from ..core.exceptions import AnsysIntegrationError, LicenseError


class AnsysConnector:
    """ANSYS连接器类"""
    
    def __init__(self):
        """初始化ANSYS连接器"""
        self.logger = logging.getLogger(__name__)
        self.mapdl: Optional[Mapdl] = None
        self.ansys_root = os.environ.get('ANSYS_ROOT', '/opt/ansys_inc/v211')
        self.license_server = os.environ.get('ANSYSLMD_LICENSE_FILE', '1055@localhost')
        
        # 检查ANSYS安装
        if not ANSYS_AVAILABLE:
            self.logger.warning("PyMAPDL未安装，ANSYS功能将受限")
        
        if not Path(self.ansys_root).exists():
            self.logger.warning(f"ANSYS安装路径不存在: {self.ansys_root}")
    
    def test_connection(self) -> bool:
        """
        测试ANSYS连接

        Returns:
            连接是否成功
        """
        try:
            if not ANSYS_AVAILABLE:
                self.logger.warning("PyMAPDL未安装，使用模拟模式")
                # 模拟连接成功，用于界面测试
                return True

            # 测试许可证
            if not self._check_license():
                self.logger.error("ANSYS许可证检查失败")
                return False

            # 尝试启动MAPDL
            test_mapdl = launch_mapdl(
                exec_file=self._get_ansys_executable(),
                run_location=None,
                cleanup_on_exit=True,
                start_timeout=60,
                additional_switches='-smp'
            )

            if test_mapdl:
                version = test_mapdl.version
                self.logger.info(f"ANSYS连接成功，版本: {version}")
                test_mapdl.exit()
                return True
            else:
                self.logger.error("ANSYS启动失败")
                return False

        except Exception as e:
            self.logger.error(f"ANSYS连接测试失败: {e}")
            return False
    
    def launch_mapdl(self, 
                     working_dir: Optional[str] = None,
                     memory_limit: str = "16GB",
                     cpu_cores: int = 8) -> Optional[Mapdl]:
        """
        启动MAPDL实例
        
        Args:
            working_dir: 工作目录
            memory_limit: 内存限制
            cpu_cores: CPU核心数
            
        Returns:
            MAPDL实例
        """
        try:
            if not ANSYS_AVAILABLE:
                raise AnsysIntegrationError("PyMAPDL未安装")
            
            # 构建启动参数
            additional_switches = [
                '-smp',  # 共享内存并行
                f'-np {cpu_cores}',  # CPU核心数
                f'-m {memory_limit}',  # 内存限制
            ]
            
            self.mapdl = launch_mapdl(
                exec_file=self._get_ansys_executable(),
                run_location=working_dir,
                cleanup_on_exit=True,
                start_timeout=120,
                additional_switches=' '.join(additional_switches)
            )
            
            if self.mapdl:
                self.logger.info(f"MAPDL启动成功，工作目录: {self.mapdl.directory}")
                return self.mapdl
            else:
                raise AnsysIntegrationError("MAPDL启动失败")
                
        except Exception as e:
            self.logger.error(f"MAPDL启动失败: {e}")
            raise AnsysIntegrationError(f"MAPDL启动失败: {e}")
    
    def close_mapdl(self) -> None:
        """关闭MAPDL实例"""
        if self.mapdl:
            try:
                self.mapdl.exit()
                self.logger.info("MAPDL实例已关闭")
            except Exception as e:
                self.logger.warning(f"关闭MAPDL实例时出错: {e}")
            finally:
                self.mapdl = None
    
    def get_version(self) -> str:
        """
        获取ANSYS版本信息
        
        Returns:
            版本字符串
        """
        try:
            if self.mapdl:
                return str(self.mapdl.version)
            else:
                # 尝试从可执行文件获取版本
                executable = self._get_ansys_executable()
                result = subprocess.run(
                    [executable, '-v'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception as e:
            self.logger.warning(f"获取ANSYS版本失败: {e}")
            return "Unknown"
    
    def _get_ansys_executable(self) -> str:
        """
        获取ANSYS可执行文件路径
        
        Returns:
            可执行文件路径
        """
        if os.name == 'nt':  # Windows
            executable = Path(self.ansys_root) / 'ansys' / 'bin' / 'winx64' / 'ansys211.exe'
        else:  # Linux
            executable = Path(self.ansys_root) / 'ansys' / 'bin' / 'ansys211'
        
        if not executable.exists():
            raise AnsysIntegrationError(f"ANSYS可执行文件不存在: {executable}")
        
        return str(executable)
    
    def _check_license(self) -> bool:
        """
        检查ANSYS许可证
        
        Returns:
            许可证是否可用
        """
        try:
            # 检查许可证服务器环境变量
            if not self.license_server:
                self.logger.error("未设置ANSYS许可证服务器")
                return False
            
            # 尝试使用lmstat检查许可证状态
            lmstat_path = Path(self.ansys_root) / 'shared_files' / 'licensing'
            if os.name == 'nt':
                lmstat_exe = lmstat_path / 'winx64' / 'lmstat.exe'
            else:
                lmstat_exe = lmstat_path / 'linx64' / 'lmstat'
            
            if lmstat_exe.exists():
                result = subprocess.run(
                    [str(lmstat_exe), '-a', '-c', self.license_server],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.logger.info("ANSYS许可证检查通过")
                    return True
                else:
                    self.logger.error(f"许可证检查失败: {result.stderr}")
                    return False
            else:
                self.logger.warning("lmstat工具不存在，跳过许可证检查")
                return True  # 假设许可证可用
                
        except Exception as e:
            self.logger.error(f"许可证检查异常: {e}")
            return False
    
    def get_license_info(self) -> Dict[str, Any]:
        """
        获取许可证信息
        
        Returns:
            许可证信息字典
        """
        license_info = {
            'server': self.license_server,
            'status': 'unknown',
            'features': [],
            'users': 0,
        }
        
        try:
            # 这里可以添加更详细的许可证信息获取逻辑
            if self._check_license():
                license_info['status'] = 'available'
            else:
                license_info['status'] = 'unavailable'
                
        except Exception as e:
            self.logger.error(f"获取许可证信息失败: {e}")
            license_info['status'] = 'error'
            license_info['error'] = str(e)
        
        return license_info
    
    def execute_apdl_script(self, script_content: str) -> Dict[str, Any]:
        """
        执行APDL脚本
        
        Args:
            script_content: APDL脚本内容
            
        Returns:
            执行结果
        """
        if not self.mapdl:
            raise AnsysIntegrationError("MAPDL实例未启动")
        
        try:
            # 执行APDL命令
            output = self.mapdl.input(script_content)
            
            return {
                'success': True,
                'output': output,
                'error': None
            }
            
        except Exception as e:
            self.logger.error(f"APDL脚本执行失败: {e}")
            return {
                'success': False,
                'output': None,
                'error': str(e)
            }
    
    def load_geometry(self, geometry_file: str) -> bool:
        """
        加载几何模型
        
        Args:
            geometry_file: 几何文件路径
            
        Returns:
            加载是否成功
        """
        if not self.mapdl:
            raise AnsysIntegrationError("MAPDL实例未启动")
        
        try:
            geometry_path = Path(geometry_file)
            if not geometry_path.exists():
                raise FileNotFoundError(f"几何文件不存在: {geometry_file}")
            
            # 根据文件扩展名选择导入方法
            ext = geometry_path.suffix.lower()
            
            if ext in ['.step', '.stp']:
                self.mapdl.cdread('step', str(geometry_path))
            elif ext in ['.iges', '.igs']:
                self.mapdl.cdread('iges', str(geometry_path))
            elif ext == '.sat':
                self.mapdl.cdread('sat', str(geometry_path))
            else:
                raise ValueError(f"不支持的几何文件格式: {ext}")
            
            self.logger.info(f"几何模型加载成功: {geometry_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"几何模型加载失败: {e}")
            return False
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close_mapdl()
        return False

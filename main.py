#!/usr/bin/env python3
"""
激光毁伤效能分析软件 - 主程序入口

基于ANSYS 2021 R1的激光毁伤效能分析软件主程序。
"""

import sys
import os
import logging
from pathlib import Path
import argparse

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入配置
from config.settings import get_system_config
from config.ansys_config import get_ansys_config, setup_ansys_environment

# 导入核心模块
from src.core.data_models import (
    LaserParameters, MaterialData, GeometryData,
    BoundaryConditions, SimulationSettings, LaserType
)

def setup_logging():
    """设置日志系统"""
    config = get_system_config()
    log_level = config.get_log_level()
    
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('laser_damage_analysis.log', encoding='utf-8')
        ]
    )

def check_environment():
    """检查运行环境"""
    logger = logging.getLogger(__name__)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        logger.error("需要Python 3.8或更高版本")
        return False
    
    # 检查ANSYS配置
    ansys_config = get_ansys_config()
    if not ansys_config.ansys_path:
        logger.error("未找到ANSYS 2021 R1安装，请检查安装路径")
        return False
    
    # 设置ANSYS环境
    if not setup_ansys_environment():
        logger.warning("ANSYS环境设置失败，部分功能可能不可用")
    
    logger.info("环境检查完成")
    return True

def create_sample_simulation():
    """创建示例仿真"""
    # 激光参数
    laser_params = LaserParameters(
        power=1000.0,           # 1kW激光
        wavelength=1064.0,      # 1064nm波长
        beam_diameter=0.01,     # 10mm光斑直径
        laser_type=LaserType.CONTINUOUS
    )
    
    # 材料数据 - 铝合金
    material_data = MaterialData(
        name="铝合金2024-T3",
        density=2780.0,
        thermal_conductivity=121.0,
        specific_heat=875.0,
        melting_point=916.0,
        boiling_point=2740.0,
        absorptivity=0.15,
        youngs_modulus=73.1e9,
        poissons_ratio=0.33,
        thermal_expansion=22.3e-6,
        yield_strength=324e6
    )
    
    # 几何数据
    geometry_data = GeometryData(
        model_file="sample_target.step",
        dimensions=(0.1, 0.1, 0.02),  # 100x100x20mm
        volume=0.0002,                 # 0.2L
        surface_area=0.024,            # 240cm²
        mesh_size=0.002                # 2mm网格
    )
    
    # 边界条件
    boundary_conditions = BoundaryConditions(
        ambient_temperature=293.15,
        convection_coefficient=10.0,
        radiation_emissivity=0.8,
        fixed_constraints=["bottom_fixed"]
    )
    
    # 仿真设置
    simulation_settings = SimulationSettings(
        analysis_type="transient",
        time_step=0.01,
        total_time=5.0,
        max_iterations=1000,
        convergence_tolerance=1e-6,
        parallel_cores=4
    )
    
    return {
        'laser_params': laser_params,
        'material_data': material_data,
        'geometry_data': geometry_data,
        'boundary_conditions': boundary_conditions,
        'simulation_settings': simulation_settings
    }

def run_cli_simulation():
    """运行命令行仿真"""
    logger = logging.getLogger(__name__)

    try:
        logger.info("开始激光毁伤仿真...")

        # 使用新的激光毁伤分析程序
        print("🚀 启动激光毁伤效能分析软件...")

        # 运行新的主程序
        import subprocess
        import sys

        result = subprocess.run([
            sys.executable, "laser_damage_analysis.py", "--cli"
        ], capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("仿真完成成功")
            print(result.stdout)
            return True
        else:
            logger.error("仿真失败")
            print(result.stderr)
            return False

    except Exception as e:
        logger.error(f"仿真执行异常: {e}")
        return False

def run_gui():
    """启动GUI界面"""
    try:
        from src.gui.main_window import MainWindow, GUI_AVAILABLE

        if not GUI_AVAILABLE:
            print("GUI模块不可用，请检查PyQt5安装")
            return False

        from PyQt5.QtWidgets import QApplication

        app = QApplication(sys.argv)
        app.setApplicationName("激光毁伤效能分析软件")
        app.setApplicationVersion("1.0.0")

        # 创建主窗口
        window = MainWindow()
        window.show()

        return app.exec_()

    except ImportError as e:
        print(f"GUI启动失败: {e}")
        print("请安装PyQt5: pip install PyQt5")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="激光毁伤效能分析软件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py --gui                    # 启动GUI界面
  python main.py --cli                    # 运行命令行仿真
  python main.py --check                  # 检查环境配置
        """
    )
    
    parser.add_argument('--gui', action='store_true', 
                       help='启动图形用户界面')
    parser.add_argument('--cli', action='store_true',
                       help='运行命令行仿真')
    parser.add_argument('--check', action='store_true',
                       help='检查环境配置')
    parser.add_argument('--debug', action='store_true',
                       help='启用调试模式')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # 设置调试模式
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("调试模式已启用")
    
    logger.info("激光毁伤效能分析软件启动")
    
    # 检查环境
    if not check_environment():
        logger.error("环境检查失败，程序退出")
        return 1
    
    # 根据参数执行相应功能
    if args.check:
        logger.info("环境检查完成，所有组件正常")
        return 0
    elif args.cli:
        success = run_cli_simulation()
        return 0 if success else 1
    elif args.gui:
        return run_gui()
    else:
        # 默认启动GUI
        logger.info("未指定运行模式，启动GUI界面")
        return run_gui()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"程序异常退出: {e}")
        sys.exit(1)

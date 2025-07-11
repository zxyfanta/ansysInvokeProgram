#!/usr/bin/env python3
"""
激光毁伤仿真系统GUI启动脚本

运行此脚本启动图形用户界面。
"""

import sys
import os
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    # 检查是否使用优化版本
    import argparse
    parser = argparse.ArgumentParser(description='激光毁伤仿真系统')
    parser.add_argument('--optimized', action='store_true', help='使用优化版本GUI')
    args = parser.parse_args()

    if args.optimized:
        from laser_damage.gui.optimized_main_window import main
        print("正在启动激光毁伤仿真系统 (优化版本)...")
    else:
        from laser_damage.gui.main_window import main
        print("正在启动激光毁伤仿真系统...")

    if __name__ == '__main__':
        print("请确保已安装所需的依赖库：")
        print("- PyQt5")
        print("- matplotlib")
        print("- numpy")
        print("- pandas")
        print()

        if args.optimized:
            print("🚀 使用优化版本GUI界面")
            print("   - 简化的菜单结构")
            print("   - 集成的项目资源管理器")
            print("   - 改进的工作流程")
        print()

        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print()
    print("请确保已安装所需的依赖库：")
    print("pip install PyQt5 matplotlib numpy pandas")
    print()
    print("或者运行：")
    print("pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)

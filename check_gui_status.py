#!/usr/bin/env python3
"""
检查GUI运行状态
"""

import psutil
import sys
import time

def check_gui_process():
    """检查GUI进程是否在运行"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and 'run_gui.py' in ' '.join(cmdline):
                print(f"✅ GUI进程正在运行:")
                print(f"   PID: {proc.info['pid']}")
                print(f"   命令: {' '.join(cmdline)}")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print("❌ 未找到GUI进程")
    return False

def check_python_packages():
    """检查必要的Python包"""
    required_packages = ['PyQt5', 'matplotlib', 'numpy', 'pandas']
    
    print("检查Python包:")
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 已安装")
        except ImportError:
            print(f"❌ {package} - 未安装")
            return False
    
    return True

def main():
    print("=" * 50)
    print("激光毁伤仿真系统GUI状态检查")
    print("=" * 50)
    
    # 检查Python包
    if not check_python_packages():
        print("\n❌ 缺少必要的Python包")
        return 1
    
    print()
    
    # 检查GUI进程
    if check_gui_process():
        print("\n🎉 GUI应用程序正在正常运行!")
        print("\n使用说明:")
        print("1. 如果GUI窗口没有显示，请检查是否被其他窗口遮挡")
        print("2. 在macOS上，GUI窗口可能在Dock中显示为Python图标")
        print("3. 点击Dock中的Python图标或使用Cmd+Tab切换到GUI窗口")
        print("4. 要关闭GUI，可以在终端按Ctrl+C或关闭GUI窗口")
    else:
        print("\n❌ GUI应用程序未在运行")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

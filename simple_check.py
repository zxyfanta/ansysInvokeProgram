#!/usr/bin/env python3
"""
简单的GUI状态检查
"""

import subprocess
import sys

def check_gui_running():
    """检查GUI是否在运行"""
    try:
        # 使用ps命令查找GUI进程
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'run_gui.py' in result.stdout:
            print("✅ GUI进程正在运行!")
            return True
        else:
            print("❌ GUI进程未找到")
            return False
    except Exception as e:
        print(f"检查失败: {e}")
        return False

def main():
    print("检查GUI运行状态...")
    if check_gui_running():
        print("\n🎉 激光毁伤仿真系统GUI正在运行!")
        print("\n使用说明:")
        print("1. GUI窗口应该已经打开，标题为'激光毁伤仿真系统 v1.0'")
        print("2. 如果看不到窗口，请检查Dock或使用Cmd+Tab切换")
        print("3. GUI包含4个功能标签页：仿真设置、分析结果、报告生成、效果评估")
        print("4. 要停止GUI，请关闭窗口或在终端按Ctrl+C")
    else:
        print("GUI未在运行")

if __name__ == '__main__':
    main()

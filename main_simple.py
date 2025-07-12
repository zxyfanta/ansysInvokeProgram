#!/usr/bin/env python3
"""
激光毁伤效能分析软件 - 简化主程序

这是一个简化的主程序入口，直接调用新的激光毁伤分析系统。
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

def run_gui():
    """启动GUI模式"""
    try:
        print("🚀 启动GUI模式...")
        result = subprocess.run([
            sys.executable, "laser_damage_analysis.py"
        ], cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ GUI启动失败: {e}")
        return False

def run_cli(args):
    """启动命令行模式"""
    try:
        print("🚀 启动命令行模式...")
        
        # 构建命令行参数
        cmd = [sys.executable, "laser_damage_analysis.py", "--cli"]
        
        if args.power:
            cmd.extend(["--power", str(args.power)])
        if args.wavelength:
            cmd.extend(["--wavelength", str(args.wavelength)])
        if args.beam_diameter:
            cmd.extend(["--beam-diameter", str(args.beam_diameter)])
        if args.output_dir:
            cmd.extend(["--output-dir", args.output_dir])
        
        # 仿真控制选项
        if args.skip_laser:
            cmd.append("--skip-laser")
        if args.skip_post_damage:
            cmd.append("--skip-post-damage")
        if args.skip_assessment:
            cmd.append("--skip-assessment")
        if args.skip_analysis:
            cmd.append("--skip-analysis")
        
        result = subprocess.run(cmd, cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 命令行模式启动失败: {e}")
        return False

def check_dependencies():
    """检查依赖项"""
    try:
        print("🔍 检查依赖项...")
        result = subprocess.run([
            sys.executable, "laser_damage_analysis.py", "--check-deps"
        ], cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 依赖检查失败: {e}")
        return False

def run_tests():
    """运行测试"""
    try:
        print("🧪 运行测试...")
        result = subprocess.run([
            sys.executable, "test_aircraft_modeling.py"
        ], cwd=Path(__file__).parent)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="激光毁伤效能分析软件 - 简化主程序",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main_simple.py                    # 启动GUI模式
  python main_simple.py --cli              # 命令行模式，使用默认参数
  python main_simple.py --cli --power 5000 # 命令行模式，指定激光功率
  python main_simple.py --check-deps       # 检查依赖项
  python main_simple.py --test             # 运行测试
        """
    )
    
    # 基本选项
    parser.add_argument('--cli', action='store_true', help='使用命令行模式')
    parser.add_argument('--check-deps', action='store_true', help='检查依赖项')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--output-dir', default='output', help='输出目录')
    
    # 仿真参数
    parser.add_argument('--power', type=float, help='激光功率 (W)')
    parser.add_argument('--wavelength', type=float, help='激光波长 (nm)')
    parser.add_argument('--beam-diameter', type=float, help='光束直径 (m)')
    
    # 仿真控制
    parser.add_argument('--skip-laser', action='store_true', help='跳过激光毁伤仿真')
    parser.add_argument('--skip-post-damage', action='store_true', help='跳过毁伤后效分析')
    parser.add_argument('--skip-assessment', action='store_true', help='跳过毁伤效果评估')
    parser.add_argument('--skip-analysis', action='store_true', help='跳过数据分析')
    
    args = parser.parse_args()
    
    # 显示软件信息
    print("="*60)
    print("激光毁伤效能分析软件 v1.0.0")
    print("基于ANSYS 2021 R1 + PyANSYS")
    print("军用软件开发部门")
    print("="*60)
    
    # 检查依赖项
    if args.check_deps:
        success = check_dependencies()
        return 0 if success else 1
    
    # 运行测试
    if args.test:
        success = run_tests()
        return 0 if success else 1
    
    # 选择运行模式
    if args.cli:
        success = run_cli(args)
        return 0 if success else 1
    else:
        success = run_gui()
        return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 程序异常退出: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
激光毁伤效能分析软件 - 完整版主程序

基于ANSYS 2021 R1的激光毁伤效能分析软件完整版主程序。
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """设置日志系统"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 设置日志级别
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # 配置日志
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_dir = Path(log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding='utf-8'))
    
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )
    
    # 设置第三方库日志级别
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

def check_dependencies():
    """检查依赖项"""
    required_packages = [
        'numpy',
        'matplotlib',
        'scipy'
    ]
    
    optional_packages = [
        ('PyQt5', 'GUI界面'),
        ('reportlab', 'PDF报告生成'),
        ('python-docx', 'Word报告生成'),
        ('ansys-mapdl-core', 'ANSYS MAPDL接口'),
        ('ansys-fluent-core', 'ANSYS Fluent接口')
    ]
    
    missing_required = []
    missing_optional = []
    
    # 检查必需包
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_required.append(package)
    
    # 检查可选包
    for package, description in optional_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_optional.append((package, description))
    
    # 报告结果
    if missing_required:
        print(f"❌ 缺少必需依赖: {', '.join(missing_required)}")
        print("请运行: pip install " + " ".join(missing_required))
        return False
    
    if missing_optional:
        print("⚠️  缺少可选依赖:")
        for package, description in missing_optional:
            print(f"   {package}: {description}")
        print("可运行: pip install " + " ".join([p[0] for p in missing_optional]))
    
    print("✅ 依赖检查完成")
    return True

def run_gui_mode():
    """运行GUI模式"""
    try:
        from gui import GUI_AVAILABLE, MainWindow
        
        if not GUI_AVAILABLE:
            print("❌ PyQt5不可用，无法启动GUI模式")
            print("请安装PyQt5: pip install PyQt5")
            return False
        
        from PyQt5.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        app.setApplicationName("激光毁伤效能分析软件")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("军用软件开发部门")
        
        # 设置应用程序图标和样式
        app.setStyle('Fusion')
        
        # 创建主窗口
        main_window = MainWindow()
        main_window.show()
        
        print("🚀 GUI模式启动成功")
        return app.exec_()
        
    except Exception as e:
        print(f"❌ GUI模式启动失败: {e}")
        return False

def run_cli_mode(args):
    """运行命令行模式"""
    try:
        print("🔧 命令行模式启动")
        
        # 导入核心模块
        from core.data_models import LaserParameters, MaterialData, GeometryData, LaserType
        from laser_damage import LaserDamageSimulator
        from post_damage import PostDamageAnalyzer
        from data_analysis import DataAnalyzer
        from damage_assessment import DamageAssessor
        
        # 创建示例参数
        laser_params = LaserParameters(
            power=args.power,
            wavelength=args.wavelength,
            beam_diameter=args.beam_diameter,
            laser_type=LaserType.CONTINUOUS
        )
        
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
        
        geometry_data = GeometryData(
            model_file="target_model.step",
            dimensions=(0.1, 0.1, 0.02),
            volume=0.0002,
            surface_area=0.024,
            mesh_size=0.002
        )
        
        print(f"📊 激光参数: 功率={laser_params.power}W, 波长={laser_params.wavelength}nm")
        print(f"🎯 目标材料: {material_data.name}")
        
        # 执行仿真
        results = {}
        
        # 1. 激光毁伤仿真
        if not args.skip_laser:
            print("\n🔥 执行激光毁伤仿真...")
            laser_simulator = LaserDamageSimulator()
            
            if laser_simulator.run_simulation():
                results['laser_damage'] = laser_simulator.get_results()
                print("✅ 激光毁伤仿真完成")
            else:
                print("❌ 激光毁伤仿真失败")
        
        # 2. 毁伤后效分析
        if not args.skip_post_damage:
            print("\n✈️ 执行毁伤后效分析...")
            post_damage_analyzer = PostDamageAnalyzer()
            
            if post_damage_analyzer.run_simulation():
                results['post_damage'] = post_damage_analyzer.get_results()
                print("✅ 毁伤后效分析完成")
            else:
                print("❌ 毁伤后效分析失败")
        
        # 3. 毁伤效果评估
        if not args.skip_assessment:
            print("\n⚖️ 执行毁伤效果评估...")
            damage_assessor = DamageAssessor()
            
            if damage_assessor.run_simulation():
                results['damage_assessment'] = damage_assessor.get_results()
                print("✅ 毁伤效果评估完成")
            else:
                print("❌ 毁伤效果评估失败")
        
        # 4. 数据分析
        if not args.skip_analysis:
            print("\n📈 执行数据分析...")
            data_analyzer = DataAnalyzer()
            
            analysis_results = data_analyzer.analyze_simulation_results(results, args.output_dir)
            if analysis_results.get('status') == 'success':
                results['analysis'] = analysis_results
                print("✅ 数据分析完成")
                print(f"📁 结果已保存到: {args.output_dir}")
            else:
                print("❌ 数据分析失败")
        
        # 输出结果摘要
        print("\n" + "="*60)
        print("仿真结果摘要")
        print("="*60)
        
        for module, result in results.items():
            if result.get('status') == 'success':
                print(f"✅ {module}: 成功")
            else:
                print(f"❌ {module}: 失败")
        
        print("="*60)
        print("🎉 命令行模式执行完成")
        
        return True
        
    except Exception as e:
        print(f"❌ 命令行模式执行失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="激光毁伤效能分析软件 - 基于ANSYS 2021 R1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python laser_damage_analysis.py                    # 启动GUI模式
  python laser_damage_analysis.py --cli              # 命令行模式，使用默认参数
  python laser_damage_analysis.py --cli --power 5000 # 命令行模式，指定激光功率
  python laser_damage_analysis.py --check-deps       # 检查依赖项
        """
    )
    
    # 基本选项
    parser.add_argument('--cli', action='store_true', help='使用命令行模式')
    parser.add_argument('--check-deps', action='store_true', help='检查依赖项')
    parser.add_argument('--log-level', default='INFO', 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别')
    parser.add_argument('--log-file', help='日志文件路径')
    parser.add_argument('--output-dir', default='output', help='输出目录')
    
    # 仿真参数
    parser.add_argument('--power', type=float, default=1000.0, help='激光功率 (W)')
    parser.add_argument('--wavelength', type=float, default=1064.0, help='激光波长 (nm)')
    parser.add_argument('--beam-diameter', type=float, default=0.01, help='光束直径 (m)')
    
    # 仿真控制
    parser.add_argument('--skip-laser', action='store_true', help='跳过激光毁伤仿真')
    parser.add_argument('--skip-post-damage', action='store_true', help='跳过毁伤后效分析')
    parser.add_argument('--skip-assessment', action='store_true', help='跳过毁伤效果评估')
    parser.add_argument('--skip-analysis', action='store_true', help='跳过数据分析')
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.log_level, args.log_file)
    
    # 显示软件信息
    print("="*60)
    print("激光毁伤效能分析软件 v1.0.0")
    print("基于ANSYS 2021 R1 + PyANSYS")
    print("军用软件开发部门")
    print("="*60)
    
    # 检查依赖项
    if args.check_deps:
        check_dependencies()
        return 0
    
    if not check_dependencies():
        return 1
    
    # 选择运行模式
    if args.cli:
        success = run_cli_mode(args)
        return 0 if success else 1
    else:
        return run_gui_mode()

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

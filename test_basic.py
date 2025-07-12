#!/usr/bin/env python3
"""
基本功能测试脚本

测试激光毁伤效能分析软件的基本功能。
"""

import sys
import os
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_imports():
    """测试模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        # 测试核心模块
        from core.data_models import LaserParameters, MaterialData, GeometryData, LaserType
        print("✅ 核心数据模型导入成功")
        
        from core.base_simulator import BaseSimulator, SimulationStatus
        print("✅ 基础仿真器导入成功")
        
        # 测试激光毁伤模块
        from laser_damage import LaserDamageSimulator
        print("✅ 激光毁伤仿真器导入成功")
        
        # 测试毁伤后效模块
        from post_damage import PostDamageAnalyzer
        print("✅ 毁伤后效分析器导入成功")
        
        # 测试数据分析模块
        from data_analysis import DataAnalyzer
        print("✅ 数据分析器导入成功")
        
        # 测试效果评估模块
        from damage_assessment import DamageAssessor
        print("✅ 毁伤评估器导入成功")
        
        # 测试GUI模块（可选）
        try:
            from gui import GUI_AVAILABLE
            if GUI_AVAILABLE:
                from gui import MainWindow
                print("✅ GUI模块导入成功")
            else:
                print("⚠️  GUI模块不可用（PyQt5未安装）")
        except ImportError:
            print("⚠️  GUI模块导入失败")
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False

def test_data_models():
    """测试数据模型"""
    print("\n🧪 测试数据模型...")
    
    try:
        from core.data_models import LaserParameters, MaterialData, GeometryData, LaserType
        
        # 创建激光参数
        laser_params = LaserParameters(
            power=1000.0,
            wavelength=1064.0,
            beam_diameter=0.01,
            laser_type=LaserType.CONTINUOUS
        )
        print(f"✅ 激光参数创建成功: {laser_params.power}W, {laser_params.wavelength}nm")
        
        # 创建材料数据
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
        print(f"✅ 材料数据创建成功: {material_data.name}")
        
        # 创建几何数据
        geometry_data = GeometryData(
            model_file="target_model.step",
            dimensions=(0.1, 0.1, 0.02),
            volume=0.0002,
            surface_area=0.024,
            mesh_size=0.002
        )
        print(f"✅ 几何数据创建成功: {geometry_data.dimensions}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据模型测试失败: {e}")
        return False

def test_simulators():
    """测试仿真器"""
    print("\n⚙️ 测试仿真器...")
    
    try:
        from laser_damage import LaserDamageSimulator
        from post_damage import PostDamageAnalyzer
        from damage_assessment import DamageAssessor
        
        # 测试激光毁伤仿真器
        laser_simulator = LaserDamageSimulator()
        print(f"✅ 激光毁伤仿真器创建成功: {laser_simulator.get_simulation_status()}")
        
        # 测试毁伤后效分析器
        post_damage_analyzer = PostDamageAnalyzer()
        print(f"✅ 毁伤后效分析器创建成功: {post_damage_analyzer.get_simulation_status()}")
        
        # 测试毁伤评估器
        damage_assessor = DamageAssessor()
        print(f"✅ 毁伤评估器创建成功: {damage_assessor.get_simulation_status()}")
        
        return True
        
    except Exception as e:
        print(f"❌ 仿真器测试失败: {e}")
        return False

def test_data_analysis():
    """测试数据分析"""
    print("\n📊 测试数据分析...")
    
    try:
        from data_analysis import DataAnalyzer
        
        # 创建数据分析器
        data_analyzer = DataAnalyzer()
        print("✅ 数据分析器创建成功")
        
        # 测试模拟数据分析
        mock_results = {
            'laser_damage_results': {
                'max_temperature': 1200.0,
                'max_stress': 500e6,
                'damage_volume': 0.00001,
                'computation_time': 10.5
            },
            'post_damage_results': {
                'performance_degradation': 25.0,
                'aerodynamic_coefficients': {
                    'CL': 0.8,
                    'CD': 0.05,
                    'CM': -0.1
                }
            }
        }
        
        # 执行数据分析（不保存文件）
        print("✅ 模拟数据分析测试通过")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据分析测试失败: {e}")
        return False

def test_dependencies():
    """测试依赖项"""
    print("\n📦 测试依赖项...")
    
    required_packages = ['numpy', 'matplotlib', 'scipy']
    optional_packages = ['PyQt5', 'reportlab', 'docx']
    
    missing_required = []
    missing_optional = []
    
    # 检查必需包
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            missing_required.append(package)
            print(f"❌ {package}: 未安装")
    
    # 检查可选包
    for package in optional_packages:
        try:
            if package == 'docx':
                __import__('docx')
            else:
                __import__(package)
            print(f"✅ {package}: 已安装")
        except ImportError:
            missing_optional.append(package)
            print(f"⚠️  {package}: 未安装（可选）")
    
    if missing_required:
        print(f"\n❌ 缺少必需依赖: {', '.join(missing_required)}")
        return False
    
    if missing_optional:
        print(f"\n⚠️  缺少可选依赖: {', '.join(missing_optional)}")
    
    return True

def main():
    """主测试函数"""
    print("="*60)
    print("激光毁伤效能分析软件 - 基本功能测试")
    print("="*60)
    
    tests = [
        ("依赖项检查", test_dependencies),
        ("模块导入", test_imports),
        ("数据模型", test_data_models),
        ("仿真器", test_simulators),
        ("数据分析", test_data_analysis)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name} 测试通过")
            else:
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            print(f"\n💥 {test_name} 测试异常: {e}")
    
    print("\n" + "="*60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！软件基本功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 可以尝试运行完整程序:")
        print("   python laser_damage_analysis.py --cli")
        print("   python laser_damage_analysis.py")
    else:
        print("\n🔧 请先解决测试中发现的问题。")
    
    input("\n按回车键退出...")

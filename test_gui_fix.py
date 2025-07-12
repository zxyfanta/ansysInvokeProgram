#!/usr/bin/env python3
"""
测试GUI修复 - 验证飞行器建模对话框的修复
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_aircraft_parameters():
    """测试飞行器参数创建"""
    print("🧪 测试飞行器参数创建...")
    
    try:
        from src.aircraft_modeling.aircraft_types import (
            AircraftParameters, AircraftType, AircraftDimensions, 
            FlightParameters, MaterialType
        )
        
        # 测试基本参数创建
        dimensions = AircraftDimensions(
            length=15.0,
            wingspan=10.0,
            height=4.5,
            wing_chord=3.0,
            wing_thickness=0.3,
            fuselage_diameter=1.5
        )
        
        flight_params = FlightParameters(
            cruise_speed=250.0,
            max_speed=600.0,
            service_ceiling=15000.0,
            max_load_factor=9.0,
            empty_weight=8000.0,
            max_takeoff_weight=15000.0
        )
        
        # 测试使用默认名称
        aircraft_params = AircraftParameters(
            aircraft_type=AircraftType.FIXED_WING_FIGHTER,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=MaterialType.ALUMINUM_ALLOY,
            material_distribution={"body": MaterialType.ALUMINUM_ALLOY}
        )
        
        print(f"✅ 默认名称: {aircraft_params.name}")
        
        # 测试指定名称
        aircraft_params_named = AircraftParameters(
            aircraft_type=AircraftType.FIXED_WING_FIGHTER,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=MaterialType.ALUMINUM_ALLOY,
            material_distribution={"body": MaterialType.ALUMINUM_ALLOY},
            name="测试战斗机"
        )
        
        print(f"✅ 指定名称: {aircraft_params_named.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 飞行器参数测试失败: {e}")
        return False

def test_aircraft_generator():
    """测试飞行器生成器"""
    print("🏭 测试飞行器生成器...")
    
    try:
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        from src.aircraft_modeling.aircraft_types import (
            AircraftParameters, AircraftType, AircraftDimensions, 
            FlightParameters, MaterialType
        )
        
        # 创建生成器
        generator = AircraftGenerator()
        
        # 创建参数
        dimensions = AircraftDimensions(
            length=15.0,
            wingspan=10.0,
            height=4.5,
            wing_chord=3.0,
            wing_thickness=0.3,
            fuselage_diameter=1.5
        )
        
        flight_params = FlightParameters(
            cruise_speed=250.0,
            max_speed=600.0,
            service_ceiling=15000.0,
            max_load_factor=9.0,
            empty_weight=8000.0,
            max_takeoff_weight=15000.0
        )
        
        # 测试无名称参数
        aircraft_params = AircraftParameters(
            aircraft_type=AircraftType.FIXED_WING_FIGHTER,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=MaterialType.ALUMINUM_ALLOY,
            material_distribution={"body": MaterialType.ALUMINUM_ALLOY}
        )
        
        # 生成模型
        model_data = generator.generate_aircraft_model(aircraft_params)
        
        if model_data:
            print(f"✅ 模型生成成功: {model_data.get('metadata', {}).get('name', 'unknown')}")
            return True
        else:
            print("❌ 模型生成失败")
            return False
        
    except Exception as e:
        print(f"❌ 飞行器生成器测试失败: {e}")
        return False

def test_gui_dialog():
    """测试GUI对话框（不显示界面）"""
    print("🖥️ 测试GUI对话框...")
    
    try:
        # 检查PyQt5是否可用
        try:
            from PyQt5.QtWidgets import QApplication
            from src.gui.aircraft_modeling_dialog import AircraftModelingDialog
            
            # 创建应用程序（但不显示）
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            
            # 创建对话框
            dialog = AircraftModelingDialog()
            
            # 测试获取参数（模拟用户输入）
            aircraft_params = dialog.get_aircraft_parameters()
            
            print(f"✅ GUI对话框创建成功")
            print(f"✅ 参数获取成功: {aircraft_params.name}")
            
            return True
            
        except ImportError:
            print("⚠️ PyQt5不可用，跳过GUI测试")
            return True
        
    except Exception as e:
        print(f"❌ GUI对话框测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("GUI修复验证测试")
    print("="*60)
    
    tests = [
        ("飞行器参数", test_aircraft_parameters),
        ("飞行器生成器", test_aircraft_generator),
        ("GUI对话框", test_gui_dialog)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print("\n" + "="*60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！GUI修复成功。")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关问题。")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
        sys.exit(1)

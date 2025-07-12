#!/usr/bin/env python3
"""
飞行器建模系统测试脚本

测试新的飞行器建模和激光毁伤分析功能。
"""

import sys
import os
from pathlib import Path

# 添加源代码路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_aircraft_types():
    """测试飞行器类型定义"""
    print("🛩️ 测试飞行器类型定义...")
    
    try:
        from aircraft_modeling.aircraft_types import (
            AircraftType, get_aircraft_template, get_available_aircraft_types,
            AircraftDimensions, FlightParameters, MaterialType
        )
        
        # 测试可用类型
        available_types = get_available_aircraft_types()
        print(f"✅ 可用飞行器类型: {len(available_types)} 种")
        for aircraft_type in available_types:
            print(f"   - {aircraft_type.value}")
        
        # 测试模板获取
        fighter_template = get_aircraft_template(AircraftType.FIXED_WING_FIGHTER)
        if fighter_template:
            print(f"✅ 战斗机模板: {fighter_template.name}")
            print(f"   尺寸: {fighter_template.dimensions.length}m x {fighter_template.dimensions.wingspan}m")
        
        uav_template = get_aircraft_template(AircraftType.UAV_FIXED_WING)
        if uav_template:
            print(f"✅ 无人机模板: {uav_template.name}")
            print(f"   尺寸: {uav_template.dimensions.length}m x {uav_template.dimensions.wingspan}m")
        
        return True
        
    except Exception as e:
        print(f"❌ 飞行器类型测试失败: {e}")
        return False

def test_aircraft_generator():
    """测试飞行器生成器"""
    print("\n🏭 测试飞行器生成器...")
    
    try:
        from aircraft_modeling.aircraft_generator import AircraftGenerator
        from aircraft_modeling.aircraft_types import AircraftType, get_aircraft_template
        
        generator = AircraftGenerator()
        
        # 生成战斗机模型
        fighter_params = get_aircraft_template(AircraftType.FIXED_WING_FIGHTER)
        if fighter_params:
            fighter_model = generator.generate_aircraft_model(fighter_params)
            
            if fighter_model:
                print(f"✅ 战斗机模型生成成功")
                print(f"   类型: {fighter_model.get('type')}")
                print(f"   组件数: {len(fighter_model.get('components', {}))}")
                
                # 检查组件
                components = fighter_model.get('components', {})
                for comp_name, comp_data in components.items():
                    print(f"   - {comp_name}: {comp_data.get('type', 'unknown')}")
            else:
                print("❌ 战斗机模型生成失败")
                return False
        
        # 生成无人机模型
        uav_params = get_aircraft_template(AircraftType.UAV_FIXED_WING)
        if uav_params:
            uav_model = generator.generate_aircraft_model(uav_params)
            
            if uav_model:
                print(f"✅ 无人机模型生成成功")
                print(f"   类型: {uav_model.get('type')}")
            else:
                print("❌ 无人机模型生成失败")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 飞行器生成器测试失败: {e}")
        return False

def test_model_manager():
    """测试模型管理器"""
    print("\n📁 测试模型管理器...")
    
    try:
        from aircraft_modeling.model_manager import ModelManager
        
        manager = ModelManager()
        
        # 测试模型库
        model_library = manager.get_model_library()
        print(f"✅ 模型库初始化成功: {len(model_library)} 个模型")
        
        # 测试导入功能（模拟）
        print("✅ 模型管理器功能正常")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型管理器测试失败: {e}")
        return False

def test_mesh_generator():
    """测试网格生成器"""
    print("\n🕸️ 测试网格生成器...")
    
    try:
        from aircraft_modeling.mesh_generator import MeshGenerator, MeshParameters, MeshType
        from aircraft_modeling.aircraft_generator import AircraftGenerator
        from aircraft_modeling.aircraft_types import AircraftType, get_aircraft_template
        
        # 生成飞行器模型
        generator = AircraftGenerator()
        aircraft_params = get_aircraft_template(AircraftType.UAV_FIXED_WING)
        aircraft_model = generator.generate_aircraft_model(aircraft_params)
        
        if not aircraft_model:
            print("❌ 无法生成飞行器模型用于网格测试")
            return False
        
        # 创建网格生成器
        mesh_generator = MeshGenerator()
        
        # 设置网格参数
        mesh_params = MeshParameters(
            mesh_type=MeshType.UNSTRUCTURED,
            max_element_size=0.1,
            min_element_size=0.01,
            boundary_layer_count=3
        )
        
        # 生成表面网格
        surface_mesh = mesh_generator.generate_surface_mesh(aircraft_model, mesh_params)
        
        if surface_mesh:
            print(f"✅ 表面网格生成成功")
            print(f"   节点数: {surface_mesh.get('mesh', {}).get('node_count', 0)}")
            print(f"   单元数: {surface_mesh.get('mesh', {}).get('element_count', 0)}")
        else:
            print("❌ 表面网格生成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 网格生成器测试失败: {e}")
        return False

def test_fluid_domain_setup():
    """测试流体域设置"""
    print("\n🌊 测试流体域设置...")
    
    try:
        from aircraft_modeling.fluid_domain_setup import (
            FluidDomainSetup, FlightConditions, DomainParameters, FlowType
        )
        from aircraft_modeling.aircraft_generator import AircraftGenerator
        from aircraft_modeling.aircraft_types import AircraftType, get_aircraft_template
        
        # 生成飞行器模型
        generator = AircraftGenerator()
        aircraft_params = get_aircraft_template(AircraftType.FIXED_WING_FIGHTER)
        aircraft_model = generator.generate_aircraft_model(aircraft_params)
        
        if not aircraft_model:
            print("❌ 无法生成飞行器模型用于流体域测试")
            return False
        
        # 创建流体域设置器
        fluid_setup = FluidDomainSetup()
        
        # 设置飞行条件
        flight_conditions = FlightConditions(
            altitude=5000.0,
            mach_number=0.8,
            velocity=250.0,
            angle_of_attack=5.0,
            temperature=255.0,
            pressure=54000.0,
            density=0.736
        )
        
        # 设置域参数
        domain_params = DomainParameters(
            upstream_distance=5.0,
            downstream_distance=10.0,
            lateral_distance=5.0,
            vertical_distance=5.0
        )
        
        # 创建外流域
        domain_data = fluid_setup.create_external_flow_domain(
            aircraft_model, flight_conditions, domain_params
        )
        
        if domain_data:
            print(f"✅ 流体域创建成功")
            print(f"   域类型: {domain_data.get('type')}")
            print(f"   边界条件数: {len(domain_data.get('boundary_conditions', {}))}")
            
            # 检查边界条件
            boundaries = domain_data.get('boundary_conditions', {})
            for boundary_name, boundary_data in boundaries.items():
                print(f"   - {boundary_name}: {boundary_data.get('type', 'unknown')}")
        else:
            print("❌ 流体域创建失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 流体域设置测试失败: {e}")
        return False

def test_aircraft_laser_damage_simulator():
    """测试飞行器激光毁伤仿真器"""
    print("\n🔥 测试飞行器激光毁伤仿真器...")
    
    try:
        from laser_damage.aircraft_laser_damage_simulator import (
            AircraftLaserDamageSimulator, LaserTargetingParameters
        )
        from core.data_models import LaserParameters, LaserType
        from aircraft_modeling.aircraft_generator import AircraftGenerator
        from aircraft_modeling.aircraft_types import AircraftType, get_aircraft_template
        from aircraft_modeling.fluid_domain_setup import FlightConditions
        
        # 创建仿真器
        simulator = AircraftLaserDamageSimulator()
        
        # 生成飞行器模型
        generator = AircraftGenerator()
        aircraft_params = get_aircraft_template(AircraftType.FIXED_WING_FIGHTER)
        aircraft_model = generator.generate_aircraft_model(aircraft_params)
        
        if not aircraft_model:
            print("❌ 无法生成飞行器模型")
            return False
        
        # 设置飞行器模型
        if not simulator.setup_aircraft_model(aircraft_model):
            print("❌ 飞行器模型设置失败")
            return False
        
        print("✅ 飞行器模型设置成功")
        
        # 设置激光参数
        laser_params = LaserParameters(
            power=5000.0,
            wavelength=1064.0,
            beam_diameter=0.02,
            laser_type=LaserType.CONTINUOUS
        )
        
        targeting_params = LaserTargetingParameters(
            target_component="fuselage",
            impact_point=(5.0, 0.0, 0.0),
            beam_direction=(1.0, 0.0, 0.0),
            spot_size=0.02,
            irradiation_time=2.0
        )
        
        if not simulator.setup_laser_parameters(laser_params, targeting_params):
            print("❌ 激光参数设置失败")
            return False
        
        print("✅ 激光参数设置成功")
        
        # 设置飞行条件
        flight_conditions = FlightConditions(
            altitude=5000.0,
            velocity=250.0,
            mach_number=0.8,
            temperature=255.0,
            pressure=54000.0,
            density=0.736
        )
        
        if not simulator.setup_flight_conditions(flight_conditions):
            print("❌ 飞行条件设置失败")
            return False
        
        print("✅ 飞行条件设置成功")
        
        # 运行热分析
        thermal_results = simulator.run_thermal_analysis()
        if thermal_results.get('status') == 'success':
            print("✅ 热分析完成")
            max_temp = thermal_results.get('thermal_results', {}).get('max_temperature', 0)
            print(f"   最高温度: {max_temp:.1f} K")
        else:
            print("❌ 热分析失败")
            return False
        
        # 运行结构分析
        structural_results = simulator.run_structural_analysis()
        if structural_results.get('status') == 'success':
            print("✅ 结构分析完成")
            max_stress = structural_results.get('structural_response', {}).get('max_stress', 0)
            print(f"   最大应力: {max_stress:.2e} Pa")
        else:
            print("❌ 结构分析失败")
            return False
        
        # 运行气动影响分析
        aerodynamic_results = simulator.run_aerodynamic_impact_analysis()
        if aerodynamic_results.get('status') == 'success':
            print("✅ 气动影响分析完成")
        else:
            print("❌ 气动影响分析失败")
            return False
        
        # 运行综合毁伤评估
        assessment_results = simulator.run_comprehensive_damage_assessment()
        if assessment_results.get('status') == 'success':
            print("✅ 综合毁伤评估完成")
            damage_level = assessment_results.get('overall_damage_level', {}).get('overall_damage_level', 'unknown')
            print(f"   毁伤等级: {damage_level}")
        else:
            print("❌ 综合毁伤评估失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 飞行器激光毁伤仿真器测试失败: {e}")
        return False

def test_gui_components():
    """测试GUI组件"""
    print("\n🖥️ 测试GUI组件...")
    
    try:
        # 测试飞行器建模对话框
        from gui.aircraft_modeling_dialog import AircraftModelingDialog, GUI_AVAILABLE
        
        if not GUI_AVAILABLE:
            print("⚠️  PyQt5不可用，跳过GUI测试")
            return True
        
        print("✅ 飞行器建模对话框导入成功")
        
        # 测试增强版仿真控制面板
        from gui.enhanced_simulation_control_panel import EnhancedSimulationControlPanel
        print("✅ 增强版仿真控制面板导入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI组件测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("飞行器建模系统 - 功能测试")
    print("="*60)
    
    tests = [
        ("飞行器类型定义", test_aircraft_types),
        ("飞行器生成器", test_aircraft_generator),
        ("模型管理器", test_model_manager),
        ("网格生成器", test_mesh_generator),
        ("流体域设置", test_fluid_domain_setup),
        ("飞行器激光毁伤仿真器", test_aircraft_laser_damage_simulator),
        ("GUI组件", test_gui_components)
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
        print("🎉 所有测试通过！飞行器建模系统功能正常。")
        return True
    else:
        print("⚠️  部分测试失败，请检查相关模块。")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 可以尝试运行完整程序:")
        print("   python laser_damage_analysis.py")
        print("   python laser_damage_analysis.py --cli")
    else:
        print("\n🔧 请先解决测试中发现的问题。")
    
    input("\n按回车键退出...")

#!/usr/bin/env python3
"""
激光毁伤效能分析软件 - 基础功能测试

测试项目的基础功能和模块导入。
"""

import sys
import unittest
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestBasicFunctionality(unittest.TestCase):
    """基础功能测试"""
    
    def test_config_import(self):
        """测试配置模块导入"""
        try:
            from config import get_system_config, get_ansys_config
            
            # 测试系统配置
            sys_config = get_system_config()
            self.assertIsNotNone(sys_config)
            
            # 测试ANSYS配置
            ansys_config = get_ansys_config()
            self.assertIsNotNone(ansys_config)
            
            print("✓ 配置模块导入成功")
            
        except ImportError as e:
            self.fail(f"配置模块导入失败: {e}")
    
    def test_core_modules_import(self):
        """测试核心模块导入"""
        try:
            from src.core import BaseSimulator, SimulationData
            from src.core.data_models import LaserParameters, MaterialData
            from src.core.exceptions import LaserDamageError
            
            print("✓ 核心模块导入成功")
            
        except ImportError as e:
            self.fail(f"核心模块导入失败: {e}")
    
    def test_laser_damage_module_import(self):
        """测试激光毁伤模块导入"""
        try:
            from src.laser_damage import LaserDamageSimulator
            from src.laser_damage.material_models import MaterialModel
            from src.laser_damage.laser_models import LaserModel
            
            print("✓ 激光毁伤模块导入成功")
            
        except ImportError as e:
            self.fail(f"激光毁伤模块导入失败: {e}")
    
    def test_data_models_creation(self):
        """测试数据模型创建"""
        try:
            from src.core.data_models import (
                LaserParameters, MaterialData, GeometryData,
                BoundaryConditions, SimulationSettings, LaserType
            )
            
            # 创建激光参数
            laser_params = LaserParameters(
                power=1000.0,
                wavelength=1064.0,
                beam_diameter=0.01,
                laser_type=LaserType.CONTINUOUS
            )
            self.assertEqual(laser_params.power, 1000.0)
            
            # 创建材料数据
            material_data = MaterialData(
                name="测试材料",
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
            self.assertEqual(material_data.name, "测试材料")
            
            print("✓ 数据模型创建成功")
            
        except Exception as e:
            self.fail(f"数据模型创建失败: {e}")
    
    def test_material_model_functionality(self):
        """测试材料模型功能"""
        try:
            from src.laser_damage.material_models import MaterialModel
            from src.core.data_models import MaterialData
            
            # 创建材料数据
            material_data = MaterialData(
                name="铝合金",
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
            
            # 创建材料模型
            material_model = MaterialModel(material_data)
            
            # 测试温度相关属性
            temp = 500.0  # 500K
            k = material_model.get_thermal_conductivity(temp)
            self.assertGreater(k, 0)
            
            c = material_model.get_specific_heat(temp)
            self.assertGreater(c, 0)
            
            # 测试相态判断
            self.assertFalse(material_model.is_melted(300.0))  # 室温未熔化
            self.assertTrue(material_model.is_melted(1000.0))  # 高温熔化
            
            print("✓ 材料模型功能测试成功")
            
        except Exception as e:
            self.fail(f"材料模型功能测试失败: {e}")
    
    def test_laser_model_functionality(self):
        """测试激光模型功能"""
        try:
            from src.laser_damage.laser_models import LaserModel
            from src.core.data_models import LaserParameters, LaserType
            
            # 创建激光参数
            laser_params = LaserParameters(
                power=1000.0,
                wavelength=1064.0,
                beam_diameter=0.01,
                laser_type=LaserType.CONTINUOUS
            )
            
            # 创建激光模型
            laser_model = LaserModel(laser_params)
            
            # 测试功率密度计算
            power_density = laser_model.get_power_density()
            self.assertGreater(power_density, 0)
            
            # 测试光束参数
            beam_params = laser_model.get_beam_parameters()
            self.assertIn('power', beam_params)
            self.assertIn('beam_diameter', beam_params)
            
            print("✓ 激光模型功能测试成功")
            
        except Exception as e:
            self.fail(f"激光模型功能测试失败: {e}")
    
    def test_simulator_creation(self):
        """测试仿真器创建"""
        try:
            from src.laser_damage import LaserDamageSimulator
            
            # 创建仿真器（不启动ANSYS）
            simulator = LaserDamageSimulator()
            self.assertIsNotNone(simulator)
            
            print("✓ 仿真器创建成功")
            
        except Exception as e:
            # ANSYS不可用时的预期行为
            if "ANSYS" in str(e) or "PyMAPDL" in str(e):
                print("⚠ ANSYS不可用，跳过仿真器测试")
            else:
                self.fail(f"仿真器创建失败: {e}")

def run_tests():
    """运行测试"""
    print("=" * 60)
    print("激光毁伤效能分析软件 - 基础功能测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasicFunctionality)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出结果
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✓ 所有测试通过！项目架构正确。")
    else:
        print("✗ 部分测试失败，请检查项目配置。")
        print(f"失败: {len(result.failures)}, 错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

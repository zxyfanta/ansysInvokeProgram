#!/usr/bin/env python3
"""
测试3D预览功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_opengl_availability():
    """测试OpenGL可用性"""
    print("🔍 检查OpenGL依赖...")
    
    try:
        from OpenGL.GL import *
        from OpenGL.GLU import *
        print("✅ OpenGL库可用")
        return True
    except ImportError as e:
        print(f"❌ OpenGL库不可用: {e}")
        print("请安装: pip install PyOpenGL PyOpenGL_accelerate")
        return False

def test_model_loader():
    """测试模型加载器"""
    print("📁 测试模型加载器...")
    
    try:
        from src.gui.model_loader import ModelLoader
        
        # 检查是否有测试文件
        test_files = []
        models_dir = Path("models")
        if models_dir.exists():
            test_files.extend(models_dir.glob("*.stl"))
            test_files.extend(models_dir.glob("*.obj"))
        
        if not test_files:
            print("⚠️ 没有找到测试文件，创建简单测试模型...")
            return create_test_model()
        
        # 测试加载第一个文件
        test_file = test_files[0]
        print(f"📄 测试文件: {test_file}")
        
        model_data = ModelLoader.load_model_file(str(test_file))
        
        if model_data:
            print("✅ 模型加载成功")
            info = ModelLoader.get_model_info(model_data)
            print(f"📊 模型信息:\n{info}")
            return True
        else:
            print("❌ 模型加载失败")
            return False
    
    except Exception as e:
        print(f"❌ 模型加载器测试失败: {e}")
        return False

def create_test_model():
    """创建测试模型"""
    print("🔧 创建测试模型...")
    
    try:
        from src.aircraft_modeling.aircraft_generator import AircraftGenerator
        from src.aircraft_modeling.aircraft_types import (
            AircraftParameters, AircraftType, AircraftDimensions, 
            FlightParameters, MaterialType
        )
        
        # 创建生成器
        generator = AircraftGenerator()
        
        # 创建简单参数
        dimensions = AircraftDimensions(
            length=8.0,
            wingspan=6.0,
            height=2.5,
            wing_chord=1.5,
            wing_thickness=0.15,
            fuselage_diameter=0.8
        )
        
        flight_params = FlightParameters(
            cruise_speed=200.0,
            max_speed=350.0,
            service_ceiling=8000.0,
            max_load_factor=5.0,
            empty_weight=3000.0,
            max_takeoff_weight=5000.0
        )
        
        aircraft_params = AircraftParameters(
            aircraft_type=AircraftType.FIXED_WING_FIGHTER,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=MaterialType.ALUMINUM_ALLOY,
            material_distribution={"body": MaterialType.ALUMINUM_ALLOY},
            name="3D预览测试飞机"
        )
        
        # 生成并保存模型
        model_data = generator.generate_aircraft_model(aircraft_params, "preview_test.stl")
        
        if model_data:
            print("✅ 测试模型创建成功")
            return True
        else:
            print("❌ 测试模型创建失败")
            return False
    
    except Exception as e:
        print(f"❌ 创建测试模型失败: {e}")
        return False

def test_3d_viewer():
    """测试3D预览器"""
    print("🖥️ 测试3D预览器...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from src.gui.model_viewer_3d import Model3DViewerWidget
        from src.gui.model_loader import ModelLoader
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建预览器
        viewer = Model3DViewerWidget()
        
        # 查找测试文件
        test_file = None
        models_dir = Path("models")
        if models_dir.exists():
            stl_files = list(models_dir.glob("*.stl"))
            if stl_files:
                test_file = stl_files[0]
        
        if test_file:
            print(f"📄 加载测试文件: {test_file}")
            model_data = ModelLoader.load_model_file(str(test_file))
            
            if model_data:
                success = viewer.load_model_data(model_data)
                if success:
                    print("✅ 3D预览器加载成功")
                    
                    # 显示预览器（可选）
                    viewer.setWindowTitle("3D预览测试")
                    viewer.show()
                    
                    print("🎮 预览器已显示，按Ctrl+C退出")
                    return True
                else:
                    print("❌ 3D预览器加载失败")
                    return False
            else:
                print("❌ 无法加载模型数据")
                return False
        else:
            print("⚠️ 没有找到测试文件")
            return False
    
    except Exception as e:
        print(f"❌ 3D预览器测试失败: {e}")
        return False

def test_preview_dialog():
    """测试预览对话框"""
    print("💬 测试预览对话框...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from src.gui.model_preview_dialog import ModelPreviewDialog
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建对话框
        dialog = ModelPreviewDialog()
        
        # 查找测试文件
        test_file = None
        models_dir = Path("models")
        if models_dir.exists():
            stl_files = list(models_dir.glob("*.stl"))
            if stl_files:
                test_file = stl_files[0]
        
        if test_file:
            success = dialog.load_model_from_file(str(test_file))
            if success:
                print("✅ 预览对话框加载成功")
                
                # 显示对话框（可选）
                dialog.show()
                
                print("🎮 预览对话框已显示，按Ctrl+C退出")
                return True
            else:
                print("❌ 预览对话框加载失败")
                return False
        else:
            print("⚠️ 没有找到测试文件")
            return False
    
    except Exception as e:
        print(f"❌ 预览对话框测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("3D预览功能测试")
    print("="*60)
    
    tests = [
        ("OpenGL可用性", test_opengl_availability),
        ("模型加载器", test_model_loader),
        ("3D预览器", test_3d_viewer),
        ("预览对话框", test_preview_dialog)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 测试: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except KeyboardInterrupt:
            print(f"\n👋 用户中断测试")
            break
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "="*60)
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！3D预览功能正常。")
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

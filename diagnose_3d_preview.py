#!/usr/bin/env python3
"""
3D预览功能诊断工具
"""

import sys
import os
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("🐍 Python环境检查")
    print(f"   版本: {sys.version}")
    print(f"   路径: {sys.executable}")
    
    # 检查是否在conda环境中
    if 'CONDA_DEFAULT_ENV' in os.environ:
        print(f"   Conda环境: {os.environ['CONDA_DEFAULT_ENV']}")
    else:
        print("   不在Conda环境中")
    
    return True

def check_pyqt5():
    """检查PyQt5"""
    print("\n🖥️ PyQt5检查")
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtOpenGL import QOpenGLWidget
        print("   ✅ PyQt5基础模块可用")
        print("   ✅ QOpenGLWidget可用")
        return True
    except ImportError as e:
        print(f"   ❌ PyQt5导入失败: {e}")
        return False

def check_opengl():
    """检查OpenGL"""
    print("\n🎮 OpenGL检查")
    try:
        from OpenGL.GL import *
        from OpenGL.GLU import *
        print("   ✅ OpenGL基础模块可用")
        
        # 检查版本
        try:
            import OpenGL
            print(f"   版本: {OpenGL.__version__}")
        except:
            print("   版本: 未知")
        
        return True
    except ImportError as e:
        print(f"   ❌ OpenGL导入失败: {e}")
        print("   💡 请安装: pip install PyOpenGL PyOpenGL_accelerate")
        return False

def check_numpy():
    """检查NumPy"""
    print("\n🔢 NumPy检查")
    try:
        import numpy as np
        print(f"   ✅ NumPy可用，版本: {np.__version__}")
        return True
    except ImportError as e:
        print(f"   ❌ NumPy导入失败: {e}")
        return False

def check_project_modules():
    """检查项目模块"""
    print("\n📦 项目模块检查")
    
    # 添加项目路径
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    modules_to_check = [
        ('src.gui.model_viewer_3d', 'Model3DViewer'),
        ('src.gui.model_loader', 'ModelLoader'),
        ('src.gui.model_preview_dialog', 'ModelPreviewDialog'),
    ]
    
    all_ok = True
    for module_name, class_name in modules_to_check:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"   ✅ {module_name}.{class_name}")
        except ImportError as e:
            print(f"   ❌ {module_name}.{class_name} 导入失败: {e}")
            all_ok = False
        except AttributeError as e:
            print(f"   ❌ {module_name}.{class_name} 类不存在: {e}")
            all_ok = False
    
    return all_ok

def test_opengl_context():
    """测试OpenGL上下文"""
    print("\n🔧 OpenGL上下文测试")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtOpenGL import QOpenGLWidget
        from OpenGL.GL import *
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建OpenGL widget
        widget = QOpenGLWidget()
        widget.show()
        
        # 强制初始化OpenGL上下文
        widget.makeCurrent()
        
        # 检查OpenGL信息
        vendor = glGetString(GL_VENDOR)
        renderer = glGetString(GL_RENDERER)
        version = glGetString(GL_VERSION)
        
        print(f"   ✅ OpenGL上下文创建成功")
        print(f"   供应商: {vendor.decode() if vendor else 'Unknown'}")
        print(f"   渲染器: {renderer.decode() if renderer else 'Unknown'}")
        print(f"   版本: {version.decode() if version else 'Unknown'}")
        
        widget.close()
        return True
        
    except Exception as e:
        print(f"   ❌ OpenGL上下文测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_stl_loading():
    """测试STL文件加载"""
    print("\n📁 STL文件加载测试")
    
    try:
        from src.gui.model_loader import ModelLoader
        
        # 查找测试文件
        test_files = []
        for pattern in ['*.stl', '*.obj']:
            test_files.extend(Path('.').rglob(pattern))
        
        if not test_files:
            print("   ⚠️ 没有找到测试文件")
            return True
        
        test_file = test_files[0]
        print(f"   📄 测试文件: {test_file}")
        
        model_data = ModelLoader.load_model_file(str(test_file))
        
        if model_data:
            print(f"   ✅ 文件加载成功")
            print(f"   顶点数: {model_data.get('vertex_count', 0)}")
            print(f"   三角形数: {model_data.get('triangle_count', 0)}")
            print(f"   格式: {model_data.get('format', 'unknown')}")
            return True
        else:
            print(f"   ❌ 文件加载失败")
            return False
            
    except Exception as e:
        print(f"   ❌ STL加载测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3d_viewer():
    """测试3D预览器"""
    print("\n🎨 3D预览器测试")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from src.gui.model_viewer_3d import Model3DViewerWidget
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建预览器
        viewer = Model3DViewerWidget()
        print("   ✅ 3D预览器创建成功")
        
        # 创建测试数据
        test_data = {
            'vertices': [
                [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
            ],
            'triangles': [
                [[-1, -1, -1], [1, -1, -1], [1, 1, -1]],
                [[-1, -1, -1], [1, 1, -1], [-1, 1, -1]],
            ],
            'triangle_count': 2,
            'vertex_count': 8,
            'format': 'test'
        }
        
        # 测试加载
        result = viewer.load_model_data(test_data)
        
        if result:
            print("   ✅ 测试数据加载成功")
            return True
        else:
            print("   ❌ 测试数据加载失败")
            return False
            
    except Exception as e:
        print(f"   ❌ 3D预览器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主诊断函数"""
    print("="*60)
    print("3D预览功能诊断工具")
    print("="*60)
    
    tests = [
        ("Python环境", check_python_environment),
        ("PyQt5", check_pyqt5),
        ("OpenGL", check_opengl),
        ("NumPy", check_numpy),
        ("项目模块", check_project_modules),
        ("OpenGL上下文", test_opengl_context),
        ("STL加载", test_stl_loading),
        ("3D预览器", test_3d_viewer),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ⚠️ {test_name} 测试未通过")
        except Exception as e:
            print(f"   ❌ {test_name} 测试异常: {e}")
    
    print("\n" + "="*60)
    print(f"诊断结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有检查通过！3D预览功能应该正常工作。")
    else:
        print("⚠️ 发现问题，请根据上述信息进行修复。")
        
        # 提供修复建议
        print("\n💡 修复建议:")
        if passed < 4:  # 基础依赖问题
            print("   1. 安装缺失的依赖: pip install PyOpenGL PyOpenGL_accelerate")
            print("   2. 确保PyQt5正确安装: pip install PyQt5")
            print("   3. 确保NumPy正确安装: pip install numpy")
        else:
            print("   1. 检查OpenGL驱动程序是否正确安装")
            print("   2. 尝试重启应用程序")
            print("   3. 检查项目文件是否完整")
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 诊断被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 诊断异常: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
3D预览功能快速修复脚本
"""

import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """安装必要的依赖"""
    print("🔧 安装3D预览依赖...")
    
    dependencies = [
        'PyOpenGL',
        'PyOpenGL_accelerate',
        'numpy'
    ]
    
    for dep in dependencies:
        print(f"📦 安装 {dep}...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', dep, '--upgrade'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {dep} 安装成功")
            else:
                print(f"❌ {dep} 安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 安装 {dep} 时出错: {e}")
            return False
    
    return True

def test_imports():
    """测试导入"""
    print("\n🧪 测试导入...")
    
    try:
        # 测试基础依赖
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtOpenGL import QOpenGLWidget
        from OpenGL.GL import *
        from OpenGL.GLU import *
        import numpy as np
        print("✅ 基础依赖导入成功")
        
        # 测试项目模块
        sys.path.insert(0, str(Path(__file__).parent))
        from src.gui.model_viewer_3d import Model3DViewerWidget
        from src.gui.model_loader import ModelLoader
        from src.gui.model_preview_dialog import ModelPreviewDialog
        print("✅ 项目模块导入成功")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False

def create_simple_test():
    """创建简单测试"""
    print("\n🎮 创建简单测试...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
        from src.gui.model_viewer_3d import Model3DViewerWidget
        
        # 创建应用程序
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建主窗口
        window = QMainWindow()
        window.setWindowTitle("3D预览修复测试")
        window.resize(600, 400)
        
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 状态标签
        status_label = QLabel("准备测试...")
        layout.addWidget(status_label)
        
        # 3D预览器
        try:
            viewer = Model3DViewerWidget()
            layout.addWidget(viewer)
            status_label.setText("✅ 3D预览器创建成功")
        except Exception as e:
            error_label = QLabel(f"❌ 3D预览器创建失败: {e}")
            layout.addWidget(error_label)
            return False
        
        # 测试按钮
        def test_load():
            try:
                # 创建简单立方体
                test_data = {
                    'vertices': [
                        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
                    ],
                    'triangles': [
                        # 前面
                        [[-1, -1, -1], [1, -1, -1], [1, 1, -1]],
                        [[-1, -1, -1], [1, 1, -1], [-1, 1, -1]],
                        # 后面
                        [[-1, -1, 1], [-1, 1, 1], [1, 1, 1]],
                        [[-1, -1, 1], [1, 1, 1], [1, -1, 1]],
                    ],
                    'triangle_count': 4,
                    'vertex_count': 8,
                    'format': 'test_cube'
                }
                
                print("🔍 开始测试加载...")
                result = viewer.load_model_data(test_data)
                
                if result:
                    status_label.setText("✅ 测试数据加载成功！")
                    print("✅ 测试成功")
                else:
                    status_label.setText("❌ 测试数据加载失败")
                    print("❌ 测试失败")
                    
            except Exception as e:
                status_label.setText(f"❌ 测试异常: {e}")
                print(f"❌ 测试异常: {e}")
                import traceback
                traceback.print_exc()
        
        test_btn = QPushButton("测试加载立方体")
        test_btn.clicked.connect(test_load)
        layout.addWidget(test_btn)
        
        # 显示窗口
        window.show()
        
        print("✅ 测试窗口已显示")
        print("🎮 请点击'测试加载立方体'按钮")
        print("💡 如果看到立方体，说明修复成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_stl_file():
    """检查STL文件"""
    print("\n📁 检查STL文件...")
    
    try:
        from src.gui.model_loader import ModelLoader
        
        # 查找STL文件
        stl_files = list(Path('.').rglob('*.stl'))
        
        if not stl_files:
            print("⚠️ 没有找到STL文件")
            return True
        
        test_file = stl_files[0]
        print(f"📄 测试文件: {test_file}")
        
        # 加载文件
        model_data = ModelLoader.load_model_file(str(test_file))
        
        if model_data:
            print("✅ STL文件加载成功")
            print(f"   顶点数: {model_data.get('vertex_count', 0)}")
            print(f"   三角形数: {model_data.get('triangle_count', 0)}")
            
            # 验证数据格式
            vertices = model_data.get('vertices', [])
            triangles = model_data.get('triangles', [])
            
            if vertices and triangles:
                print("✅ 数据格式正确")
                
                # 检查前几个数据
                print(f"   第一个顶点: {vertices[0] if vertices else 'None'}")
                print(f"   第一个三角形: {len(triangles[0]) if triangles else 0} 个顶点")
                
                return True
            else:
                print("❌ 数据格式错误")
                return False
        else:
            print("❌ STL文件加载失败")
            return False
            
    except Exception as e:
        print(f"❌ STL文件检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主修复函数"""
    print("="*60)
    print("3D预览功能快速修复")
    print("="*60)
    
    steps = [
        ("安装依赖", install_dependencies),
        ("测试导入", test_imports),
        ("检查STL文件", check_stl_file),
        ("创建测试", create_simple_test),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        try:
            if not step_func():
                print(f"❌ {step_name} 失败")
                return 1
            print(f"✅ {step_name} 完成")
        except Exception as e:
            print(f"❌ {step_name} 异常: {e}")
            return 1
    
    print("\n" + "="*60)
    print("🎉 修复完成！")
    print("\n💡 使用说明:")
    print("1. 如果测试窗口正常显示立方体，说明3D预览功能已修复")
    print("2. 现在可以在主程序中使用'预览文件'功能")
    print("3. 如果仍有问题，请运行: python diagnose_3d_preview.py")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        
        # 保持窗口打开
        if exit_code == 0:
            try:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app:
                    print("\n🎮 测试窗口已打开，关闭窗口退出")
                    app.exec_()
            except:
                pass
        
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 修复被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 修复异常: {e}")
        sys.exit(1)

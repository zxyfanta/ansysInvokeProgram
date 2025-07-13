#!/usr/bin/env python3
"""
安装3D预览功能依赖
"""

import sys
import subprocess
from pathlib import Path

def check_conda_environment():
    """检查是否在conda环境中"""
    try:
        result = subprocess.run(['conda', 'info', '--envs'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # 检查当前环境
            current_env = subprocess.run(['conda', 'info', '--json'], 
                                       capture_output=True, text=True)
            if 'jg' in current_env.stdout:
                print("✅ 检测到conda环境 'jg'")
                return True
        return False
    except:
        return False

def install_opengl_dependencies():
    """安装OpenGL依赖"""
    print("🔧 安装OpenGL依赖...")
    
    packages = [
        'PyOpenGL',
        'PyOpenGL_accelerate'
    ]
    
    for package in packages:
        print(f"📦 安装 {package}...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {package} 安装成功")
            else:
                print(f"❌ {package} 安装失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ 安装 {package} 时出错: {e}")
            return False
    
    return True

def test_installation():
    """测试安装结果"""
    print("🧪 测试安装结果...")
    
    try:
        # 测试PyQt5
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 可用")
        
        # 测试OpenGL
        from OpenGL.GL import *
        from OpenGL.GLU import *
        print("✅ OpenGL 可用")
        
        # 测试我们的模块
        sys.path.insert(0, str(Path(__file__).parent))
        from src.gui.model_viewer_3d import Model3DViewerWidget
        from src.gui.model_loader import ModelLoader
        from src.gui.model_preview_dialog import ModelPreviewDialog
        print("✅ 3D预览模块可用")
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入测试失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def create_test_gui():
    """创建测试GUI"""
    print("🖥️ 创建测试GUI...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
        from src.gui.model_viewer_3d import Model3DViewerWidget
        
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 创建主窗口
        window = QMainWindow()
        window.setWindowTitle("3D预览功能测试")
        window.resize(800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # 添加3D预览器
        viewer = Model3DViewerWidget()
        layout.addWidget(viewer)
        
        # 添加测试按钮
        test_btn = QPushButton("加载测试立方体")
        
        def load_test_cube():
            # 创建简单的立方体数据
            vertices = [
                [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],  # 底面
                [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]       # 顶面
            ]
            
            triangles = [
                # 底面
                [vertices[0], vertices[1], vertices[2]],
                [vertices[0], vertices[2], vertices[3]],
                # 顶面
                [vertices[4], vertices[7], vertices[6]],
                [vertices[4], vertices[6], vertices[5]],
                # 前面
                [vertices[0], vertices[4], vertices[5]],
                [vertices[0], vertices[5], vertices[1]],
                # 后面
                [vertices[2], vertices[6], vertices[7]],
                [vertices[2], vertices[7], vertices[3]],
                # 左面
                [vertices[0], vertices[3], vertices[7]],
                [vertices[0], vertices[7], vertices[4]],
                # 右面
                [vertices[1], vertices[5], vertices[6]],
                [vertices[1], vertices[6], vertices[2]],
            ]
            
            test_data = {
                'vertices': vertices,
                'triangles': triangles,
                'triangle_count': len(triangles),
                'vertex_count': len(vertices),
                'format': 'test_cube'
            }
            
            viewer.load_model_data(test_data)
        
        test_btn.clicked.connect(load_test_cube)
        layout.addWidget(test_btn)
        
        # 显示窗口
        window.show()
        
        print("✅ 测试GUI已启动")
        print("🎮 操作说明:")
        print("   - 点击'加载测试立方体'按钮")
        print("   - 鼠标左键拖拽旋转")
        print("   - 鼠标滚轮缩放")
        print("   - 关闭窗口退出")
        
        return app, window
        
    except Exception as e:
        print(f"❌ 创建测试GUI失败: {e}")
        return None, None

def main():
    """主函数"""
    print("="*60)
    print("3D预览功能依赖安装程序")
    print("="*60)
    
    # 检查conda环境
    if check_conda_environment():
        print("✅ 推荐在conda环境中安装")
    else:
        print("⚠️ 未检测到conda环境，将使用pip安装")
    
    # 安装依赖
    if install_opengl_dependencies():
        print("✅ 依赖安装完成")
    else:
        print("❌ 依赖安装失败")
        return 1
    
    # 测试安装
    if test_installation():
        print("✅ 安装验证成功")
    else:
        print("❌ 安装验证失败")
        return 1
    
    # 询问是否启动测试GUI
    try:
        response = input("\n是否启动测试GUI？(y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            app, window = create_test_gui()
            if app and window:
                app.exec_()
    except KeyboardInterrupt:
        print("\n👋 用户取消")
    
    print("\n🎉 3D预览功能安装完成！")
    print("现在您可以在GUI中使用3D模型预览功能了。")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 安装被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 安装异常: {e}")
        sys.exit(1)

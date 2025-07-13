"""
3D模型预览对话框
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QTextEdit, QSplitter, QGroupBox)
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

if GUI_AVAILABLE:
    try:
        from .model_viewer_3d import Model3DViewerWidget
        from .model_loader import ModelLoader
        VIEWER_AVAILABLE = True
    except ImportError:
        VIEWER_AVAILABLE = False
else:
    VIEWER_AVAILABLE = False

class ModelPreviewDialog(QDialog):
    """3D模型预览对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_data = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("3D模型预览")
        self.setModal(True)
        self.resize(1000, 700)
        
        # 主布局
        main_layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：3D预览
        if VIEWER_AVAILABLE:
            self.viewer_widget = Model3DViewerWidget()
            splitter.addWidget(self.viewer_widget)
        else:
            # 如果3D预览不可用，显示提示
            preview_placeholder = QLabel("3D预览功能需要安装PyOpenGL库\n请运行: pip install PyOpenGL PyOpenGL_accelerate")
            preview_placeholder.setAlignment(Qt.AlignCenter)
            preview_placeholder.setStyleSheet("color: red; font-size: 14px; background-color: #f0f0f0; border: 1px solid #ccc;")
            splitter.addWidget(preview_placeholder)
        
        # 右侧：模型信息和控制
        right_panel = self.create_info_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([700, 300])
    
    def create_info_panel(self) -> QGroupBox:
        """创建信息面板"""
        panel = QGroupBox("模型信息")
        layout = QVBoxLayout(panel)
        
        # 模型信息显示
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(200)
        font = QFont("Consolas", 9)
        self.info_text.setFont(font)
        layout.addWidget(self.info_text)
        
        # 控制按钮
        if VIEWER_AVAILABLE:
            controls_group = QGroupBox("视图控制")
            controls_layout = QVBoxLayout(controls_group)
            
            # 视图控制按钮
            self.wireframe_btn = QPushButton("线框模式")
            self.wireframe_btn.setCheckable(True)
            self.wireframe_btn.clicked.connect(self.toggle_wireframe)
            controls_layout.addWidget(self.wireframe_btn)
            
            self.auto_rotate_btn = QPushButton("自动旋转")
            self.auto_rotate_btn.setCheckable(True)
            self.auto_rotate_btn.clicked.connect(self.toggle_auto_rotate)
            controls_layout.addWidget(self.auto_rotate_btn)
            
            self.reset_view_btn = QPushButton("重置视角")
            self.reset_view_btn.clicked.connect(self.reset_view)
            controls_layout.addWidget(self.reset_view_btn)
            
            layout.addWidget(controls_group)
        
        # 操作说明
        help_group = QGroupBox("操作说明")
        help_layout = QVBoxLayout(help_group)
        
        help_text = QLabel(
            "• 鼠标左键拖拽：旋转视角\n"
            "• 鼠标滚轮：缩放\n"
            "• 线框模式：切换实体/线框显示\n"
            "• 自动旋转：自动旋转模型\n"
            "• 重置视角：恢复默认视角"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 11px;")
        help_layout.addWidget(help_text)
        
        layout.addWidget(help_group)
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        layout.addStretch()
        
        return panel
    
    def load_model_from_file(self, file_path: str) -> bool:
        """从文件加载模型"""
        try:
            model_data = ModelLoader.load_model_file(file_path)
            if model_data:
                return self.load_model_data(model_data, f"文件: {Path(file_path).name}")
            else:
                return False
        except Exception as e:
            print(f"从文件加载模型失败: {e}")
            return False
    
    def load_model_data(self, model_data: Dict[str, Any], title: str = "模型预览") -> bool:
        """加载模型数据"""
        try:
            print(f"🔍 ModelPreviewDialog.load_model_data 开始")
            print(f"📊 模型数据键: {list(model_data.keys()) if model_data else 'None'}")
            print(f"🏷️ 标题: {title}")

            self.model_data = model_data
            self.setWindowTitle(f"3D模型预览 - {title}")

            # 更新信息显示
            info_text = ModelLoader.get_model_info(model_data)
            self.info_text.setPlainText(info_text)
            print(f"✅ 模型信息已更新")

            # 加载到3D预览器
            print(f"🔧 VIEWER_AVAILABLE: {VIEWER_AVAILABLE}")
            print(f"🔧 hasattr(self, 'viewer_widget'): {hasattr(self, 'viewer_widget')}")

            if VIEWER_AVAILABLE and hasattr(self, 'viewer_widget'):
                print(f"🎯 调用viewer_widget.load_model_data")
                success = self.viewer_widget.load_model_data(model_data)
                print(f"📊 viewer_widget.load_model_data 返回: {success}")

                if not success:
                    print("❌ 加载到3D预览器失败")
                    # 即使3D预览失败，也显示对话框（只显示信息）
                    return True
                else:
                    print("✅ 加载到3D预览器成功")
                    return True
            else:
                print("⚠️ 3D预览器不可用，仅显示模型信息")
                return True  # 即使没有3D预览，信息显示也算成功

        except Exception as e:
            print(f"❌ 加载模型数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_generated_model(self, model_data: Dict[str, Any], aircraft_generator) -> bool:
        """加载生成的飞行器模型"""
        try:
            # 生成网格数据
            mesh_data = aircraft_generator._generate_mesh_from_model(model_data)
            
            if mesh_data:
                model_name = model_data.get('metadata', {}).get('name', '生成的飞行器')
                return self.load_model_data(mesh_data, f"生成模型: {model_name}")
            else:
                print("无法生成网格数据")
                return False
                
        except Exception as e:
            print(f"加载生成模型失败: {e}")
            return False
    
    def toggle_wireframe(self):
        """切换线框模式"""
        if VIEWER_AVAILABLE and hasattr(self, 'viewer_widget'):
            self.viewer_widget.viewer.toggle_wireframe()
    
    def toggle_auto_rotate(self):
        """切换自动旋转"""
        if VIEWER_AVAILABLE and hasattr(self, 'viewer_widget'):
            self.viewer_widget.viewer.toggle_auto_rotate()
    
    def reset_view(self):
        """重置视角"""
        if VIEWER_AVAILABLE and hasattr(self, 'viewer_widget'):
            self.viewer_widget.viewer.reset_view()


def show_model_preview(parent, file_path: str = None, model_data: Dict[str, Any] = None, 
                      aircraft_generator = None, title: str = "模型预览"):
    """显示模型预览对话框的便捷函数"""
    try:
        dialog = ModelPreviewDialog(parent)
        
        success = False
        if file_path:
            success = dialog.load_model_from_file(file_path)
        elif model_data and aircraft_generator:
            success = dialog.load_generated_model(model_data, aircraft_generator)
        elif model_data:
            success = dialog.load_model_data(model_data, title)
        
        if success:
            dialog.exec_()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "警告", "无法加载模型数据")
    
    except Exception as e:
        print(f"显示模型预览失败: {e}")
        if GUI_AVAILABLE:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(parent, "错误", f"预览失败: {e}")

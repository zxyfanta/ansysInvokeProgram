"""
简化版3D模型预览器 - 专门解决当前加载问题
"""

import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                                QLabel, QDialog, QTextEdit, QGroupBox)
    from PyQt5.QtCore import Qt
    from PyQt5.QtOpenGL import QOpenGLWidget
    from OpenGL.GL import *
    from OpenGL.GLU import *
    DEPENDENCIES_OK = True
except ImportError as e:
    print(f"依赖导入失败: {e}")
    DEPENDENCIES_OK = False
    QOpenGLWidget = QWidget  # 占位符

class SimpleModel3DViewer(QOpenGLWidget if DEPENDENCIES_OK else QWidget):
    """简化版3D模型预览器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not DEPENDENCIES_OK:
            return
        
        # 基本参数
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = -5.0
        self.last_pos = None
        
        # 模型数据
        self.triangles = []
        self.model_loaded = False
        
        # 设置最小尺寸
        self.setMinimumSize(400, 300)
        
        print("✅ SimpleModel3DViewer 初始化完成")
    
    def initializeGL(self):
        """初始化OpenGL"""
        if not DEPENDENCIES_OK:
            return
        
        try:
            print("🔧 SimpleModel3DViewer 初始化OpenGL...")
            
            # 基本设置
            glClearColor(0.1, 0.1, 0.1, 1.0)
            glEnable(GL_DEPTH_TEST)
            
            # 简单光照
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            
            # 光源设置
            glLightfv(GL_LIGHT0, GL_POSITION, [1.0, 1.0, 1.0, 0.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
            
            print("✅ OpenGL初始化完成")
            
        except Exception as e:
            print(f"❌ OpenGL初始化失败: {e}")
    
    def resizeGL(self, width, height):
        """调整视口"""
        if not DEPENDENCIES_OK:
            return
        
        try:
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            
            aspect = width / height if height != 0 else 1
            gluPerspective(45.0, aspect, 0.1, 100.0)
            
            glMatrixMode(GL_MODELVIEW)
            
        except Exception as e:
            print(f"❌ 视口调整失败: {e}")
    
    def paintGL(self):
        """绘制场景"""
        if not DEPENDENCIES_OK:
            return
        
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            
            # 设置视角
            glTranslatef(0.0, 0.0, self.zoom)
            glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
            glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
            
            if self.model_loaded and self.triangles:
                self._draw_model()
            else:
                self._draw_placeholder()
                
        except Exception as e:
            print(f"❌ 绘制失败: {e}")
    
    def _draw_model(self):
        """绘制模型"""
        try:
            glColor3f(0.7, 0.7, 0.9)
            
            glBegin(GL_TRIANGLES)
            
            for i, triangle in enumerate(self.triangles):
                if len(triangle) != 3:
                    continue
                
                # 计算法向量
                try:
                    v0 = np.array(triangle[0], dtype=float)
                    v1 = np.array(triangle[1], dtype=float)
                    v2 = np.array(triangle[2], dtype=float)
                    
                    edge1 = v1 - v0
                    edge2 = v2 - v0
                    normal = np.cross(edge1, edge2)
                    
                    # 归一化
                    norm_length = np.linalg.norm(normal)
                    if norm_length > 1e-6:
                        normal = normal / norm_length
                    else:
                        normal = np.array([0, 0, 1])
                    
                    glNormal3f(normal[0], normal[1], normal[2])
                    
                    # 绘制顶点
                    for vertex in triangle:
                        glVertex3f(float(vertex[0]), float(vertex[1]), float(vertex[2]))
                        
                except Exception as e:
                    print(f"绘制三角形 {i} 失败: {e}")
                    continue
            
            glEnd()
            
        except Exception as e:
            print(f"❌ 模型绘制失败: {e}")
    
    def _draw_placeholder(self):
        """绘制占位符"""
        try:
            glColor3f(0.5, 0.5, 0.5)
            glBegin(GL_LINES)
            
            # 绘制坐标轴
            # X轴 - 红色
            glColor3f(1.0, 0.0, 0.0)
            glVertex3f(0.0, 0.0, 0.0)
            glVertex3f(2.0, 0.0, 0.0)
            
            # Y轴 - 绿色
            glColor3f(0.0, 1.0, 0.0)
            glVertex3f(0.0, 0.0, 0.0)
            glVertex3f(0.0, 2.0, 0.0)
            
            # Z轴 - 蓝色
            glColor3f(0.0, 0.0, 1.0)
            glVertex3f(0.0, 0.0, 0.0)
            glVertex3f(0.0, 0.0, 2.0)
            
            glEnd()
            
        except Exception as e:
            print(f"❌ 占位符绘制失败: {e}")
    
    def load_model_data(self, model_data: Dict[str, Any]) -> bool:
        """加载模型数据"""
        try:
            print("🔍 SimpleModel3DViewer.load_model_data 开始")
            
            if not DEPENDENCIES_OK:
                print("❌ 依赖不可用")
                return False
            
            if not model_data:
                print("❌ 模型数据为空")
                return False
            
            print(f"📊 模型数据键: {list(model_data.keys())}")
            
            # 检查必要的键
            if 'triangles' not in model_data:
                print("❌ 缺少triangles键")
                return False
            
            triangles = model_data['triangles']
            print(f"🔺 三角形数量: {len(triangles)}")
            
            if not triangles:
                print("❌ 三角形数据为空")
                return False
            
            # 验证数据格式
            print("🔍 验证数据格式...")
            for i, triangle in enumerate(triangles[:3]):  # 只检查前3个
                if len(triangle) != 3:
                    print(f"❌ 三角形 {i} 顶点数错误: {len(triangle)}")
                    return False
                
                for j, vertex in enumerate(triangle):
                    if len(vertex) != 3:
                        print(f"❌ 三角形 {i} 顶点 {j} 坐标数错误: {len(vertex)}")
                        return False
            
            print("✅ 数据格式验证通过")
            
            # 保存数据
            self.triangles = triangles
            self.model_loaded = True
            
            # 调整视角
            self._fit_to_view(triangles)
            
            # 重绘
            self.update()
            
            print("✅ 模型加载完成")
            return True
            
        except Exception as e:
            print(f"❌ 加载模型数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _fit_to_view(self, triangles):
        """调整视角以适应模型"""
        try:
            if not triangles:
                return
            
            # 收集所有顶点
            all_vertices = []
            for triangle in triangles:
                for vertex in triangle:
                    all_vertices.append(vertex)
            
            if not all_vertices:
                return
            
            # 计算边界框
            vertices_array = np.array(all_vertices)
            min_coords = np.min(vertices_array, axis=0)
            max_coords = np.max(vertices_array, axis=0)
            
            # 计算尺寸
            size = max_coords - min_coords
            max_size = np.max(size)
            
            # 调整缩放
            if max_size > 0:
                self.zoom = -max_size * 2.5
            
            print(f"📏 模型尺寸: {size}, 缩放: {self.zoom}")
            
        except Exception as e:
            print(f"❌ 视角调整失败: {e}")
    
    def mousePressEvent(self, event):
        """鼠标按下"""
        self.last_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        """鼠标移动"""
        if self.last_pos is None:
            return
        
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()
        
        if event.buttons() & Qt.LeftButton:
            self.rotation_x += dy * 0.5
            self.rotation_y += dx * 0.5
            self.update()
        
        self.last_pos = event.pos()
    
    def wheelEvent(self, event):
        """鼠标滚轮"""
        delta = event.angleDelta().y()
        self.zoom += delta * 0.01
        self.zoom = max(-100, min(-1, self.zoom))
        self.update()


class SimpleModelPreviewDialog(QDialog):
    """简化版模型预览对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("3D模型预览")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QHBoxLayout(self)
        
        # 左侧：3D预览
        if DEPENDENCIES_OK:
            self.viewer = SimpleModel3DViewer()
            layout.addWidget(self.viewer, 2)
        else:
            error_label = QLabel("3D预览功能需要安装PyOpenGL库\npip install PyOpenGL PyOpenGL_accelerate")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label, 2)
        
        # 右侧：信息面板
        info_panel = QGroupBox("模型信息")
        info_layout = QVBoxLayout(info_panel)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumWidth(250)
        info_layout.addWidget(self.info_text)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        info_layout.addWidget(close_btn)
        
        layout.addWidget(info_panel, 1)
    
    def load_model_data(self, model_data: Dict[str, Any], title: str = "模型预览") -> bool:
        """加载模型数据"""
        try:
            print(f"🔍 SimpleModelPreviewDialog.load_model_data")
            
            self.setWindowTitle(f"3D模型预览 - {title}")
            
            # 显示模型信息
            info_lines = []
            info_lines.append(f"格式: {model_data.get('format', 'unknown')}")
            info_lines.append(f"顶点数: {model_data.get('vertex_count', 0)}")
            info_lines.append(f"三角形数: {model_data.get('triangle_count', 0)}")
            
            self.info_text.setPlainText("\n".join(info_lines))
            
            # 加载到3D预览器
            if DEPENDENCIES_OK and hasattr(self, 'viewer'):
                return self.viewer.load_model_data(model_data)
            else:
                return True
                
        except Exception as e:
            print(f"❌ SimpleModelPreviewDialog 加载失败: {e}")
            return False


def show_simple_model_preview(parent, model_data: Dict[str, Any], title: str = "模型预览"):
    """显示简化版模型预览"""
    try:
        dialog = SimpleModelPreviewDialog(parent)
        
        if dialog.load_model_data(model_data, title):
            dialog.exec_()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(parent, "警告", "无法加载模型数据")
    
    except Exception as e:
        print(f"❌ 显示预览失败: {e}")
        if DEPENDENCIES_OK:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(parent, "错误", f"预览失败: {e}")

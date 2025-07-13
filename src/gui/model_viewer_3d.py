"""
3D模型预览器 - 基于PyOpenGL的轻量级3D预览组件
"""

import sys
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

try:
    from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
    from PyQt5.QtCore import Qt, QTimer
    from PyQt5.QtOpenGL import QOpenGLWidget
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    QOpenGLWidget = QWidget  # 占位符

class Model3DViewer(QOpenGLWidget if OPENGL_AVAILABLE else QWidget):
    """3D模型预览器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not OPENGL_AVAILABLE:
            self.setMinimumSize(400, 300)
            return
        
        # 3D场景参数
        self.rotation_x = 0
        self.rotation_y = 0
        self.zoom = -10.0
        self.last_pos = None
        
        # 模型数据
        self.vertices = []
        self.faces = []
        self.triangles = []
        self.model_loaded = False
        
        # 渲染参数
        self.wireframe_mode = False
        self.show_normals = False
        
        # 设置OpenGL格式
        self.setMinimumSize(400, 300)
        
        # 自动旋转
        self.auto_rotate = False
        self.auto_rotate_timer = QTimer()
        self.auto_rotate_timer.timeout.connect(self._auto_rotate)
    
    def initializeGL(self):
        """初始化OpenGL"""
        if not OPENGL_AVAILABLE:
            print("❌ OpenGL不可用")
            return

        try:
            print("🔧 初始化OpenGL...")

            # 设置背景色
            glClearColor(0.2, 0.2, 0.2, 1.0)

            # 启用深度测试
            glEnable(GL_DEPTH_TEST)

            # 启用光照
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)

            # 设置光源
            light_pos = [5.0, 5.0, 5.0, 1.0]
            light_ambient = [0.3, 0.3, 0.3, 1.0]
            light_diffuse = [0.8, 0.8, 0.8, 1.0]
            light_specular = [1.0, 1.0, 1.0, 1.0]

            glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
            glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
            glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
            glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

            # 设置材质
            material_ambient = [0.2, 0.2, 0.2, 1.0]
            material_diffuse = [0.6, 0.6, 0.8, 1.0]
            material_specular = [1.0, 1.0, 1.0, 1.0]
            material_shininess = [50.0]

            glMaterialfv(GL_FRONT, GL_AMBIENT, material_ambient)
            glMaterialfv(GL_FRONT, GL_DIFFUSE, material_diffuse)
            glMaterialfv(GL_FRONT, GL_SPECULAR, material_specular)
            glMaterialfv(GL_FRONT, GL_SHININESS, material_shininess)

            # 启用颜色材质
            glEnable(GL_COLOR_MATERIAL)
            glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

            print("✅ OpenGL初始化完成")

        except Exception as e:
            print(f"❌ OpenGL初始化失败: {e}")
            import traceback
            traceback.print_exc()
    
    def resizeGL(self, width, height):
        """调整视口大小"""
        if not OPENGL_AVAILABLE:
            return
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        aspect = width / height if height != 0 else 1
        gluPerspective(45.0, aspect, 0.1, 100.0)
        
        glMatrixMode(GL_MODELVIEW)
    
    def paintGL(self):
        """绘制场景"""
        if not OPENGL_AVAILABLE:
            return
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        
        # 设置视角
        glTranslatef(0.0, 0.0, self.zoom)
        glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
        glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
        
        if self.model_loaded:
            self._draw_model()
        else:
            self._draw_placeholder()
    
    def _draw_model(self):
        """绘制模型"""
        if not self.triangles:
            print("⚠️ 没有三角形数据可绘制")
            return

        try:
            print(f"🎨 开始绘制模型，三角形数: {len(self.triangles)}")

            if self.wireframe_mode:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                glDisable(GL_LIGHTING)
                glColor3f(0.8, 0.8, 0.8)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glEnable(GL_LIGHTING)
                glColor3f(0.6, 0.6, 0.8)

            glBegin(GL_TRIANGLES)

            triangle_count = 0
            for triangle in self.triangles:
                try:
                    # 验证三角形数据
                    if len(triangle) != 3:
                        print(f"⚠️ 三角形 {triangle_count} 顶点数不正确: {len(triangle)}")
                        continue

                    # 计算法向量
                    v0 = np.array(triangle[0])
                    v1 = np.array(triangle[1])
                    v2 = np.array(triangle[2])

                    edge1 = v1 - v0
                    edge2 = v2 - v0
                    normal = np.cross(edge1, edge2)
                    norm_length = np.linalg.norm(normal)
                    if norm_length > 0:
                        normal = normal / norm_length
                    else:
                        normal = [0, 0, 1]

                    glNormal3f(float(normal[0]), float(normal[1]), float(normal[2]))

                    # 绘制顶点
                    for vertex in triangle:
                        glVertex3f(float(vertex[0]), float(vertex[1]), float(vertex[2]))

                    triangle_count += 1

                except Exception as e:
                    print(f"❌ 绘制三角形 {triangle_count} 失败: {e}")
                    continue

            glEnd()

            # 恢复设置
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            glEnable(GL_LIGHTING)

            print(f"✅ 模型绘制完成，成功绘制 {triangle_count} 个三角形")

        except Exception as e:
            print(f"❌ 绘制模型失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _draw_placeholder(self):
        """绘制占位符（立方体）"""
        glColor3f(0.5, 0.5, 0.5)
        
        # 绘制线框立方体
        glBegin(GL_LINES)
        
        # 底面
        glVertex3f(-1, -1, -1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, 1, -1)
        glVertex3f(-1, 1, -1)
        glVertex3f(-1, 1, -1)
        glVertex3f(-1, -1, -1)
        
        # 顶面
        glVertex3f(-1, -1, 1)
        glVertex3f(1, -1, 1)
        glVertex3f(1, -1, 1)
        glVertex3f(1, 1, 1)
        glVertex3f(1, 1, 1)
        glVertex3f(-1, 1, 1)
        glVertex3f(-1, 1, 1)
        glVertex3f(-1, -1, 1)
        
        # 垂直边
        glVertex3f(-1, -1, -1)
        glVertex3f(-1, -1, 1)
        glVertex3f(1, -1, -1)
        glVertex3f(1, -1, 1)
        glVertex3f(1, 1, -1)
        glVertex3f(1, 1, 1)
        glVertex3f(-1, 1, -1)
        glVertex3f(-1, 1, 1)
        
        glEnd()
    
    def load_model_data(self, model_data: Dict[str, Any]):
        """加载模型数据"""
        try:
            print(f"🔍 开始加载模型数据...")
            print(f"📊 数据键: {list(model_data.keys())}")

            if 'vertices' in model_data and 'triangles' in model_data:
                vertices = model_data['vertices']
                triangles = model_data['triangles']

                print(f"📈 顶点数: {len(vertices)}")
                print(f"🔺 三角形数: {len(triangles)}")

                # 验证数据格式
                if not self._validate_model_data(vertices, triangles):
                    print("❌ 模型数据验证失败")
                    return False

                # 转换数据格式
                self.vertices = self._convert_vertices(vertices)
                self.triangles = self._convert_triangles(triangles)
                self.model_loaded = True

                print(f"✅ 数据转换完成")

                # 计算模型边界框并调整视角
                self._fit_model_to_view()

                # 强制重绘
                self.update()
                print(f"🎨 模型加载完成，已触发重绘")
                return True
            else:
                missing_keys = []
                if 'vertices' not in model_data:
                    missing_keys.append('vertices')
                if 'triangles' not in model_data:
                    missing_keys.append('triangles')
                print(f"❌ 模型数据格式不正确，缺少键: {missing_keys}")
                return False
        except Exception as e:
            print(f"❌ 加载模型失败: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _validate_model_data(self, vertices, triangles):
        """验证模型数据"""
        try:
            # 检查顶点数据
            if not vertices:
                print("❌ 顶点数据为空")
                return False

            # 检查三角形数据
            if not triangles:
                print("❌ 三角形数据为空")
                return False

            # 检查顶点格式
            for i, vertex in enumerate(vertices[:5]):  # 只检查前5个
                if not isinstance(vertex, (list, tuple)) or len(vertex) != 3:
                    print(f"❌ 顶点 {i} 格式错误: {vertex}")
                    return False
                try:
                    [float(x) for x in vertex]
                except:
                    print(f"❌ 顶点 {i} 包含非数值: {vertex}")
                    return False

            # 检查三角形格式
            for i, triangle in enumerate(triangles[:5]):  # 只检查前5个
                if not isinstance(triangle, (list, tuple)) or len(triangle) != 3:
                    print(f"❌ 三角形 {i} 格式错误: {triangle}")
                    return False
                for j, vertex in enumerate(triangle):
                    if not isinstance(vertex, (list, tuple)) or len(vertex) != 3:
                        print(f"❌ 三角形 {i} 顶点 {j} 格式错误: {vertex}")
                        return False

            print("✅ 模型数据验证通过")
            return True

        except Exception as e:
            print(f"❌ 数据验证异常: {e}")
            return False

    def _convert_vertices(self, vertices):
        """转换顶点数据"""
        try:
            converted = []
            for vertex in vertices:
                converted.append([float(vertex[0]), float(vertex[1]), float(vertex[2])])
            return converted
        except Exception as e:
            print(f"❌ 顶点转换失败: {e}")
            return vertices

    def _convert_triangles(self, triangles):
        """转换三角形数据"""
        try:
            converted = []
            for triangle in triangles:
                triangle_coords = []
                for vertex in triangle:
                    triangle_coords.append([float(vertex[0]), float(vertex[1]), float(vertex[2])])
                converted.append(triangle_coords)
            return converted
        except Exception as e:
            print(f"❌ 三角形转换失败: {e}")
            return triangles
    
    def _fit_model_to_view(self):
        """调整视角以适应模型"""
        if not self.vertices:
            return
        
        vertices_array = np.array(self.vertices)
        min_coords = np.min(vertices_array, axis=0)
        max_coords = np.max(vertices_array, axis=0)
        
        # 计算模型尺寸
        size = max_coords - min_coords
        max_size = np.max(size)
        
        # 调整缩放
        if max_size > 0:
            self.zoom = -max_size * 2
        else:
            self.zoom = -10.0
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        self.last_pos = event.pos()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
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
        """鼠标滚轮事件"""
        delta = event.angleDelta().y()
        self.zoom += delta * 0.01
        self.zoom = max(-100, min(-1, self.zoom))
        self.update()
    
    def toggle_wireframe(self):
        """切换线框模式"""
        self.wireframe_mode = not self.wireframe_mode
        self.update()
    
    def toggle_auto_rotate(self):
        """切换自动旋转"""
        self.auto_rotate = not self.auto_rotate
        if self.auto_rotate:
            self.auto_rotate_timer.start(50)  # 20 FPS
        else:
            self.auto_rotate_timer.stop()
    
    def _auto_rotate(self):
        """自动旋转"""
        self.rotation_y += 1
        self.update()
    
    def reset_view(self):
        """重置视角"""
        self.rotation_x = 0
        self.rotation_y = 0
        if self.model_loaded:
            self._fit_model_to_view()
        else:
            self.zoom = -10.0
        self.update()


class Model3DViewerWidget(QWidget):
    """3D模型预览器组件（包含控制按钮）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 3D预览器
        if OPENGL_AVAILABLE:
            self.viewer = Model3DViewer()
            layout.addWidget(self.viewer)
            
            # 控制按钮
            controls_layout = QHBoxLayout()
            
            self.wireframe_btn = QPushButton("线框模式")
            self.wireframe_btn.setCheckable(True)
            self.wireframe_btn.clicked.connect(self.viewer.toggle_wireframe)
            controls_layout.addWidget(self.wireframe_btn)
            
            self.auto_rotate_btn = QPushButton("自动旋转")
            self.auto_rotate_btn.setCheckable(True)
            self.auto_rotate_btn.clicked.connect(self.viewer.toggle_auto_rotate)
            controls_layout.addWidget(self.auto_rotate_btn)
            
            self.reset_btn = QPushButton("重置视角")
            self.reset_btn.clicked.connect(self.viewer.reset_view)
            controls_layout.addWidget(self.reset_btn)
            
            controls_layout.addStretch()
            
            layout.addLayout(controls_layout)
        else:
            # OpenGL不可用时的提示
            error_label = QLabel("3D预览功能需要安装PyOpenGL库\n请运行: pip install PyOpenGL PyOpenGL_accelerate")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px;")
            layout.addWidget(error_label)
    
    def load_model_data(self, model_data: Dict[str, Any]) -> bool:
        """加载模型数据"""
        try:
            print("🔍 Model3DViewerWidget.load_model_data 开始")
            print(f"📊 OPENGL_AVAILABLE: {OPENGL_AVAILABLE}")
            print(f"🔧 hasattr(self, 'viewer'): {hasattr(self, 'viewer')}")

            if not OPENGL_AVAILABLE:
                print("❌ OpenGL不可用")
                return False

            if not hasattr(self, 'viewer'):
                print("❌ 没有viewer属性")
                return False

            print("🎯 调用viewer.load_model_data")
            result = self.viewer.load_model_data(model_data)
            print(f"📊 viewer.load_model_data 返回: {result}")

            return result

        except Exception as e:
            print(f"❌ Model3DViewerWidget.load_model_data 异常: {e}")
            import traceback
            traceback.print_exc()
            return False

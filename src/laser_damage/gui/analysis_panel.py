"""
分析结果面板

显示激光毁伤仿真的分析结果，包括温度场、应力场等可视化。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.patches as patches

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QComboBox, QSlider, QCheckBox, QTextEdit, QSplitter,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
from typing import Dict, Any, Optional, List


class AnalysisPanel(QWidget):
    """分析结果面板"""
    
    # 信号定义
    export_requested = pyqtSignal(str, str)  # 导出请求信号 (数据类型, 文件路径)
    
    def __init__(self):
        super().__init__()
        self.simulation_results: Optional[Dict[str, Any]] = None
        self.init_ui()
        self.generate_sample_data()  # 生成示例数据用于界面展示
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：结果概览和控制面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：可视化区域
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([300, 800])
        
        layout.addWidget(splitter)
    
    def create_left_panel(self) -> QWidget:
        """创建左侧控制面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 结果概览组
        overview_group = QGroupBox("仿真结果概览")
        overview_layout = QVBoxLayout(overview_group)
        
        # 结果统计表格
        self.results_table = QTableWidget(0, 2)
        self.results_table.setHorizontalHeaderLabels(["参数", "数值"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setMaximumHeight(200)
        overview_layout.addWidget(self.results_table)
        
        layout.addWidget(overview_group)
        
        # 显示控制组
        control_group = QGroupBox("显示控制")
        control_layout = QVBoxLayout(control_group)
        
        # 数据类型选择
        data_type_layout = QHBoxLayout()
        data_type_layout.addWidget(QLabel("数据类型:"))
        
        self.data_type_combo = QComboBox()
        self.data_type_combo.addItems(["温度场", "应力场", "位移场", "损伤分布"])
        self.data_type_combo.currentTextChanged.connect(self.update_visualization)
        data_type_layout.addWidget(self.data_type_combo)
        
        control_layout.addLayout(data_type_layout)
        
        # 颜色映射选择
        colormap_layout = QHBoxLayout()
        colormap_layout.addWidget(QLabel("颜色映射:"))
        
        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(["hot", "viridis", "plasma", "coolwarm", "jet"])
        self.colormap_combo.currentTextChanged.connect(self.update_visualization)
        colormap_layout.addWidget(self.colormap_combo)
        
        control_layout.addLayout(colormap_layout)
        
        # 显示选项
        self.show_contour_check = QCheckBox("显示等值线")
        self.show_contour_check.setChecked(True)
        self.show_contour_check.toggled.connect(self.update_visualization)
        control_layout.addWidget(self.show_contour_check)
        
        self.show_colorbar_check = QCheckBox("显示颜色条")
        self.show_colorbar_check.setChecked(True)
        self.show_colorbar_check.toggled.connect(self.update_visualization)
        control_layout.addWidget(self.show_colorbar_check)
        
        # 数值范围控制
        range_label = QLabel("显示范围:")
        control_layout.addWidget(range_label)
        
        self.min_slider = QSlider(Qt.Horizontal)
        self.min_slider.setRange(0, 100)
        self.min_slider.setValue(0)
        self.min_slider.valueChanged.connect(self.update_visualization)
        control_layout.addWidget(QLabel("最小值:"))
        control_layout.addWidget(self.min_slider)
        
        self.max_slider = QSlider(Qt.Horizontal)
        self.max_slider.setRange(0, 100)
        self.max_slider.setValue(100)
        self.max_slider.valueChanged.connect(self.update_visualization)
        control_layout.addWidget(QLabel("最大值:"))
        control_layout.addWidget(self.max_slider)
        
        layout.addWidget(control_group)
        
        # 导出控制组
        export_group = QGroupBox("数据导出")
        export_layout = QVBoxLayout(export_group)
        
        # 导出图片按钮
        export_image_btn = QPushButton("导出图片")
        export_image_btn.clicked.connect(self.export_image)
        export_layout.addWidget(export_image_btn)
        
        # 导出数据按钮
        export_data_btn = QPushButton("导出数据")
        export_data_btn.clicked.connect(self.export_data)
        export_layout.addWidget(export_data_btn)
        
        # 生成报告按钮
        generate_report_btn = QPushButton("生成分析报告")
        generate_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        generate_report_btn.clicked.connect(self.generate_analysis_report)
        export_layout.addWidget(generate_report_btn)
        
        layout.addWidget(export_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        return widget
    
    def create_right_panel(self) -> QWidget:
        """创建右侧可视化面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建标签页
        self.viz_tabs = QTabWidget()
        
        # 2D可视化标签页
        viz_2d_tab = self.create_2d_visualization_tab()
        self.viz_tabs.addTab(viz_2d_tab, "2D可视化")
        
        # 3D可视化标签页
        viz_3d_tab = self.create_3d_visualization_tab()
        self.viz_tabs.addTab(viz_3d_tab, "3D可视化")
        
        # 数据分析标签页
        data_analysis_tab = self.create_data_analysis_tab()
        self.viz_tabs.addTab(data_analysis_tab, "数据分析")
        
        layout.addWidget(self.viz_tabs)
        
        return widget
    
    def create_2d_visualization_tab(self) -> QWidget:
        """创建2D可视化标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建matplotlib图形
        self.figure_2d = Figure(figsize=(10, 8))
        self.canvas_2d = FigureCanvas(self.figure_2d)
        layout.addWidget(self.canvas_2d)
        
        return widget
    
    def create_3d_visualization_tab(self) -> QWidget:
        """创建3D可视化标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 创建3D matplotlib图形
        self.figure_3d = Figure(figsize=(10, 8))
        self.canvas_3d = FigureCanvas(self.figure_3d)
        layout.addWidget(self.canvas_3d)
        
        # 3D控制按钮
        control_layout = QHBoxLayout()
        
        rotate_btn = QPushButton("旋转视角")
        rotate_btn.clicked.connect(self.rotate_3d_view)
        control_layout.addWidget(rotate_btn)
        
        reset_view_btn = QPushButton("重置视角")
        reset_view_btn.clicked.connect(self.reset_3d_view)
        control_layout.addWidget(reset_view_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        return widget
    
    def create_data_analysis_tab(self) -> QWidget:
        """创建数据分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 统计信息组
        stats_group = QGroupBox("统计信息")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setMaximumHeight(150)
        stats_layout.addWidget(self.stats_text)
        
        layout.addWidget(stats_group)
        
        # 历史曲线图
        history_group = QGroupBox("时间历程曲线")
        history_layout = QVBoxLayout(history_group)
        
        self.figure_history = Figure(figsize=(10, 4))
        self.canvas_history = FigureCanvas(self.figure_history)
        history_layout.addWidget(self.canvas_history)
        
        layout.addWidget(history_group)
        
        return widget
    
    def generate_sample_data(self):
        """生成示例数据用于界面展示"""
        # 生成示例温度场数据
        x = np.linspace(0, 10, 50)
        y = np.linspace(0, 10, 50)
        X, Y = np.meshgrid(x, y)
        
        # 模拟激光加热的温度分布
        center_x, center_y = 5, 5
        temperature = 293.15 + 800 * np.exp(-((X - center_x)**2 + (Y - center_y)**2) / 4)
        
        # 生成示例应力场数据
        stress = 50e6 * np.exp(-((X - center_x)**2 + (Y - center_y)**2) / 8)
        
        # 生成示例位移场数据
        displacement = 0.1 * np.exp(-((X - center_x)**2 + (Y - center_y)**2) / 6)
        
        self.simulation_results = {
            "temperature_field": temperature,
            "stress_field": stress,
            "displacement_field": displacement,
            "coordinates": (X, Y),
            "max_temperature": np.max(temperature),
            "min_temperature": np.min(temperature),
            "max_stress": np.max(stress),
            "max_displacement": np.max(displacement)
        }
        
        # 更新结果概览表格
        self.update_results_table()
        
        # 更新可视化
        self.update_visualization()
    
    def update_results_table(self):
        """更新结果概览表格"""
        if not self.simulation_results:
            return
        
        data = [
            ("最高温度", f"{self.simulation_results['max_temperature']:.1f} K"),
            ("最低温度", f"{self.simulation_results['min_temperature']:.1f} K"),
            ("最大应力", f"{self.simulation_results['max_stress']/1e6:.1f} MPa"),
            ("最大位移", f"{self.simulation_results['max_displacement']*1000:.2f} mm"),
            ("温度梯度", f"{(self.simulation_results['max_temperature'] - self.simulation_results['min_temperature']):.1f} K"),
        ]
        
        self.results_table.setRowCount(len(data))
        
        for i, (param, value) in enumerate(data):
            self.results_table.setItem(i, 0, QTableWidgetItem(param))
            self.results_table.setItem(i, 1, QTableWidgetItem(value))
    
    def update_visualization(self):
        """更新可视化显示"""
        if not self.simulation_results:
            return
        
        # 获取当前选择的数据类型
        data_type = self.data_type_combo.currentText()
        colormap = self.colormap_combo.currentText()
        
        # 选择对应的数据
        if data_type == "温度场":
            data = self.simulation_results["temperature_field"]
            title = "Temperature Distribution (K)"
            unit = "K"
        elif data_type == "应力场":
            data = self.simulation_results["stress_field"]
            title = "Stress Distribution (Pa)"
            unit = "MPa"
            data = data / 1e6  # 转换为MPa
        elif data_type == "位移场":
            data = self.simulation_results["displacement_field"]
            title = "Displacement Distribution (mm)"
            unit = "mm"
            data = data * 1000  # 转换为mm
        else:  # 损伤分布
            # 基于温度计算损伤
            temp_data = self.simulation_results["temperature_field"]
            melting_point = 933.15  # 铝的熔点
            data = np.where(temp_data > melting_point, 1.0, 0.0)
            title = "Damage Distribution"
            unit = ""
        
        # 更新2D可视化
        self.update_2d_plot(data, title, unit, colormap)
        
        # 更新3D可视化
        self.update_3d_plot(data, title, unit, colormap)
        
        # 更新统计信息
        self.update_statistics(data, data_type)
    
    def update_2d_plot(self, data, title, unit, colormap):
        """更新2D图形"""
        self.figure_2d.clear()
        ax = self.figure_2d.add_subplot(111)
        
        X, Y = self.simulation_results["coordinates"]
        
        # 应用范围控制
        min_val = np.min(data) + (np.max(data) - np.min(data)) * self.min_slider.value() / 100
        max_val = np.min(data) + (np.max(data) - np.min(data)) * self.max_slider.value() / 100
        
        # 绘制填充等值线图
        contourf = ax.contourf(X, Y, data, levels=20, cmap=colormap, vmin=min_val, vmax=max_val)
        
        # 绘制等值线
        if self.show_contour_check.isChecked():
            contour = ax.contour(X, Y, data, levels=10, colors='black', alpha=0.3, linewidths=0.5)
            ax.clabel(contour, inline=True, fontsize=8)
        
        # 添加颜色条
        if self.show_colorbar_check.isChecked():
            cbar = self.figure_2d.colorbar(contourf, ax=ax)
            cbar.set_label(unit)
        
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_title(title)
        ax.set_aspect('equal')
        
        self.canvas_2d.draw()
    
    def update_3d_plot(self, data, title, unit, colormap):
        """更新3D图形"""
        self.figure_3d.clear()
        ax = self.figure_3d.add_subplot(111, projection='3d')
        
        X, Y = self.simulation_results["coordinates"]
        
        # 创建3D表面图
        surf = ax.plot_surface(X, Y, data, cmap=colormap, alpha=0.8)
        
        # 添加颜色条
        if self.show_colorbar_check.isChecked():
            self.figure_3d.colorbar(surf, ax=ax, shrink=0.5, aspect=5, label=unit)
        
        ax.set_xlabel('X (mm)')
        ax.set_ylabel('Y (mm)')
        ax.set_zlabel(unit)
        ax.set_title(title)
        
        self.canvas_3d.draw()
    
    def update_statistics(self, data, data_type):
        """更新统计信息"""
        stats_text = f"=== {data_type} 统计信息 ===\n\n"
        stats_text += f"最大值: {np.max(data):.3f}\n"
        stats_text += f"最小值: {np.min(data):.3f}\n"
        stats_text += f"平均值: {np.mean(data):.3f}\n"
        stats_text += f"标准差: {np.std(data):.3f}\n"
        stats_text += f"中位数: {np.median(data):.3f}\n"
        
        # 计算百分位数
        p25 = np.percentile(data, 25)
        p75 = np.percentile(data, 75)
        stats_text += f"25%分位数: {p25:.3f}\n"
        stats_text += f"75%分位数: {p75:.3f}\n"
        
        self.stats_text.setText(stats_text)
        
        # 更新历史曲线（模拟时间历程）
        self.update_history_plot(data_type)
    
    def update_history_plot(self, data_type):
        """更新历史曲线图"""
        self.figure_history.clear()
        ax = self.figure_history.add_subplot(111)
        
        # 生成模拟的时间历程数据
        time = np.linspace(0, 10, 100)  # 10秒的仿真时间
        
        if data_type == "温度场":
            # 模拟温度随时间的变化
            max_temp = 293.15 + 800 * (1 - np.exp(-time/2))
            ax.plot(time, max_temp, 'r-', linewidth=2, label='最高温度')
            ax.set_ylabel('温度 (K)')
        elif data_type == "应力场":
            # 模拟应力随时间的变化
            max_stress = 50 * (1 - np.exp(-time/3))
            ax.plot(time, max_stress, 'b-', linewidth=2, label='最大应力')
            ax.set_ylabel('应力 (MPa)')
        else:
            # 模拟位移随时间的变化
            max_disp = 0.1 * (1 - np.exp(-time/4))
            ax.plot(time, max_disp, 'g-', linewidth=2, label='最大位移')
            ax.set_ylabel('位移 (mm)')
        
        ax.set_xlabel('时间 (s)')
        ax.set_title(f'{data_type}时间历程')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        self.canvas_history.draw()
    
    def rotate_3d_view(self):
        """旋转3D视角"""
        if hasattr(self, 'figure_3d'):
            ax = self.figure_3d.gca(projection='3d')
            ax.view_init(elev=ax.elev + 10, azim=ax.azim + 10)
            self.canvas_3d.draw()
    
    def reset_3d_view(self):
        """重置3D视角"""
        if hasattr(self, 'figure_3d'):
            ax = self.figure_3d.gca(projection='3d')
            ax.view_init(elev=30, azim=45)
            self.canvas_3d.draw()
    
    def export_image(self):
        """导出图片"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出图片', '', 
            'PNG Files (*.png);;JPEG Files (*.jpg);;All Files (*)'
        )
        
        if file_path:
            try:
                current_tab = self.viz_tabs.currentIndex()
                if current_tab == 0:  # 2D可视化
                    self.figure_2d.savefig(file_path, dpi=300, bbox_inches='tight')
                elif current_tab == 1:  # 3D可视化
                    self.figure_3d.savefig(file_path, dpi=300, bbox_inches='tight')
                else:  # 数据分析
                    self.figure_history.savefig(file_path, dpi=300, bbox_inches='tight')
                
                QMessageBox.information(self, '导出成功', f'图片已保存到: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '导出失败', f'导出图片失败: {str(e)}')
    
    def export_data(self):
        """导出数据"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出数据', '', 
            'CSV Files (*.csv);;Excel Files (*.xlsx);;All Files (*)'
        )
        
        if file_path:
            try:
                # 这里实现数据导出逻辑
                QMessageBox.information(self, '导出成功', f'数据已保存到: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '导出失败', f'导出数据失败: {str(e)}')
    
    def generate_analysis_report(self):
        """生成分析报告"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, '生成报告', '分析报告生成功能将在报告面板中实现')
    
    def load_simulation_results(self, results: Dict[str, Any]):
        """加载仿真结果"""
        self.simulation_results = results
        self.update_results_table()
        self.update_visualization()
    
    def reset(self):
        """重置面板"""
        self.simulation_results = None
        self.results_table.setRowCount(0)
        
        # 清空图形
        if hasattr(self, 'figure_2d'):
            self.figure_2d.clear()
            self.canvas_2d.draw()
        
        if hasattr(self, 'figure_3d'):
            self.figure_3d.clear()
            self.canvas_3d.draw()
        
        if hasattr(self, 'figure_history'):
            self.figure_history.clear()
            self.canvas_history.draw()
        
        self.stats_text.clear()

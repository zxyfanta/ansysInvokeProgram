"""
GUI - 图表查看器

图表显示组件。
"""

import os
from typing import List

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
        QLabel, QListWidget, QListWidgetItem, QSplitter,
        QPushButton, QGroupBox, QGridLayout, QComboBox
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QPixmap, QFont
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

class ChartViewer(QWidget):
    """图表查看器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5不可用，无法创建图表查看器")
        
        self.chart_files = []
        self.current_chart_index = 0
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QHBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧图表列表
        self.create_chart_list(splitter)
        
        # 右侧图表显示区域
        self.create_chart_display(splitter)
        
        # 设置分割器比例
        splitter.setSizes([200, 800])
    
    def create_chart_list(self, parent):
        """创建图表列表"""
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        # 图表分类
        category_group = QGroupBox("图表分类")
        category_layout = QVBoxLayout(category_group)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["全部", "毁伤分析", "轨迹分析", "对比分析", "综合分析"])
        self.category_combo.currentTextChanged.connect(self.filter_charts)
        category_layout.addWidget(self.category_combo)
        
        list_layout.addWidget(category_group)
        
        # 图表列表
        charts_group = QGroupBox("图表列表")
        charts_layout = QVBoxLayout(charts_group)
        
        self.chart_list = QListWidget()
        self.chart_list.itemClicked.connect(self.on_chart_selected)
        charts_layout.addWidget(self.chart_list)
        
        list_layout.addWidget(charts_group)
        
        # 控制按钮
        buttons_group = QGroupBox("控制")
        buttons_layout = QVBoxLayout(buttons_group)
        
        self.prev_btn = QPushButton("上一张")
        self.prev_btn.clicked.connect(self.show_previous_chart)
        buttons_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("下一张")
        self.next_btn.clicked.connect(self.show_next_chart)
        buttons_layout.addWidget(self.next_btn)
        
        self.export_btn = QPushButton("导出图表")
        self.export_btn.clicked.connect(self.export_current_chart)
        buttons_layout.addWidget(self.export_btn)
        
        list_layout.addWidget(buttons_group)
        
        parent.addWidget(list_widget)
    
    def create_chart_display(self, parent):
        """创建图表显示区域"""
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)
        
        # 图表信息
        info_group = QGroupBox("图表信息")
        info_layout = QVBoxLayout(info_group)
        
        self.chart_title_label = QLabel("未选择图表")
        self.chart_title_label.setAlignment(Qt.AlignCenter)
        self.chart_title_label.setFont(QFont("Arial", 14, QFont.Bold))
        info_layout.addWidget(self.chart_title_label)
        
        self.chart_info_label = QLabel("")
        self.chart_info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.chart_info_label)
        
        display_layout.addWidget(info_group)
        
        # 图表显示区域
        chart_group = QGroupBox("图表显示")
        chart_layout = QVBoxLayout(chart_group)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignCenter)
        
        # 图表标签
        self.chart_label = QLabel("请选择要查看的图表")
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                padding: 50px;
                font-size: 16px;
                color: #7f8c8d;
            }
        """)
        self.chart_label.setMinimumSize(600, 400)
        
        self.scroll_area.setWidget(self.chart_label)
        chart_layout.addWidget(self.scroll_area)
        
        display_layout.addWidget(chart_group)
        
        parent.addWidget(display_widget)
    
    def load_charts(self, chart_files: List[str]):
        """加载图表文件"""
        self.chart_files = [f for f in chart_files if os.path.exists(f)]
        self.current_chart_index = 0
        
        # 更新图表列表
        self.update_chart_list()
        
        # 显示第一张图表
        if self.chart_files:
            self.show_chart(0)
        else:
            self.chart_label.setText("没有可显示的图表")
    
    def update_chart_list(self):
        """更新图表列表"""
        self.chart_list.clear()
        
        category = self.category_combo.currentText()
        
        for i, chart_file in enumerate(self.chart_files):
            chart_name = os.path.basename(chart_file)
            
            # 根据分类过滤
            if category != "全部":
                if category == "毁伤分析" and not any(keyword in chart_name.lower() 
                    for keyword in ["temperature", "stress", "damage"]):
                    continue
                elif category == "轨迹分析" and not any(keyword in chart_name.lower() 
                    for keyword in ["trajectory", "altitude", "velocity", "attitude"]):
                    continue
                elif category == "对比分析" and not any(keyword in chart_name.lower() 
                    for keyword in ["comparison", "degradation", "deviation"]):
                    continue
                elif category == "综合分析" and not any(keyword in chart_name.lower() 
                    for keyword in ["comprehensive", "dashboard", "summary"]):
                    continue
            
            item = QListWidgetItem(chart_name)
            item.setData(Qt.UserRole, i)  # 存储原始索引
            self.chart_list.addItem(item)
        
        # 更新按钮状态
        self.update_button_states()
    
    def filter_charts(self):
        """过滤图表"""
        self.update_chart_list()
    
    def on_chart_selected(self, item):
        """图表选择处理"""
        chart_index = item.data(Qt.UserRole)
        self.show_chart(chart_index)
    
    def show_chart(self, index: int):
        """显示指定索引的图表"""
        if 0 <= index < len(self.chart_files):
            self.current_chart_index = index
            chart_file = self.chart_files[index]
            
            # 加载图片
            pixmap = QPixmap(chart_file)
            if not pixmap.isNull():
                # 缩放图片以适应显示区域
                scaled_pixmap = pixmap.scaled(
                    800, 600, 
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
                self.chart_label.setPixmap(scaled_pixmap)
                self.chart_label.setText("")
                
                # 更新图表信息
                chart_name = os.path.basename(chart_file)
                self.chart_title_label.setText(chart_name)
                
                file_size = os.path.getsize(chart_file)
                self.chart_info_label.setText(f"文件大小: {file_size/1024:.1f} KB | 索引: {index+1}/{len(self.chart_files)}")
                
            else:
                self.chart_label.setText(f"无法加载图表: {os.path.basename(chart_file)}")
                self.chart_label.setPixmap(QPixmap())
            
            # 更新按钮状态
            self.update_button_states()
            
            # 更新列表选择
            self.update_list_selection(index)
    
    def show_previous_chart(self):
        """显示上一张图表"""
        if self.current_chart_index > 0:
            self.show_chart(self.current_chart_index - 1)
    
    def show_next_chart(self):
        """显示下一张图表"""
        if self.current_chart_index < len(self.chart_files) - 1:
            self.show_chart(self.current_chart_index + 1)
    
    def update_button_states(self):
        """更新按钮状态"""
        has_charts = len(self.chart_files) > 0
        
        self.prev_btn.setEnabled(has_charts and self.current_chart_index > 0)
        self.next_btn.setEnabled(has_charts and self.current_chart_index < len(self.chart_files) - 1)
        self.export_btn.setEnabled(has_charts)
    
    def update_list_selection(self, chart_index: int):
        """更新列表选择"""
        for i in range(self.chart_list.count()):
            item = self.chart_list.item(i)
            if item.data(Qt.UserRole) == chart_index:
                self.chart_list.setCurrentItem(item)
                break
    
    def export_current_chart(self):
        """导出当前图表"""
        if 0 <= self.current_chart_index < len(self.chart_files):
            try:
                from PyQt5.QtWidgets import QFileDialog
                
                current_file = self.chart_files[self.current_chart_index]
                file_name = os.path.basename(current_file)
                
                save_path, _ = QFileDialog.getSaveFileName(
                    self, '导出图表', file_name,
                    'PNG文件 (*.png);;JPEG文件 (*.jpg);;所有文件 (*)'
                )
                
                if save_path:
                    import shutil
                    shutil.copy2(current_file, save_path)
                    
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.information(self, "导出成功", f"图表已导出到:\n{save_path}")
                    
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(self, "导出失败", f"导出图表失败:\n{str(e)}")
    
    def clear_charts(self):
        """清空图表"""
        self.chart_files = []
        self.current_chart_index = 0
        
        self.chart_list.clear()
        self.chart_label.setPixmap(QPixmap())
        self.chart_label.setText("请选择要查看的图表")
        self.chart_title_label.setText("未选择图表")
        self.chart_info_label.setText("")
        
        self.update_button_states()
    
    def get_current_chart_file(self) -> str:
        """获取当前图表文件路径"""
        if 0 <= self.current_chart_index < len(self.chart_files):
            return self.chart_files[self.current_chart_index]
        return ""
    
    def get_chart_count(self) -> int:
        """获取图表数量"""
        return len(self.chart_files)

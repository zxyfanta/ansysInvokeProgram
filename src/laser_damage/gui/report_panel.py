"""
报告生成面板

提供仿真结果报告的生成和管理功能。
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton, QCheckBox,
    QListWidget, QListWidgetItem, QTabWidget, QFormLayout, QSpinBox,
    QFileDialog, QMessageBox, QProgressBar, QSplitter, QTreeWidget,
    QTreeWidgetItem, QDateEdit, QTimeEdit
)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPixmap, QIcon
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
from datetime import datetime


class ReportGenerationThread(QThread):
    """报告生成线程"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    finished = pyqtSignal(str)  # 完成信号，传递报告文件路径
    error_occurred = pyqtSignal(str)
    
    def __init__(self, report_config: Dict[str, Any]):
        super().__init__()
        self.report_config = report_config
    
    def run(self):
        """执行报告生成"""
        try:
            self.status_updated.emit("正在准备报告模板...")
            self.progress_updated.emit(10)
            self.msleep(500)
            
            self.status_updated.emit("正在收集仿真数据...")
            self.progress_updated.emit(30)
            self.msleep(1000)
            
            self.status_updated.emit("正在生成图表...")
            self.progress_updated.emit(50)
            self.msleep(1000)
            
            self.status_updated.emit("正在编译报告...")
            self.progress_updated.emit(80)
            self.msleep(1000)
            
            self.status_updated.emit("正在保存报告文件...")
            self.progress_updated.emit(95)
            self.msleep(500)
            
            # 模拟生成的报告文件路径
            report_path = f"reports/simulation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            self.progress_updated.emit(100)
            self.status_updated.emit("报告生成完成")
            self.finished.emit(report_path)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class ReportPanel(QWidget):
    """报告生成面板"""
    
    # 信号定义
    report_generated = pyqtSignal(str)  # 报告生成完成信号
    
    def __init__(self):
        super().__init__()
        self.report_templates: List[Dict[str, Any]] = []
        self.current_report_config: Optional[Dict[str, Any]] = None
        self.generation_thread: Optional[ReportGenerationThread] = None
        
        self.init_ui()
        self.load_report_templates()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：报告配置
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧：报告预览
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        
        # 底部：生成控制
        bottom_panel = self.create_bottom_panel()
        layout.addWidget(bottom_panel)
    
    def create_left_panel(self) -> QWidget:
        """创建左侧配置面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 报告基本信息组
        basic_group = QGroupBox("报告基本信息")
        basic_layout = QFormLayout(basic_group)
        
        # 报告标题
        self.title_edit = QLineEdit()
        self.title_edit.setText("激光毁伤仿真分析报告")
        basic_layout.addRow("报告标题:", self.title_edit)
        
        # 项目名称
        self.project_edit = QLineEdit()
        self.project_edit.setText("激光毁伤仿真项目")
        basic_layout.addRow("项目名称:", self.project_edit)
        
        # 作者
        self.author_edit = QLineEdit()
        self.author_edit.setText("仿真工程师")
        basic_layout.addRow("报告作者:", self.author_edit)
        
        # 日期
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        basic_layout.addRow("报告日期:", self.date_edit)
        
        layout.addWidget(basic_group)
        
        # 报告模板组
        template_group = QGroupBox("报告模板")
        template_layout = QVBoxLayout(template_group)
        
        # 模板选择
        template_select_layout = QHBoxLayout()
        template_select_layout.addWidget(QLabel("选择模板:"))
        
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self.on_template_changed)
        template_select_layout.addWidget(self.template_combo)
        
        template_layout.addLayout(template_select_layout)
        
        # 模板描述
        self.template_desc_text = QTextEdit()
        self.template_desc_text.setMaximumHeight(80)
        self.template_desc_text.setReadOnly(True)
        template_layout.addWidget(self.template_desc_text)
        
        layout.addWidget(template_group)
        
        # 报告内容组
        content_group = QGroupBox("报告内容")
        content_layout = QVBoxLayout(content_group)
        
        # 内容选择树
        self.content_tree = QTreeWidget()
        self.content_tree.setHeaderLabel("报告章节")
        self.setup_content_tree()
        content_layout.addWidget(self.content_tree)
        
        layout.addWidget(content_group)
        
        # 输出设置组
        output_group = QGroupBox("输出设置")
        output_layout = QFormLayout(output_group)
        
        # 输出格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF", "HTML", "Word文档"])
        output_layout.addRow("输出格式:", self.format_combo)
        
        # 图片质量
        self.image_quality_combo = QComboBox()
        self.image_quality_combo.addItems(["标准 (150 DPI)", "高质量 (300 DPI)", "超高质量 (600 DPI)"])
        self.image_quality_combo.setCurrentIndex(1)
        output_layout.addRow("图片质量:", self.image_quality_combo)
        
        # 页面设置
        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["A4", "A3", "Letter", "Legal"])
        output_layout.addRow("页面大小:", self.page_size_combo)
        
        # 输出路径
        output_path_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setText("reports/")
        output_path_layout.addWidget(self.output_path_edit)
        
        browse_output_btn = QPushButton("浏览...")
        browse_output_btn.clicked.connect(self.browse_output_path)
        output_path_layout.addWidget(browse_output_btn)
        
        output_layout.addRow("输出路径:", output_path_layout)
        
        layout.addWidget(output_group)
        
        return widget
    
    def create_right_panel(self) -> QWidget:
        """创建右侧预览面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 预览标签页
        preview_tabs = QTabWidget()
        
        # 报告结构预览
        structure_tab = self.create_structure_preview_tab()
        preview_tabs.addTab(structure_tab, "报告结构")
        
        # 内容预览
        content_tab = self.create_content_preview_tab()
        preview_tabs.addTab(content_tab, "内容预览")
        
        # 样式预览
        style_tab = self.create_style_preview_tab()
        preview_tabs.addTab(style_tab, "样式预览")
        
        layout.addWidget(preview_tabs)
        
        return widget
    
    def create_structure_preview_tab(self) -> QWidget:
        """创建报告结构预览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 结构树
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabel("报告结构预览")
        layout.addWidget(self.structure_tree)
        
        return widget
    
    def create_content_preview_tab(self) -> QWidget:
        """创建内容预览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 内容预览文本
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)
        layout.addWidget(self.content_preview)
        
        return widget
    
    def create_style_preview_tab(self) -> QWidget:
        """创建样式预览标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 样式设置
        style_group = QGroupBox("样式设置")
        style_layout = QFormLayout(style_group)
        
        # 字体设置
        self.font_combo = QComboBox()
        self.font_combo.addItems(["宋体", "黑体", "微软雅黑", "Times New Roman", "Arial"])
        self.font_combo.setCurrentText("微软雅黑")
        style_layout.addRow("正文字体:", self.font_combo)
        
        # 字体大小
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        style_layout.addRow("字体大小:", self.font_size_spin)
        
        # 行间距
        self.line_spacing_combo = QComboBox()
        self.line_spacing_combo.addItems(["单倍行距", "1.5倍行距", "双倍行距"])
        self.line_spacing_combo.setCurrentIndex(1)
        style_layout.addRow("行间距:", self.line_spacing_combo)
        
        layout.addWidget(style_group)
        
        # 颜色主题
        theme_group = QGroupBox("颜色主题")
        theme_layout = QVBoxLayout(theme_group)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["默认主题", "蓝色主题", "绿色主题", "橙色主题"])
        theme_layout.addWidget(self.theme_combo)
        
        layout.addWidget(theme_group)
        
        layout.addStretch()
        
        return widget
    
    def create_bottom_panel(self) -> QWidget:
        """创建底部控制面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 进度显示
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("就绪")
        progress_layout.addWidget(self.status_label)
        
        layout.addLayout(progress_layout)
        
        # 控制按钮
        button_layout = QHBoxLayout()
        
        # 预览报告按钮
        preview_btn = QPushButton("预览报告")
        preview_btn.clicked.connect(self.preview_report)
        button_layout.addWidget(preview_btn)
        
        # 保存配置按钮
        save_config_btn = QPushButton("保存配置")
        save_config_btn.clicked.connect(self.save_report_config)
        button_layout.addWidget(save_config_btn)
        
        # 加载配置按钮
        load_config_btn = QPushButton("加载配置")
        load_config_btn.clicked.connect(self.load_report_config)
        button_layout.addWidget(load_config_btn)
        
        button_layout.addStretch()
        
        # 生成报告按钮
        self.generate_btn = QPushButton("生成报告")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(self.generate_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def setup_content_tree(self):
        """设置内容选择树"""
        # 创建根节点
        root_items = [
            ("封面", True),
            ("目录", True),
            ("摘要", True),
            ("1. 项目概述", True),
            ("2. 仿真参数", True),
            ("3. 仿真结果", True),
            ("4. 数据分析", True),
            ("5. 毁伤评估", True),
            ("6. 结论与建议", True),
            ("附录", False)
        ]
        
        for text, checked in root_items:
            item = QTreeWidgetItem(self.content_tree)
            item.setText(0, text)
            item.setCheckState(0, Qt.Checked if checked else Qt.Unchecked)
            
            # 为主要章节添加子项
            if text.startswith(("3.", "4.", "5.")):
                if "仿真结果" in text:
                    sub_items = ["温度场分析", "应力场分析", "位移场分析", "损伤分布"]
                elif "数据分析" in text:
                    sub_items = ["统计分析", "时间历程分析", "参数敏感性分析"]
                elif "毁伤评估" in text:
                    sub_items = ["毁伤程度评估", "毁伤机理分析", "效果对比分析"]
                else:
                    sub_items = []
                
                for sub_text in sub_items:
                    sub_item = QTreeWidgetItem(item)
                    sub_item.setText(0, sub_text)
                    sub_item.setCheckState(0, Qt.Checked)
        
        self.content_tree.expandAll()
    
    def load_report_templates(self):
        """加载报告模板"""
        # 模拟报告模板数据
        self.report_templates = [
            {
                "name": "标准仿真报告",
                "description": "包含完整仿真流程和结果分析的标准报告模板",
                "sections": ["封面", "目录", "摘要", "项目概述", "仿真参数", "仿真结果", "数据分析", "结论"]
            },
            {
                "name": "简化分析报告",
                "description": "重点关注结果分析的简化报告模板",
                "sections": ["封面", "摘要", "仿真结果", "数据分析", "结论"]
            },
            {
                "name": "技术评估报告",
                "description": "专注于技术评估和建议的报告模板",
                "sections": ["封面", "项目概述", "技术分析", "评估结果", "建议措施"]
            }
        ]
        
        # 更新模板下拉框
        self.template_combo.clear()
        for template in self.report_templates:
            self.template_combo.addItem(template["name"])
    
    def on_template_changed(self, template_name: str):
        """模板选择变化事件"""
        for template in self.report_templates:
            if template["name"] == template_name:
                self.template_desc_text.setText(template["description"])
                self.update_structure_preview(template)
                break
    
    def update_structure_preview(self, template: Dict[str, Any]):
        """更新结构预览"""
        self.structure_tree.clear()
        
        for section in template["sections"]:
            item = QTreeWidgetItem(self.structure_tree)
            item.setText(0, section)
        
        self.structure_tree.expandAll()
    
    def browse_output_path(self):
        """浏览输出路径"""
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_path_edit.setText(path)
    
    def preview_report(self):
        """预览报告"""
        # 生成预览内容
        preview_content = self.generate_preview_content()
        self.content_preview.setText(preview_content)
    
    def generate_preview_content(self) -> str:
        """生成预览内容"""
        content = f"""
# {self.title_edit.text()}

**项目名称**: {self.project_edit.text()}
**报告作者**: {self.author_edit.text()}
**报告日期**: {self.date_edit.date().toString('yyyy-MM-dd')}

## 摘要

本报告基于激光毁伤仿真系统生成，详细分析了激光对目标材料的毁伤效果。
仿真采用了先进的有限元方法，考虑了热传导、热应力等多物理场耦合效应。

## 主要结果

- 最高温度: 1200.5 K
- 最大应力: 250.0 MPa  
- 最大位移: 0.15 mm
- 毁伤面积: 25.6 mm²

## 结论

仿真结果表明，在给定的激光参数下，目标材料发生了显著的热损伤...

（这是报告内容的预览，完整报告将包含详细的图表和分析）
        """
        
        return content.strip()
    
    def save_report_config(self):
        """保存报告配置"""
        config = self.get_current_config()
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存报告配置', '', 
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                QMessageBox.information(self, '保存成功', f'配置已保存到: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '保存失败', f'保存配置失败: {str(e)}')
    
    def load_report_config(self):
        """加载报告配置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '加载报告配置', '', 
            'JSON Files (*.json);;All Files (*)'
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.apply_config(config)
                QMessageBox.information(self, '加载成功', f'配置已从文件加载: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '加载失败', f'加载配置失败: {str(e)}')
    
    def get_current_config(self) -> Dict[str, Any]:
        """获取当前配置"""
        return {
            "title": self.title_edit.text(),
            "project": self.project_edit.text(),
            "author": self.author_edit.text(),
            "date": self.date_edit.date().toString('yyyy-MM-dd'),
            "template": self.template_combo.currentText(),
            "format": self.format_combo.currentText(),
            "image_quality": self.image_quality_combo.currentText(),
            "page_size": self.page_size_combo.currentText(),
            "output_path": self.output_path_edit.text(),
            "font": self.font_combo.currentText(),
            "font_size": self.font_size_spin.value(),
            "line_spacing": self.line_spacing_combo.currentText(),
            "theme": self.theme_combo.currentText()
        }
    
    def apply_config(self, config: Dict[str, Any]):
        """应用配置"""
        self.title_edit.setText(config.get("title", ""))
        self.project_edit.setText(config.get("project", ""))
        self.author_edit.setText(config.get("author", ""))
        
        if "date" in config:
            date = QDate.fromString(config["date"], 'yyyy-MM-dd')
            self.date_edit.setDate(date)
        
        self.template_combo.setCurrentText(config.get("template", ""))
        self.format_combo.setCurrentText(config.get("format", "PDF"))
        self.output_path_edit.setText(config.get("output_path", "reports/"))
    
    def generate_report(self):
        """生成报告"""
        # 获取当前配置
        config = self.get_current_config()
        
        # 验证配置
        if not config["title"].strip():
            QMessageBox.warning(self, '配置错误', '请输入报告标题')
            return
        
        if not config["output_path"].strip():
            QMessageBox.warning(self, '配置错误', '请选择输出路径')
            return
        
        # 禁用生成按钮
        self.generate_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 启动生成线程
        self.generation_thread = ReportGenerationThread(config)
        self.generation_thread.progress_updated.connect(self.progress_bar.setValue)
        self.generation_thread.status_updated.connect(self.status_label.setText)
        self.generation_thread.finished.connect(self.on_report_generated)
        self.generation_thread.error_occurred.connect(self.on_generation_error)
        self.generation_thread.start()
    
    def on_report_generated(self, report_path: str):
        """报告生成完成"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("就绪")
        
        QMessageBox.information(
            self, '生成完成', 
            f'报告已生成完成！\n\n文件路径: {report_path}\n\n是否打开报告文件？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        self.report_generated.emit(report_path)
    
    def on_generation_error(self, error_message: str):
        """报告生成错误"""
        self.generate_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("生成失败")
        
        QMessageBox.critical(self, '生成失败', f'报告生成失败:\n{error_message}')
    
    def reset(self):
        """重置面板"""
        self.title_edit.setText("激光毁伤仿真分析报告")
        self.project_edit.setText("激光毁伤仿真项目")
        self.author_edit.setText("仿真工程师")
        self.date_edit.setDate(QDate.currentDate())
        self.template_combo.setCurrentIndex(0)
        self.format_combo.setCurrentIndex(0)
        self.output_path_edit.setText("reports/")
        self.content_preview.clear()
        self.structure_tree.clear()

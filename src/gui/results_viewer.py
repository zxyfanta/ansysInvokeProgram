"""
GUI - 结果查看器

仿真结果显示组件。
"""

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
        QTextEdit, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
        QLabel, QGroupBox, QScrollArea, QSplitter, QHeaderView
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

import json
from typing import Dict, Any

class ResultsViewer(QWidget):
    """结果查看器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5不可用，无法创建结果查看器")
        
        self.simulation_results = None
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # 概览选项卡
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "概览")
        
        # 激光毁伤结果选项卡
        self.laser_damage_tab = self.create_laser_damage_tab()
        self.tab_widget.addTab(self.laser_damage_tab, "激光毁伤")
        
        # 毁伤后效结果选项卡
        self.post_damage_tab = self.create_post_damage_tab()
        self.tab_widget.addTab(self.post_damage_tab, "毁伤后效")
        
        # 数据分析结果选项卡
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "数据分析")
        
        # 原始数据选项卡
        self.raw_data_tab = self.create_raw_data_tab()
        self.tab_widget.addTab(self.raw_data_tab, "原始数据")
    
    def create_overview_tab(self) -> QWidget:
        """创建概览选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 仿真状态组
        status_group = QGroupBox("仿真状态")
        status_layout = QVBoxLayout(status_group)
        
        self.status_label = QLabel("未运行")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7f8c8d;")
        status_layout.addWidget(self.status_label)
        
        layout.addWidget(status_group)
        
        # 关键指标组
        metrics_group = QGroupBox("关键指标")
        metrics_layout = QVBoxLayout(metrics_group)
        
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(2)
        self.metrics_table.setHorizontalHeaderLabels(["指标", "数值"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        metrics_layout.addWidget(self.metrics_table)
        
        layout.addWidget(metrics_group)
        
        # 仿真摘要组
        summary_group = QGroupBox("仿真摘要")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        return widget
    
    def create_laser_damage_tab(self) -> QWidget:
        """创建激光毁伤结果选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 毁伤指标表格
        self.damage_metrics_table = QTableWidget()
        self.damage_metrics_table.setColumnCount(3)
        self.damage_metrics_table.setHorizontalHeaderLabels(["指标", "数值", "单位"])
        self.damage_metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.damage_metrics_table)
        
        # 毁伤详情
        details_group = QGroupBox("毁伤详情")
        details_layout = QVBoxLayout(details_group)
        
        self.damage_details_text = QTextEdit()
        self.damage_details_text.setReadOnly(True)
        details_layout.addWidget(self.damage_details_text)
        
        layout.addWidget(details_group)
        
        return widget
    
    def create_post_damage_tab(self) -> QWidget:
        """创建毁伤后效结果选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 气动力系数表格
        aero_group = QGroupBox("气动力系数")
        aero_layout = QVBoxLayout(aero_group)
        
        self.aero_coeffs_table = QTableWidget()
        self.aero_coeffs_table.setColumnCount(2)
        self.aero_coeffs_table.setHorizontalHeaderLabels(["系数", "数值"])
        self.aero_coeffs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        aero_layout.addWidget(self.aero_coeffs_table)
        
        layout.addWidget(aero_group)
        
        # 飞行性能表格
        performance_group = QGroupBox("飞行性能")
        performance_layout = QVBoxLayout(performance_group)
        
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(3)
        self.performance_table.setHorizontalHeaderLabels(["指标", "数值", "单位"])
        self.performance_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        performance_layout.addWidget(self.performance_table)
        
        layout.addWidget(performance_group)
        
        return widget
    
    def create_analysis_tab(self) -> QWidget:
        """创建数据分析结果选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 分析摘要
        summary_group = QGroupBox("分析摘要")
        summary_layout = QVBoxLayout(summary_group)
        
        self.analysis_summary_text = QTextEdit()
        self.analysis_summary_text.setReadOnly(True)
        summary_layout.addWidget(self.analysis_summary_text)
        
        layout.addWidget(summary_group)
        
        # 关键发现
        findings_group = QGroupBox("关键发现")
        findings_layout = QVBoxLayout(findings_group)
        
        self.findings_table = QTableWidget()
        self.findings_table.setColumnCount(2)
        self.findings_table.setHorizontalHeaderLabels(["类别", "发现"])
        self.findings_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        findings_layout.addWidget(self.findings_table)
        
        layout.addWidget(findings_group)
        
        return widget
    
    def create_raw_data_tab(self) -> QWidget:
        """创建原始数据选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 数据树
        self.data_tree = QTreeWidget()
        self.data_tree.setHeaderLabel("数据结构")
        layout.addWidget(self.data_tree)
        
        return widget
    
    def display_results(self, results: Dict[str, Any]):
        """显示仿真结果"""
        self.simulation_results = results
        
        # 更新概览
        self.update_overview(results)
        
        # 更新激光毁伤结果
        if 'laser_damage_results' in results:
            self.update_laser_damage_results(results['laser_damage_results'])
        
        # 更新毁伤后效结果
        if 'post_damage_results' in results:
            self.update_post_damage_results(results['post_damage_results'])
        
        # 更新数据分析结果
        if 'analysis_results' in results:
            self.update_analysis_results(results['analysis_results'])
        
        # 更新原始数据
        self.update_raw_data(results)
    
    def update_overview(self, results: Dict[str, Any]):
        """更新概览"""
        # 更新状态
        status = results.get('status', '未知')
        if status == 'success':
            self.status_label.setText("仿真完成")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        else:
            self.status_label.setText("仿真失败")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e74c3c;")
        
        # 更新关键指标
        metrics = []
        
        if 'laser_damage_results' in results:
            laser_results = results['laser_damage_results']
            if 'damage_metrics' in laser_results:
                damage_metrics = laser_results['damage_metrics']
                metrics.extend([
                    ("最高温度", f"{damage_metrics.get('max_temperature', 0):.1f} K"),
                    ("最大应力", f"{damage_metrics.get('max_stress', 0):.0f} Pa"),
                    ("毁伤体积", f"{damage_metrics.get('damage_volume', 0):.6f} m³")
                ])
        
        if 'analysis_results' in results:
            analysis_results = results['analysis_results']
            if 'analysis_summary' in analysis_results:
                summary = analysis_results['analysis_summary']
                if 'performance_metrics' in summary:
                    perf_metrics = summary['performance_metrics']
                    metrics.extend([
                        ("毁伤效能", f"{perf_metrics.get('damage_effectiveness', 0):.1f}%"),
                        ("飞行能力保持", f"{perf_metrics.get('flight_capability_retention', 0):.1f}%")
                    ])
        
        self.metrics_table.setRowCount(len(metrics))
        for i, (metric, value) in enumerate(metrics):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric))
            self.metrics_table.setItem(i, 1, QTableWidgetItem(value))
        
        # 更新摘要
        summary_text = "仿真已完成，包含以下分析结果：\n"
        if 'laser_damage_results' in results:
            summary_text += "• 激光毁伤仿真\n"
        if 'post_damage_results' in results:
            summary_text += "• 毁伤后效分析\n"
        if 'analysis_results' in results:
            summary_text += "• 数据分析与报告生成\n"
        
        self.summary_text.setText(summary_text)
    
    def update_laser_damage_results(self, laser_results: Dict[str, Any]):
        """更新激光毁伤结果"""
        if 'damage_metrics' in laser_results:
            metrics = laser_results['damage_metrics']
            
            metric_data = [
                ("最高温度", f"{metrics.get('max_temperature', 0):.1f}", "K"),
                ("最大应力", f"{metrics.get('max_stress', 0):.0f}", "Pa"),
                ("毁伤体积", f"{metrics.get('damage_volume', 0):.6f}", "m³"),
                ("毁伤深度", f"{metrics.get('damage_depth', 0):.3f}", "m"),
                ("计算时间", f"{metrics.get('computation_time', 0):.1f}", "s")
            ]
            
            self.damage_metrics_table.setRowCount(len(metric_data))
            for i, (metric, value, unit) in enumerate(metric_data):
                self.damage_metrics_table.setItem(i, 0, QTableWidgetItem(metric))
                self.damage_metrics_table.setItem(i, 1, QTableWidgetItem(value))
                self.damage_metrics_table.setItem(i, 2, QTableWidgetItem(unit))
        
        # 更新详情
        details_text = json.dumps(laser_results, indent=2, ensure_ascii=False, default=str)
        self.damage_details_text.setText(details_text)
    
    def update_post_damage_results(self, post_results: Dict[str, Any]):
        """更新毁伤后效结果"""
        # 更新气动力系数
        if 'aerodynamic_coefficients' in post_results:
            aero_coeffs = post_results['aerodynamic_coefficients']
            
            self.aero_coeffs_table.setRowCount(len(aero_coeffs))
            for i, (coeff, value) in enumerate(aero_coeffs.items()):
                self.aero_coeffs_table.setItem(i, 0, QTableWidgetItem(coeff))
                self.aero_coeffs_table.setItem(i, 1, QTableWidgetItem(f"{value:.4f}"))
        
        # 更新飞行性能
        if 'flight_performance' in post_results:
            performance = post_results['flight_performance']
            
            perf_data = [
                ("平均速度", f"{performance.get('average_speed', 0):.1f}", "m/s"),
                ("最大速度", f"{performance.get('max_speed', 0):.1f}", "m/s"),
                ("爬升率", f"{performance.get('climb_rate', 0):.1f}", "m/s"),
                ("转弯率", f"{performance.get('turn_rate', 0):.1f}", "°/s"),
                ("载荷因子", f"{performance.get('load_factor', 0):.2f}", "-")
            ]
            
            self.performance_table.setRowCount(len(perf_data))
            for i, (metric, value, unit) in enumerate(perf_data):
                self.performance_table.setItem(i, 0, QTableWidgetItem(metric))
                self.performance_table.setItem(i, 1, QTableWidgetItem(value))
                self.performance_table.setItem(i, 2, QTableWidgetItem(unit))
    
    def update_analysis_results(self, analysis_results: Dict[str, Any]):
        """更新数据分析结果"""
        # 更新分析摘要
        if 'analysis_summary' in analysis_results:
            summary = analysis_results['analysis_summary']
            summary_text = json.dumps(summary, indent=2, ensure_ascii=False, default=str)
            self.analysis_summary_text.setText(summary_text)
        
        # 更新关键发现
        if 'extracted_data' in analysis_results:
            extracted_data = analysis_results['extracted_data']
            findings = []
            
            if 'laser_damage' in extracted_data:
                findings.append(("激光毁伤", "毁伤分析完成"))
            if 'post_damage' in extracted_data:
                findings.append(("毁伤后效", "后效分析完成"))
            if 'comparison' in extracted_data:
                findings.append(("对比分析", "对比分析完成"))
            
            self.findings_table.setRowCount(len(findings))
            for i, (category, finding) in enumerate(findings):
                self.findings_table.setItem(i, 0, QTableWidgetItem(category))
                self.findings_table.setItem(i, 1, QTableWidgetItem(finding))
    
    def update_raw_data(self, results: Dict[str, Any]):
        """更新原始数据"""
        self.data_tree.clear()
        self.populate_tree_item(self.data_tree.invisibleRootItem(), results)
        self.data_tree.expandAll()
    
    def populate_tree_item(self, parent_item, data):
        """填充树形项目"""
        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem(parent_item)
                item.setText(0, str(key))
                self.populate_tree_item(item, value)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = QTreeWidgetItem(parent_item)
                item.setText(0, f"[{i}]")
                self.populate_tree_item(item, value)
        else:
            parent_item.setText(1, str(data))
    
    def clear_results(self):
        """清空结果"""
        self.simulation_results = None
        
        # 清空所有表格和文本
        self.metrics_table.setRowCount(0)
        self.damage_metrics_table.setRowCount(0)
        self.aero_coeffs_table.setRowCount(0)
        self.performance_table.setRowCount(0)
        self.findings_table.setRowCount(0)
        
        self.summary_text.clear()
        self.damage_details_text.clear()
        self.analysis_summary_text.clear()
        self.data_tree.clear()
        
        self.status_label.setText("未运行")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #7f8c8d;")

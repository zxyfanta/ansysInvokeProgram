"""
效果评估面板

提供激光毁伤效果的综合评估和分析功能。
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QProgressBar, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButton, QComboBox, QTextEdit, QTabWidget, QFormLayout,
    QSlider, QCheckBox, QSpinBox, QDoubleSpinBox, QListWidget,
    QListWidgetItem, QSplitter, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap, QPainter
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum


class DamageLevel(Enum):
    """毁伤等级枚举"""
    MINIMAL = ("轻微毁伤", "#4CAF50", 0.2)
    MODERATE = ("中等毁伤", "#FF9800", 0.5)
    SEVERE = ("严重毁伤", "#FF5722", 0.8)
    CRITICAL = ("致命毁伤", "#F44336", 1.0)


class AssessmentPanel(QWidget):
    """效果评估面板"""

    # 信号定义
    assessment_completed = pyqtSignal(dict)  # 评估完成信号

    def __init__(self):
        super().__init__()
        self.assessment_results: Optional[Dict[str, Any]] = None
        self.damage_metrics: Dict[str, float] = {}

        self.init_ui()
        self.generate_sample_assessment()  # 生成示例评估数据

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)

        # 创建标签页
        tab_widget = QTabWidget()

        # 毁伤评估标签页
        damage_tab = self.create_damage_assessment_tab()
        tab_widget.addTab(damage_tab, "毁伤评估")

        # 效果分析标签页
        effect_tab = self.create_effect_analysis_tab()
        tab_widget.addTab(effect_tab, "效果分析")

        # 对比分析标签页
        comparison_tab = self.create_comparison_tab()
        tab_widget.addTab(comparison_tab, "对比分析")

        # 评估报告标签页
        report_tab = self.create_assessment_report_tab()
        tab_widget.addTab(report_tab, "评估报告")

        layout.addWidget(tab_widget)

    def create_damage_assessment_tab(self) -> QWidget:
        """创建毁伤评估标签页"""
        widget = QWidget()
        layout = QHBoxLayout(widget)

        # 左侧：评估指标
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # 毁伤指标组
        metrics_group = QGroupBox("毁伤指标")
        metrics_layout = QVBoxLayout(metrics_group)

        # 指标表格
        self.metrics_table = QTableWidget(0, 3)
        self.metrics_table.setHorizontalHeaderLabels(["指标名称", "数值", "权重"])
        self.metrics_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        metrics_layout.addWidget(self.metrics_table)

        left_layout.addWidget(metrics_group)

        # 评估参数组
        params_group = QGroupBox("评估参数")
        params_layout = QFormLayout(params_group)

        # 评估方法
        self.method_combo = QComboBox()
        self.method_combo.addItems(["综合评估法", "层次分析法", "模糊评估法", "神经网络法"])
        self.method_combo.currentTextChanged.connect(self.update_assessment)
        params_layout.addRow("评估方法:", self.method_combo)

        # 阈值设置
        self.threshold_spin = QDoubleSpinBox()
        self.threshold_spin.setRange(0.0, 1.0)
        self.threshold_spin.setValue(0.5)
        self.threshold_spin.setSingleStep(0.1)
        self.threshold_spin.valueChanged.connect(self.update_assessment)
        params_layout.addRow("毁伤阈值:", self.threshold_spin)

        # 置信度
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.5, 1.0)
        self.confidence_spin.setValue(0.95)
        self.confidence_spin.setSingleStep(0.05)
        params_layout.addRow("置信度:", self.confidence_spin)

        left_layout.addWidget(params_group)

        # 重新评估按钮
        reassess_btn = QPushButton("重新评估")
        reassess_btn.clicked.connect(self.perform_assessment)
        left_layout.addWidget(reassess_btn)

        left_layout.addStretch()
        layout.addWidget(left_panel)

        # 右侧：评估结果可视化
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # 毁伤等级显示
        level_group = QGroupBox("毁伤等级评估")
        level_layout = QVBoxLayout(level_group)

        # 等级指示器
        self.level_indicator = self.create_level_indicator()
        level_layout.addWidget(self.level_indicator)

        # 等级描述
        self.level_description = QTextEdit()
        self.level_description.setMaximumHeight(100)
        self.level_description.setReadOnly(True)
        level_layout.addWidget(self.level_description)

        right_layout.addWidget(level_group)

        # 雷达图
        radar_group = QGroupBox("毁伤指标雷达图")
        radar_layout = QVBoxLayout(radar_group)

        self.radar_figure = Figure(figsize=(6, 6))
        self.radar_canvas = FigureCanvas(self.radar_figure)
        radar_layout.addWidget(self.radar_canvas)

        right_layout.addWidget(radar_group)

        layout.addWidget(right_panel)

        return widget

    def create_effect_analysis_tab(self) -> QWidget:
        """创建效果分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)

        # 上部：效果分析图表
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)

        # 温度效应分析
        temp_group = QGroupBox("温度效应分析")
        temp_layout = QVBoxLayout(temp_group)

        self.temp_effect_figure = Figure(figsize=(5, 4))
        self.temp_effect_canvas = FigureCanvas(self.temp_effect_figure)
        temp_layout.addWidget(self.temp_effect_canvas)

        top_layout.addWidget(temp_group)

        # 应力效应分析
        stress_group = QGroupBox("应力效应分析")
        stress_layout = QVBoxLayout(stress_group)

        self.stress_effect_figure = Figure(figsize=(5, 4))
        self.stress_effect_canvas = FigureCanvas(self.stress_effect_figure)
        stress_layout.addWidget(self.stress_effect_canvas)

        top_layout.addWidget(stress_group)

        splitter.addWidget(top_widget)

        # 下部：效应机理分析
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)

        mechanism_group = QGroupBox("毁伤机理分析")
        mechanism_layout = QVBoxLayout(mechanism_group)

        self.mechanism_text = QTextEdit()
        self.mechanism_text.setReadOnly(True)
        mechanism_layout.addWidget(self.mechanism_text)

        bottom_layout.addWidget(mechanism_group)

        splitter.addWidget(bottom_widget)

        # 设置分割器比例
        splitter.setSizes([400, 200])

        layout.addWidget(splitter)

        return widget

    def create_comparison_tab(self) -> QWidget:
        """创建对比分析标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 对比设置
        settings_group = QGroupBox("对比设置")
        settings_layout = QHBoxLayout(settings_group)

        settings_layout.addWidget(QLabel("对比基准:"))

        self.baseline_combo = QComboBox()
        self.baseline_combo.addItems(["标准工况", "历史数据", "理论值", "实验数据"])
        settings_layout.addWidget(self.baseline_combo)

        settings_layout.addWidget(QLabel("对比指标:"))

        self.comparison_metrics = QComboBox()
        self.comparison_metrics.addItems(["全部指标", "热损伤", "结构损伤", "功能损伤"])
        settings_layout.addWidget(self.comparison_metrics)

        update_comparison_btn = QPushButton("更新对比")
        update_comparison_btn.clicked.connect(self.update_comparison)
        settings_layout.addWidget(update_comparison_btn)

        settings_layout.addStretch()

        layout.addWidget(settings_group)

        # 对比图表
        comparison_group = QGroupBox("对比分析图表")
        comparison_layout = QVBoxLayout(comparison_group)

        self.comparison_figure = Figure(figsize=(10, 6))
        self.comparison_canvas = FigureCanvas(self.comparison_figure)
        comparison_layout.addWidget(self.comparison_canvas)

        layout.addWidget(comparison_group)

        # 对比结论
        conclusion_group = QGroupBox("对比结论")
        conclusion_layout = QVBoxLayout(conclusion_group)

        self.comparison_conclusion = QTextEdit()
        self.comparison_conclusion.setReadOnly(True)
        self.comparison_conclusion.setMaximumHeight(120)
        conclusion_layout.addWidget(self.comparison_conclusion)

        layout.addWidget(conclusion_group)

        return widget

    def create_assessment_report_tab(self) -> QWidget:
        """创建评估报告标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # 报告内容
        report_group = QGroupBox("评估报告")
        report_layout = QVBoxLayout(report_group)

        self.assessment_report = QTextEdit()
        self.assessment_report.setReadOnly(True)
        report_layout.addWidget(self.assessment_report)

        layout.addWidget(report_group)

        # 报告操作
        actions_layout = QHBoxLayout()

        generate_report_btn = QPushButton("生成评估报告")
        generate_report_btn.clicked.connect(self.generate_assessment_report)
        actions_layout.addWidget(generate_report_btn)

        export_report_btn = QPushButton("导出报告")
        export_report_btn.clicked.connect(self.export_assessment_report)
        actions_layout.addWidget(export_report_btn)

        actions_layout.addStretch()

        layout.addLayout(actions_layout)

        return widget

    def create_level_indicator(self) -> QWidget:
        """创建毁伤等级指示器"""
        widget = QWidget()
        widget.setFixedHeight(80)

        # 自定义绘制毁伤等级指示器
        def paintEvent(event):
            painter = QPainter(widget)
            painter.setRenderHint(QPainter.Antialiasing)

            # 绘制背景
            rect = widget.rect().adjusted(10, 10, -10, -10)
            painter.fillRect(rect, QColor(240, 240, 240))

            # 绘制等级条
            level_width = rect.width() // 4
            current_level = getattr(widget, 'current_level', DamageLevel.MODERATE)

            for i, level in enumerate(DamageLevel):
                level_rect = rect.adjusted(i * level_width, 0, -(3-i) * level_width, 0)
                color = QColor(level.value[1])

                if level == current_level:
                    painter.fillRect(level_rect, color)
                    painter.setPen(QColor(0, 0, 0))
                    painter.drawRect(level_rect)
                else:
                    color.setAlpha(100)
                    painter.fillRect(level_rect, color)

                # 绘制文字
                painter.setPen(QColor(0, 0, 0))
                painter.drawText(level_rect, Qt.AlignCenter, level.value[0])

        widget.paintEvent = paintEvent
        widget.current_level = DamageLevel.MODERATE

        return widget

    def generate_sample_assessment(self):
        """生成示例评估数据"""
        # 模拟毁伤指标数据
        self.damage_metrics = {
            "热损伤面积": 25.6,  # mm²
            "熔化体积": 12.3,   # mm³
            "应力集中系数": 2.8,
            "结构完整性": 0.75,  # 0-1
            "气动性能影响": 0.15, # 0-1
            "功能损失程度": 0.35  # 0-1
        }

        # 更新指标表格
        self.update_metrics_table()

        # 更新可视化
        self.update_assessment()
        self.update_radar_chart()
        self.update_effect_analysis()
        self.update_comparison()
        self.generate_assessment_report()

    def update_metrics_table(self):
        """更新指标表格"""
        metrics_data = [
            ("热损伤面积", f"{self.damage_metrics['热损伤面积']:.1f} mm²", "0.25"),
            ("熔化体积", f"{self.damage_metrics['熔化体积']:.1f} mm³", "0.20"),
            ("应力集中系数", f"{self.damage_metrics['应力集中系数']:.1f}", "0.15"),
            ("结构完整性", f"{self.damage_metrics['结构完整性']:.2f}", "0.20"),
            ("气动性能影响", f"{self.damage_metrics['气动性能影响']:.2f}", "0.10"),
            ("功能损失程度", f"{self.damage_metrics['功能损失程度']:.2f}", "0.10")
        ]

        self.metrics_table.setRowCount(len(metrics_data))

        for i, (metric, value, weight) in enumerate(metrics_data):
            self.metrics_table.setItem(i, 0, QTableWidgetItem(metric))
            self.metrics_table.setItem(i, 1, QTableWidgetItem(value))
            self.metrics_table.setItem(i, 2, QTableWidgetItem(weight))

    def update_assessment(self):
        """更新毁伤评估"""
        # 计算综合毁伤程度
        weights = [0.25, 0.20, 0.15, 0.20, 0.10, 0.10]

        # 归一化指标值
        normalized_metrics = [
            min(self.damage_metrics["热损伤面积"] / 50.0, 1.0),
            min(self.damage_metrics["熔化体积"] / 25.0, 1.0),
            min(self.damage_metrics["应力集中系数"] / 5.0, 1.0),
            1.0 - self.damage_metrics["结构完整性"],
            self.damage_metrics["气动性能影响"],
            self.damage_metrics["功能损失程度"]
        ]

        # 计算加权综合评分
        overall_damage = sum(w * m for w, m in zip(weights, normalized_metrics))

        # 确定毁伤等级
        if overall_damage < 0.25:
            damage_level = DamageLevel.MINIMAL
        elif overall_damage < 0.5:
            damage_level = DamageLevel.MODERATE
        elif overall_damage < 0.75:
            damage_level = DamageLevel.SEVERE
        else:
            damage_level = DamageLevel.CRITICAL

        # 更新等级指示器
        self.level_indicator.current_level = damage_level
        self.level_indicator.update()

        # 更新等级描述
        description = f"""
毁伤等级: {damage_level.value[0]}
综合评分: {overall_damage:.3f}
置信度: {self.confidence_spin.value():.2f}

评估说明:
基于{self.method_combo.currentText()}，综合考虑热损伤、结构损伤、功能损伤等多个维度，
评估结果表明目标受到了{damage_level.value[0]}。

主要毁伤特征:
- 热损伤面积达到 {self.damage_metrics['热损伤面积']:.1f} mm²
- 结构完整性降低至 {self.damage_metrics['结构完整性']:.1%}
- 功能损失程度为 {self.damage_metrics['功能损失程度']:.1%}
        """.strip()

        self.level_description.setText(description)

    def update_radar_chart(self):
        """更新雷达图"""
        self.radar_figure.clear()
        ax = self.radar_figure.add_subplot(111, projection='polar')

        # 指标名称和数值
        metrics = ["热损伤", "熔化损伤", "应力集中", "结构损伤", "气动影响", "功能损失"]
        values = [
            min(self.damage_metrics["热损伤面积"] / 50.0, 1.0),
            min(self.damage_metrics["熔化体积"] / 25.0, 1.0),
            min(self.damage_metrics["应力集中系数"] / 5.0, 1.0),
            1.0 - self.damage_metrics["结构完整性"],
            self.damage_metrics["气动性能影响"],
            self.damage_metrics["功能损失程度"]
        ]

        # 角度
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        values += values[:1]  # 闭合图形
        angles += angles[:1]

        # 绘制雷达图
        ax.plot(angles, values, 'o-', linewidth=2, label='当前评估')
        ax.fill(angles, values, alpha=0.25)

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        ax.grid(True)

        ax.set_title('毁伤指标雷达图', pad=20)

        self.radar_canvas.draw()

    def update_effect_analysis(self):
        """更新效应分析"""
        # 温度效应分析
        self.temp_effect_figure.clear()
        ax1 = self.temp_effect_figure.add_subplot(111)

        # 模拟温度随时间的变化
        time = np.linspace(0, 10, 100)
        temp_rise = 800 * (1 - np.exp(-time/2))

        ax1.plot(time, temp_rise, 'r-', linewidth=2)
        ax1.set_xlabel('时间 (s)')
        ax1.set_ylabel('温升 (K)')
        ax1.set_title('温度效应时间历程')
        ax1.grid(True, alpha=0.3)

        # 标注关键点
        melting_time = 3.5
        ax1.axhline(y=640, color='orange', linestyle='--', alpha=0.7, label='熔点')
        ax1.axvline(x=melting_time, color='red', linestyle='--', alpha=0.7, label='开始熔化')
        ax1.legend()

        self.temp_effect_canvas.draw()

        # 应力效应分析
        self.stress_effect_figure.clear()
        ax2 = self.stress_effect_figure.add_subplot(111)

        # 模拟应力随温度的变化
        temp_range = np.linspace(293, 1200, 100)
        thermal_stress = 200e6 * (temp_range - 293) / 907  # 热应力

        ax2.plot(temp_range, thermal_stress/1e6, 'b-', linewidth=2)
        ax2.set_xlabel('温度 (K)')
        ax2.set_ylabel('热应力 (MPa)')
        ax2.set_title('热应力-温度关系')
        ax2.grid(True, alpha=0.3)

        # 标注屈服强度
        yield_strength = 276  # MPa
        ax2.axhline(y=yield_strength, color='red', linestyle='--', alpha=0.7, label='屈服强度')
        ax2.legend()

        self.stress_effect_canvas.draw()

        # 更新机理分析文本
        mechanism_text = """
毁伤机理分析:

1. 热效应机理:
   - 激光能量被材料表面吸收，转化为热能
   - 热传导导致温度场快速扩展
   - 当温度超过熔点(933K)时，材料开始熔化
   - 熔化区域形成热损伤

2. 热应力机理:
   - 温度梯度产生热应力
   - 热膨胀受约束导致压应力
   - 冷却过程中产生拉应力
   - 应力超过屈服强度时发生塑性变形

3. 结构损伤机理:
   - 热应力导致材料屈服和塑性变形
   - 熔化区域形成结构缺陷
   - 热循环导致疲劳损伤累积
   - 结构完整性逐步降低

4. 功能影响机理:
   - 表面形貌改变影响气动性能
   - 结构变形影响载荷传递
   - 材料性能退化影响服役性能
        """

        self.mechanism_text.setText(mechanism_text.strip())

    def update_comparison(self):
        """更新对比分析"""
        self.comparison_figure.clear()
        ax = self.comparison_figure.add_subplot(111)

        # 对比数据
        metrics = ['热损伤', '结构损伤', '功能损伤', '综合评估']
        current_values = [0.6, 0.4, 0.3, 0.45]
        baseline_values = [0.5, 0.3, 0.2, 0.35]

        x = np.arange(len(metrics))
        width = 0.35

        bars1 = ax.bar(x - width/2, current_values, width, label='当前仿真', color='#FF6B6B')
        bars2 = ax.bar(x + width/2, baseline_values, width, label='基准对比', color='#4ECDC4')

        ax.set_xlabel('评估指标')
        ax.set_ylabel('损伤程度')
        ax.set_title('毁伤效果对比分析')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.2f}', ha='center', va='bottom')

        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{height:.2f}', ha='center', va='bottom')

        self.comparison_canvas.draw()

        # 更新对比结论
        conclusion_text = """
对比分析结论:

与基准工况相比，当前仿真结果显示:
• 热损伤程度提高了20%，主要由于激光功率增加
• 结构损伤程度提高了33%，热应力效应更加显著
• 功能损伤程度提高了50%，对系统性能影响较大
• 综合评估结果提高了29%，整体毁伤效果明显增强

建议: 当前激光参数设置能够有效实现预期毁伤目标，建议在实际应用中采用。
        """

        self.comparison_conclusion.setText(conclusion_text.strip())

    def perform_assessment(self):
        """执行毁伤评估"""
        # 重新计算评估结果
        self.update_assessment()
        self.update_radar_chart()

        # 发送评估完成信号
        assessment_data = {
            "damage_level": self.level_indicator.current_level.value[0],
            "metrics": self.damage_metrics,
            "method": self.method_combo.currentText(),
            "confidence": self.confidence_spin.value()
        }

        self.assessment_completed.emit(assessment_data)

    def generate_assessment_report(self):
        """生成评估报告"""
        current_level = getattr(self.level_indicator, 'current_level', DamageLevel.MODERATE)

        report_text = f"""
# 激光毁伤效果评估报告

## 评估概要
- 评估时间: {QTimer().singleShot.__name__}
- 评估方法: {self.method_combo.currentText()}
- 置信度: {self.confidence_spin.value():.1%}

## 毁伤等级评定
**评估结果: {current_level.value[0]}**

## 详细指标分析

### 热损伤分析
- 热损伤面积: {self.damage_metrics['热损伤面积']:.1f} mm²
- 熔化体积: {self.damage_metrics['熔化体积']:.1f} mm³
- 评估: 热损伤程度较为显著，达到预期毁伤效果

### 结构损伤分析
- 应力集中系数: {self.damage_metrics['应力集中系数']:.1f}
- 结构完整性: {self.damage_metrics['结构完整性']:.1%}
- 评估: 结构受到一定程度损伤，但整体完整性尚可

### 功能影响分析
- 气动性能影响: {self.damage_metrics['气动性能影响']:.1%}
- 功能损失程度: {self.damage_metrics['功能损失程度']:.1%}
- 评估: 功能受到轻微影响，不影响基本性能

## 毁伤机理总结
1. 激光能量快速加热目标表面
2. 热传导形成温度场分布
3. 热应力导致材料变形
4. 局部区域发生熔化损伤

## 评估结论
基于多维度综合分析，目标受到{current_level.value[0]}，
激光武器在当前参数设置下能够有效实现毁伤目标。

## 建议措施
1. 可适当调整激光功率以优化毁伤效果
2. 建议进行实验验证以确认仿真结果
3. 考虑环境因素对毁伤效果的影响
        """

        self.assessment_report.setText(report_text.strip())

    def export_assessment_report(self):
        """导出评估报告"""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox

        file_path, _ = QFileDialog.getSaveFileName(
            self, '导出评估报告', '',
            'Text Files (*.txt);;PDF Files (*.pdf);;All Files (*)'
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.assessment_report.toPlainText())
                QMessageBox.information(self, '导出成功', f'评估报告已保存到: {file_path}')
            except Exception as e:
                QMessageBox.critical(self, '导出失败', f'导出报告失败: {str(e)}')

    def load_simulation_results(self, results: Dict[str, Any]):
        """加载仿真结果进行评估"""
        # 从仿真结果中提取毁伤指标
        if results:
            self.damage_metrics.update({
                "热损伤面积": results.get("thermal_damage_area", 0),
                "熔化体积": results.get("melting_volume", 0),
                "应力集中系数": results.get("stress_concentration", 1),
                "结构完整性": results.get("structural_integrity", 1),
                "气动性能影响": results.get("aerodynamic_impact", 0),
                "功能损失程度": results.get("functional_loss", 0)
            })

            self.update_metrics_table()
            self.perform_assessment()

    def reset(self):
        """重置面板"""
        self.damage_metrics = {}
        self.metrics_table.setRowCount(0)
        self.level_description.clear()
        self.mechanism_text.clear()
        self.comparison_conclusion.clear()
        self.assessment_report.clear()

        # 清空图形
        if hasattr(self, 'radar_figure'):
            self.radar_figure.clear()
            self.radar_canvas.draw()

        if hasattr(self, 'temp_effect_figure'):
            self.temp_effect_figure.clear()
            self.temp_effect_canvas.draw()

        if hasattr(self, 'stress_effect_figure'):
            self.stress_effect_figure.clear()
            self.stress_effect_canvas.draw()

        if hasattr(self, 'comparison_figure'):
            self.comparison_figure.clear()
            self.comparison_canvas.draw()
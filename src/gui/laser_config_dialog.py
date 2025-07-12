"""
GUI - 激光配置对话框

激光参数配置界面。
"""

import sys
from pathlib import Path
from typing import Optional

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
        QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox,
        QGroupBox, QDialogButtonBox, QTabWidget, QWidget,
        QSlider, QCheckBox, QPushButton, QTextEdit
    )
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont, QDoubleValidator
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from core.data_models import LaserParameters, LaserType

class LaserConfigDialog(QDialog):
    """激光配置对话框"""
    
    def __init__(self, laser_params: Optional[LaserParameters] = None, parent=None):
        super().__init__(parent)
        
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5不可用，无法创建对话框")
        
        self.laser_params = laser_params
        self.init_ui()
        self.load_parameters()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("激光参数配置")
        self.setModal(True)
        self.resize(500, 600)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 基本参数选项卡
        basic_tab = self.create_basic_parameters_tab()
        tab_widget.addTab(basic_tab, "基本参数")
        
        # 高级参数选项卡
        advanced_tab = self.create_advanced_parameters_tab()
        tab_widget.addTab(advanced_tab, "高级参数")
        
        # 预设选项卡
        presets_tab = self.create_presets_tab()
        tab_widget.addTab(presets_tab, "预设配置")
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_parameters)
        main_layout.addWidget(buttons)
        
        # 设置样式
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QDoubleSpinBox, QSpinBox, QComboBox, QLineEdit {
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            
            QDoubleSpinBox:focus, QSpinBox:focus, QComboBox:focus, QLineEdit:focus {
                border: 2px solid #3498db;
            }
        """)
    
    def create_basic_parameters_tab(self) -> QWidget:
        """创建基本参数选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 激光器类型组
        laser_type_group = QGroupBox("激光器类型")
        laser_type_layout = QFormLayout(laser_type_group)
        
        self.laser_type_combo = QComboBox()
        self.laser_type_combo.addItems(["连续激光", "脉冲激光", "准连续激光"])
        laser_type_layout.addRow("激光类型:", self.laser_type_combo)
        
        layout.addWidget(laser_type_group)
        
        # 功率参数组
        power_group = QGroupBox("功率参数")
        power_layout = QFormLayout(power_group)
        
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(1.0, 100000.0)
        self.power_spin.setValue(1000.0)
        self.power_spin.setSuffix(" W")
        self.power_spin.setDecimals(1)
        power_layout.addRow("激光功率:", self.power_spin)
        
        # 功率滑块
        self.power_slider = QSlider(Qt.Horizontal)
        self.power_slider.setRange(1, 10000)
        self.power_slider.setValue(1000)
        self.power_slider.valueChanged.connect(lambda v: self.power_spin.setValue(v))
        self.power_spin.valueChanged.connect(lambda v: self.power_slider.setValue(int(v)))
        power_layout.addRow("功率调节:", self.power_slider)
        
        layout.addWidget(power_group)
        
        # 光束参数组
        beam_group = QGroupBox("光束参数")
        beam_layout = QFormLayout(beam_group)
        
        self.wavelength_spin = QDoubleSpinBox()
        self.wavelength_spin.setRange(200.0, 20000.0)
        self.wavelength_spin.setValue(1064.0)
        self.wavelength_spin.setSuffix(" nm")
        self.wavelength_spin.setDecimals(1)
        beam_layout.addRow("波长:", self.wavelength_spin)
        
        self.beam_diameter_spin = QDoubleSpinBox()
        self.beam_diameter_spin.setRange(0.001, 1.0)
        self.beam_diameter_spin.setValue(0.01)
        self.beam_diameter_spin.setSuffix(" m")
        self.beam_diameter_spin.setDecimals(4)
        beam_layout.addRow("光束直径:", self.beam_diameter_spin)
        
        self.beam_quality_spin = QDoubleSpinBox()
        self.beam_quality_spin.setRange(1.0, 10.0)
        self.beam_quality_spin.setValue(1.2)
        self.beam_quality_spin.setDecimals(2)
        beam_layout.addRow("光束质量因子:", self.beam_quality_spin)
        
        self.divergence_spin = QDoubleSpinBox()
        self.divergence_spin.setRange(0.1, 100.0)
        self.divergence_spin.setValue(1.0)
        self.divergence_spin.setSuffix(" mrad")
        self.divergence_spin.setDecimals(2)
        beam_layout.addRow("发散角:", self.divergence_spin)
        
        layout.addWidget(beam_group)
        
        # 脉冲参数组（仅脉冲激光）
        self.pulse_group = QGroupBox("脉冲参数")
        pulse_layout = QFormLayout(self.pulse_group)
        
        self.pulse_duration_spin = QDoubleSpinBox()
        self.pulse_duration_spin.setRange(1e-12, 1.0)
        self.pulse_duration_spin.setValue(1e-6)
        self.pulse_duration_spin.setSuffix(" s")
        self.pulse_duration_spin.setDecimals(9)
        self.pulse_duration_spin.setEnabled(False)
        pulse_layout.addRow("脉冲宽度:", self.pulse_duration_spin)
        
        self.pulse_frequency_spin = QDoubleSpinBox()
        self.pulse_frequency_spin.setRange(1.0, 1000000.0)
        self.pulse_frequency_spin.setValue(1000.0)
        self.pulse_frequency_spin.setSuffix(" Hz")
        self.pulse_frequency_spin.setDecimals(1)
        self.pulse_frequency_spin.setEnabled(False)
        pulse_layout.addRow("脉冲频率:", self.pulse_frequency_spin)
        
        layout.addWidget(self.pulse_group)
        
        # 连接信号
        self.laser_type_combo.currentTextChanged.connect(self.on_laser_type_changed)
        
        return widget
    
    def create_advanced_parameters_tab(self) -> QWidget:
        """创建高级参数选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 光束轮廓组
        profile_group = QGroupBox("光束轮廓")
        profile_layout = QFormLayout(profile_group)
        
        self.beam_profile_combo = QComboBox()
        self.beam_profile_combo.addItems(["高斯光束", "均匀光束", "超高斯光束", "环形光束"])
        profile_layout.addRow("光束轮廓:", self.beam_profile_combo)
        
        self.super_gaussian_order_spin = QSpinBox()
        self.super_gaussian_order_spin.setRange(1, 10)
        self.super_gaussian_order_spin.setValue(2)
        self.super_gaussian_order_spin.setEnabled(False)
        profile_layout.addRow("超高斯阶数:", self.super_gaussian_order_spin)
        
        layout.addWidget(profile_group)
        
        # 偏振参数组
        polarization_group = QGroupBox("偏振参数")
        polarization_layout = QFormLayout(polarization_group)
        
        self.polarization_combo = QComboBox()
        self.polarization_combo.addItems(["线偏振", "圆偏振", "椭圆偏振", "随机偏振"])
        polarization_layout.addRow("偏振类型:", self.polarization_combo)
        
        self.polarization_angle_spin = QDoubleSpinBox()
        self.polarization_angle_spin.setRange(0.0, 180.0)
        self.polarization_angle_spin.setValue(0.0)
        self.polarization_angle_spin.setSuffix(" °")
        self.polarization_angle_spin.setDecimals(1)
        polarization_layout.addRow("偏振角:", self.polarization_angle_spin)
        
        layout.addWidget(polarization_group)
        
        # 稳定性参数组
        stability_group = QGroupBox("稳定性参数")
        stability_layout = QFormLayout(stability_group)
        
        self.power_stability_spin = QDoubleSpinBox()
        self.power_stability_spin.setRange(0.1, 10.0)
        self.power_stability_spin.setValue(1.0)
        self.power_stability_spin.setSuffix(" %")
        self.power_stability_spin.setDecimals(2)
        stability_layout.addRow("功率稳定性:", self.power_stability_spin)
        
        self.pointing_stability_spin = QDoubleSpinBox()
        self.pointing_stability_spin.setRange(0.1, 100.0)
        self.pointing_stability_spin.setValue(10.0)
        self.pointing_stability_spin.setSuffix(" μrad")
        self.pointing_stability_spin.setDecimals(1)
        stability_layout.addRow("指向稳定性:", self.pointing_stability_spin)
        
        layout.addWidget(stability_group)
        
        # 连接信号
        self.beam_profile_combo.currentTextChanged.connect(self.on_beam_profile_changed)
        
        return widget
    
    def create_presets_tab(self) -> QWidget:
        """创建预设配置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 预设选择组
        presets_group = QGroupBox("预设配置")
        presets_layout = QVBoxLayout(presets_group)
        
        # 预设列表
        self.presets_combo = QComboBox()
        self.presets_combo.addItems([
            "1kW连续激光器",
            "10kW连续激光器", 
            "高功率脉冲激光器",
            "精密加工激光器",
            "自定义配置"
        ])
        presets_layout.addWidget(QLabel("选择预设:"))
        presets_layout.addWidget(self.presets_combo)
        
        # 预设描述
        self.preset_description = QTextEdit()
        self.preset_description.setMaximumHeight(100)
        self.preset_description.setReadOnly(True)
        presets_layout.addWidget(QLabel("预设描述:"))
        presets_layout.addWidget(self.preset_description)
        
        # 应用预设按钮
        apply_preset_btn = QPushButton("应用预设")
        apply_preset_btn.clicked.connect(self.apply_preset)
        presets_layout.addWidget(apply_preset_btn)
        
        layout.addWidget(presets_group)
        
        # 保存预设组
        save_group = QGroupBox("保存预设")
        save_layout = QFormLayout(save_group)
        
        self.preset_name_edit = QLineEdit()
        save_layout.addRow("预设名称:", self.preset_name_edit)
        
        save_preset_btn = QPushButton("保存当前配置为预设")
        save_preset_btn.clicked.connect(self.save_preset)
        save_layout.addRow(save_preset_btn)
        
        layout.addWidget(save_group)
        
        # 连接信号
        self.presets_combo.currentTextChanged.connect(self.on_preset_changed)
        
        # 初始化预设描述
        self.on_preset_changed()
        
        return widget
    
    def on_laser_type_changed(self):
        """激光类型改变处理"""
        laser_type = self.laser_type_combo.currentText()
        is_pulsed = laser_type in ["脉冲激光", "准连续激光"]
        
        self.pulse_duration_spin.setEnabled(is_pulsed)
        self.pulse_frequency_spin.setEnabled(is_pulsed)
        self.pulse_group.setEnabled(is_pulsed)
    
    def on_beam_profile_changed(self):
        """光束轮廓改变处理"""
        profile = self.beam_profile_combo.currentText()
        is_super_gaussian = profile == "超高斯光束"
        
        self.super_gaussian_order_spin.setEnabled(is_super_gaussian)
    
    def on_preset_changed(self):
        """预设改变处理"""
        preset_name = self.presets_combo.currentText()
        
        descriptions = {
            "1kW连续激光器": "标准1kW连续激光器配置，适用于一般毁伤测试",
            "10kW连续激光器": "高功率10kW连续激光器配置，适用于重型目标毁伤",
            "高功率脉冲激光器": "高峰值功率脉冲激光器配置，适用于精确毁伤",
            "精密加工激光器": "精密加工用激光器配置，光束质量优良",
            "自定义配置": "用户自定义的激光器配置"
        }
        
        self.preset_description.setText(descriptions.get(preset_name, ""))
    
    def apply_preset(self):
        """应用预设配置"""
        preset_name = self.presets_combo.currentText()
        
        presets = {
            "1kW连续激光器": {
                "power": 1000.0,
                "wavelength": 1064.0,
                "beam_diameter": 0.01,
                "laser_type": "连续激光",
                "beam_quality": 1.2,
                "divergence": 1.0
            },
            "10kW连续激光器": {
                "power": 10000.0,
                "wavelength": 1070.0,
                "beam_diameter": 0.02,
                "laser_type": "连续激光",
                "beam_quality": 1.5,
                "divergence": 2.0
            },
            "高功率脉冲激光器": {
                "power": 1000000.0,
                "wavelength": 1064.0,
                "beam_diameter": 0.005,
                "laser_type": "脉冲激光",
                "beam_quality": 1.1,
                "divergence": 0.5,
                "pulse_duration": 1e-9,
                "pulse_frequency": 1000.0
            },
            "精密加工激光器": {
                "power": 500.0,
                "wavelength": 532.0,
                "beam_diameter": 0.002,
                "laser_type": "连续激光",
                "beam_quality": 1.05,
                "divergence": 0.2
            }
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            
            self.power_spin.setValue(preset["power"])
            self.wavelength_spin.setValue(preset["wavelength"])
            self.beam_diameter_spin.setValue(preset["beam_diameter"])
            self.laser_type_combo.setCurrentText(preset["laser_type"])
            self.beam_quality_spin.setValue(preset["beam_quality"])
            self.divergence_spin.setValue(preset["divergence"])
            
            if "pulse_duration" in preset:
                self.pulse_duration_spin.setValue(preset["pulse_duration"])
            if "pulse_frequency" in preset:
                self.pulse_frequency_spin.setValue(preset["pulse_frequency"])
    
    def save_preset(self):
        """保存预设配置"""
        # 简化实现，实际可以保存到文件
        preset_name = self.preset_name_edit.text()
        if preset_name:
            self.presets_combo.addItem(preset_name)
            self.presets_combo.setCurrentText(preset_name)
    
    def load_parameters(self):
        """加载参数"""
        if self.laser_params:
            self.power_spin.setValue(self.laser_params.power)
            self.wavelength_spin.setValue(self.laser_params.wavelength)
            self.beam_diameter_spin.setValue(self.laser_params.beam_diameter)
            
            # 设置激光类型
            laser_type_map = {
                LaserType.CONTINUOUS: "连续激光",
                LaserType.PULSED: "脉冲激光",
                LaserType.QUASI_CONTINUOUS: "准连续激光"
            }
            self.laser_type_combo.setCurrentText(laser_type_map.get(self.laser_params.laser_type, "连续激光"))
            
            if hasattr(self.laser_params, 'pulse_duration'):
                self.pulse_duration_spin.setValue(self.laser_params.pulse_duration)
            if hasattr(self.laser_params, 'pulse_frequency'):
                self.pulse_frequency_spin.setValue(self.laser_params.pulse_frequency)
            if hasattr(self.laser_params, 'beam_quality'):
                self.beam_quality_spin.setValue(self.laser_params.beam_quality)
            if hasattr(self.laser_params, 'divergence_angle'):
                self.divergence_spin.setValue(self.laser_params.divergence_angle)
    
    def apply_parameters(self):
        """应用参数"""
        # 这里可以添加参数验证和应用逻辑
        pass
    
    def get_laser_parameters(self) -> LaserParameters:
        """获取激光参数"""
        # 激光类型映射
        laser_type_map = {
            "连续激光": LaserType.CONTINUOUS,
            "脉冲激光": LaserType.PULSED,
            "准连续激光": LaserType.QUASI_CONTINUOUS
        }
        
        laser_type = laser_type_map.get(self.laser_type_combo.currentText(), LaserType.CONTINUOUS)
        
        params = LaserParameters(
            power=self.power_spin.value(),
            wavelength=self.wavelength_spin.value(),
            beam_diameter=self.beam_diameter_spin.value(),
            laser_type=laser_type
        )
        
        # 添加可选参数
        if laser_type in [LaserType.PULSED, LaserType.QUASI_CONTINUOUS]:
            params.pulse_duration = self.pulse_duration_spin.value()
            params.pulse_frequency = self.pulse_frequency_spin.value()
        
        params.beam_quality = self.beam_quality_spin.value()
        params.divergence_angle = self.divergence_spin.value()
        
        return params

"""
仿真设置面板

提供激光毁伤仿真参数的配置界面。
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox,
    QPushButton, QFileDialog, QTextEdit, QTabWidget, QFormLayout,
    QCheckBox, QSlider, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
from pathlib import Path
from typing import Dict, Any, Optional


class SimulationPanel(QWidget):
    """仿真设置面板"""
    
    # 信号定义
    simulation_requested = pyqtSignal(dict)  # 请求开始仿真
    parameters_changed = pyqtSignal()  # 参数发生变化
    
    def __init__(self):
        super().__init__()
        self.model_file_path: Optional[str] = None
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建标签页
        tab_widget = QTabWidget()
        
        # 模型设置标签页
        model_tab = self.create_model_tab()
        tab_widget.addTab(model_tab, "模型设置")
        
        # 激光参数标签页
        laser_tab = self.create_laser_tab()
        tab_widget.addTab(laser_tab, "激光参数")
        
        # 材料参数标签页
        material_tab = self.create_material_tab()
        tab_widget.addTab(material_tab, "材料参数")
        
        # 环境参数标签页
        environment_tab = self.create_environment_tab()
        tab_widget.addTab(environment_tab, "环境参数")
        
        layout.addWidget(tab_widget)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        # 验证参数按钮
        self.validate_btn = QPushButton("验证参数")
        self.validate_btn.clicked.connect(self.validate_parameters)
        control_layout.addWidget(self.validate_btn)
        
        # 重置按钮
        reset_btn = QPushButton("重置参数")
        reset_btn.clicked.connect(self.reset_parameters)
        control_layout.addWidget(reset_btn)
        
        # 开始仿真按钮
        self.start_btn = QPushButton("开始仿真")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                font-size: 14px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.start_btn.clicked.connect(self.start_simulation)
        control_layout.addWidget(self.start_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
    
    def create_model_tab(self) -> QWidget:
        """创建模型设置标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 模型文件选择组
        model_group = QGroupBox("3D模型文件")
        model_layout = QVBoxLayout(model_group)
        
        # 文件路径显示和选择
        file_layout = QHBoxLayout()
        
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText("请选择3D模型文件...")
        self.model_path_edit.setReadOnly(True)
        file_layout.addWidget(self.model_path_edit)
        
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_model_file)
        file_layout.addWidget(browse_btn)
        
        model_layout.addLayout(file_layout)
        
        # 支持的文件格式说明
        format_label = QLabel("支持的格式: STEP (.step, .stp), IGES (.iges, .igs), SAT (.sat), Parasolid (.x_t)")
        format_label.setStyleSheet("color: #666; font-size: 10px;")
        model_layout.addWidget(format_label)
        
        layout.addWidget(model_group)
        
        # 网格设置组
        mesh_group = QGroupBox("网格设置")
        mesh_layout = QFormLayout(mesh_group)
        
        # 单元大小
        self.element_size_spin = QDoubleSpinBox()
        self.element_size_spin.setRange(0.1, 100.0)
        self.element_size_spin.setValue(1.0)
        self.element_size_spin.setSuffix(" mm")
        self.element_size_spin.setDecimals(2)
        mesh_layout.addRow("单元大小:", self.element_size_spin)
        
        # 网格质量
        self.mesh_quality_combo = QComboBox()
        self.mesh_quality_combo.addItems(["粗糙", "中等", "精细", "超精细"])
        self.mesh_quality_combo.setCurrentText("中等")
        mesh_layout.addRow("网格质量:", self.mesh_quality_combo)
        
        # 自适应网格
        self.adaptive_mesh_check = QCheckBox("启用自适应网格细化")
        mesh_layout.addRow("", self.adaptive_mesh_check)
        
        layout.addWidget(mesh_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        return widget
    
    def create_laser_tab(self) -> QWidget:
        """创建激光参数标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本激光参数组
        basic_group = QGroupBox("基本激光参数")
        basic_layout = QFormLayout(basic_group)
        
        # 激光功率
        self.power_spin = QDoubleSpinBox()
        self.power_spin.setRange(1.0, 100000.0)
        self.power_spin.setValue(1000.0)
        self.power_spin.setSuffix(" W")
        self.power_spin.setDecimals(1)
        basic_layout.addRow("激光功率:", self.power_spin)
        
        # 波长
        self.wavelength_spin = QDoubleSpinBox()
        self.wavelength_spin.setRange(200.0, 12000.0)
        self.wavelength_spin.setValue(1064.0)
        self.wavelength_spin.setSuffix(" nm")
        self.wavelength_spin.setDecimals(1)
        basic_layout.addRow("波长:", self.wavelength_spin)
        
        # 光斑直径
        self.beam_diameter_spin = QDoubleSpinBox()
        self.beam_diameter_spin.setRange(0.1, 100.0)
        self.beam_diameter_spin.setValue(5.0)
        self.beam_diameter_spin.setSuffix(" mm")
        self.beam_diameter_spin.setDecimals(2)
        basic_layout.addRow("光斑直径:", self.beam_diameter_spin)
        
        layout.addWidget(basic_group)
        
        # 脉冲参数组
        pulse_group = QGroupBox("脉冲参数")
        pulse_layout = QFormLayout(pulse_group)
        
        # 脉冲持续时间
        self.pulse_duration_spin = QDoubleSpinBox()
        self.pulse_duration_spin.setRange(1e-12, 1.0)
        self.pulse_duration_spin.setValue(0.001)
        self.pulse_duration_spin.setSuffix(" s")
        self.pulse_duration_spin.setDecimals(6)
        self.pulse_duration_spin.setSpecialValueText("连续激光")
        pulse_layout.addRow("脉冲持续时间:", self.pulse_duration_spin)
        
        # 重复频率
        self.repetition_rate_spin = QDoubleSpinBox()
        self.repetition_rate_spin.setRange(0.1, 10000.0)
        self.repetition_rate_spin.setValue(1.0)
        self.repetition_rate_spin.setSuffix(" Hz")
        self.repetition_rate_spin.setDecimals(1)
        pulse_layout.addRow("重复频率:", self.repetition_rate_spin)
        
        layout.addWidget(pulse_group)
        
        # 光束特性组
        beam_group = QGroupBox("光束特性")
        beam_layout = QFormLayout(beam_group)
        
        # 光束轮廓
        self.beam_profile_combo = QComboBox()
        self.beam_profile_combo.addItems(["高斯分布", "平顶分布", "环形分布"])
        beam_layout.addRow("光束轮廓:", self.beam_profile_combo)
        
        # 发散角
        self.divergence_spin = QDoubleSpinBox()
        self.divergence_spin.setRange(0.0, 100.0)
        self.divergence_spin.setValue(0.0)
        self.divergence_spin.setSuffix(" mrad")
        self.divergence_spin.setDecimals(2)
        beam_layout.addRow("发散角:", self.divergence_spin)
        
        layout.addWidget(beam_group)
        
        # 功率密度显示
        power_density_group = QGroupBox("计算结果")
        power_density_layout = QFormLayout(power_density_group)
        
        self.power_density_label = QLabel("0.0 W/cm²")
        self.power_density_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        power_density_layout.addRow("功率密度:", self.power_density_label)
        
        layout.addWidget(power_density_group)
        
        # 连接信号以实时计算功率密度
        self.power_spin.valueChanged.connect(self.calculate_power_density)
        self.beam_diameter_spin.valueChanged.connect(self.calculate_power_density)
        
        # 初始计算
        self.calculate_power_density()
        
        layout.addStretch()
        return widget
    
    def create_material_tab(self) -> QWidget:
        """创建材料参数标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 材料选择组
        material_select_group = QGroupBox("材料选择")
        material_select_layout = QVBoxLayout(material_select_group)
        
        # 预设材料
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设材料:"))
        
        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "自定义", "铝合金 6061", "不锈钢 304", "钛合金 Ti-6Al-4V", 
            "碳纤维复合材料", "铜", "钢"
        ])
        self.material_combo.currentTextChanged.connect(self.load_preset_material)
        preset_layout.addWidget(self.material_combo)
        
        preset_layout.addStretch()
        material_select_layout.addLayout(preset_layout)
        
        layout.addWidget(material_select_group)
        
        # 热物性参数组
        thermal_group = QGroupBox("热物性参数")
        thermal_layout = QFormLayout(thermal_group)
        
        # 热导率
        self.thermal_conductivity_spin = QDoubleSpinBox()
        self.thermal_conductivity_spin.setRange(0.1, 1000.0)
        self.thermal_conductivity_spin.setValue(167.0)
        self.thermal_conductivity_spin.setSuffix(" W/m·K")
        self.thermal_conductivity_spin.setDecimals(1)
        thermal_layout.addRow("热导率:", self.thermal_conductivity_spin)
        
        # 比热容
        self.specific_heat_spin = QDoubleSpinBox()
        self.specific_heat_spin.setRange(100.0, 5000.0)
        self.specific_heat_spin.setValue(896.0)
        self.specific_heat_spin.setSuffix(" J/kg·K")
        self.specific_heat_spin.setDecimals(1)
        thermal_layout.addRow("比热容:", self.specific_heat_spin)
        
        # 密度
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(100.0, 20000.0)
        self.density_spin.setValue(2700.0)
        self.density_spin.setSuffix(" kg/m³")
        self.density_spin.setDecimals(1)
        thermal_layout.addRow("密度:", self.density_spin)
        
        # 熔点
        self.melting_point_spin = QDoubleSpinBox()
        self.melting_point_spin.setRange(200.0, 4000.0)
        self.melting_point_spin.setValue(933.0)
        self.melting_point_spin.setSuffix(" K")
        self.melting_point_spin.setDecimals(1)
        thermal_layout.addRow("熔点:", self.melting_point_spin)
        
        layout.addWidget(thermal_group)
        
        # 光学参数组
        optical_group = QGroupBox("光学参数")
        optical_layout = QFormLayout(optical_group)
        
        # 吸收系数
        self.absorption_spin = QDoubleSpinBox()
        self.absorption_spin.setRange(0.01, 1.0)
        self.absorption_spin.setValue(0.1)
        self.absorption_spin.setDecimals(3)
        optical_layout.addRow("吸收系数:", self.absorption_spin)
        
        # 反射率
        self.reflectivity_spin = QDoubleSpinBox()
        self.reflectivity_spin.setRange(0.0, 0.99)
        self.reflectivity_spin.setValue(0.9)
        self.reflectivity_spin.setDecimals(3)
        optical_layout.addRow("反射率:", self.reflectivity_spin)
        
        layout.addWidget(optical_group)
        
        layout.addStretch()
        return widget
    
    def create_environment_tab(self) -> QWidget:
        """创建环境参数标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 环境条件组
        env_group = QGroupBox("环境条件")
        env_layout = QFormLayout(env_group)
        
        # 环境温度
        self.ambient_temp_spin = QDoubleSpinBox()
        self.ambient_temp_spin.setRange(200.0, 400.0)
        self.ambient_temp_spin.setValue(293.15)
        self.ambient_temp_spin.setSuffix(" K")
        self.ambient_temp_spin.setDecimals(2)
        env_layout.addRow("环境温度:", self.ambient_temp_spin)
        
        # 压力
        self.pressure_spin = QDoubleSpinBox()
        self.pressure_spin.setRange(1000.0, 200000.0)
        self.pressure_spin.setValue(101325.0)
        self.pressure_spin.setSuffix(" Pa")
        self.pressure_spin.setDecimals(1)
        env_layout.addRow("压力:", self.pressure_spin)
        
        # 相对湿度
        self.humidity_spin = QDoubleSpinBox()
        self.humidity_spin.setRange(0.0, 1.0)
        self.humidity_spin.setValue(0.5)
        self.humidity_spin.setDecimals(2)
        env_layout.addRow("相对湿度:", self.humidity_spin)
        
        layout.addWidget(env_group)
        
        # 大气参数组
        atm_group = QGroupBox("大气参数")
        atm_layout = QFormLayout(atm_group)
        
        # 风速
        self.wind_speed_spin = QDoubleSpinBox()
        self.wind_speed_spin.setRange(0.0, 50.0)
        self.wind_speed_spin.setValue(0.0)
        self.wind_speed_spin.setSuffix(" m/s")
        self.wind_speed_spin.setDecimals(1)
        atm_layout.addRow("风速:", self.wind_speed_spin)
        
        # 大气透过率
        self.transmission_spin = QDoubleSpinBox()
        self.transmission_spin.setRange(0.1, 1.0)
        self.transmission_spin.setValue(0.8)
        self.transmission_spin.setDecimals(3)
        atm_layout.addRow("大气透过率:", self.transmission_spin)
        
        layout.addWidget(atm_group)
        
        layout.addStretch()
        return widget
    
    def connect_signals(self):
        """连接信号"""
        # 参数变化信号
        widgets_to_connect = [
            self.power_spin, self.wavelength_spin, self.beam_diameter_spin,
            self.thermal_conductivity_spin, self.specific_heat_spin, self.density_spin
        ]
        
        for widget in widgets_to_connect:
            widget.valueChanged.connect(self.parameters_changed.emit)
    
    def browse_model_file(self):
        """浏览模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择3D模型文件', '',
            'CAD Files (*.step *.stp *.iges *.igs *.sat *.x_t);;All Files (*)'
        )
        
        if file_path:
            self.model_file_path = file_path
            self.model_path_edit.setText(file_path)
    
    def calculate_power_density(self):
        """计算功率密度"""
        power = self.power_spin.value()  # W
        diameter = self.beam_diameter_spin.value()  # mm
        
        if diameter > 0:
            radius_cm = diameter / 20.0  # 转换为cm
            area_cm2 = 3.14159 * radius_cm * radius_cm
            power_density = power / area_cm2 if area_cm2 > 0 else 0
            self.power_density_label.setText(f"{power_density:.1f} W/cm²")
        else:
            self.power_density_label.setText("0.0 W/cm²")
    
    def load_preset_material(self, material_name: str):
        """加载预设材料参数"""
        materials = {
            "铝合金 6061": {
                "thermal_conductivity": 167.0,
                "specific_heat": 896.0,
                "density": 2700.0,
                "melting_point": 933.0,
                "absorption": 0.1,
                "reflectivity": 0.9
            },
            "不锈钢 304": {
                "thermal_conductivity": 16.2,
                "specific_heat": 500.0,
                "density": 8000.0,
                "melting_point": 1673.0,
                "absorption": 0.3,
                "reflectivity": 0.7
            },
            "钛合金 Ti-6Al-4V": {
                "thermal_conductivity": 6.7,
                "specific_heat": 526.0,
                "density": 4430.0,
                "melting_point": 1933.0,
                "absorption": 0.4,
                "reflectivity": 0.6
            }
        }
        
        if material_name in materials:
            params = materials[material_name]
            self.thermal_conductivity_spin.setValue(params["thermal_conductivity"])
            self.specific_heat_spin.setValue(params["specific_heat"])
            self.density_spin.setValue(params["density"])
            self.melting_point_spin.setValue(params["melting_point"])
            self.absorption_spin.setValue(params["absorption"])
            self.reflectivity_spin.setValue(params["reflectivity"])
    
    def validate_parameters(self):
        """验证参数"""
        errors = []
        
        # 检查模型文件
        if not self.model_file_path:
            errors.append("请选择3D模型文件")
        elif not Path(self.model_file_path).exists():
            errors.append("模型文件不存在")
        
        # 检查激光参数
        if self.power_spin.value() <= 0:
            errors.append("激光功率必须大于0")
        
        if self.beam_diameter_spin.value() <= 0:
            errors.append("光斑直径必须大于0")
        
        # 检查材料参数
        if self.thermal_conductivity_spin.value() <= 0:
            errors.append("热导率必须大于0")
        
        if errors:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, '参数验证', '\n'.join(errors))
            return False
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, '参数验证', '所有参数验证通过！')
            return True
    
    def reset_parameters(self):
        """重置参数到默认值"""
        # 重置激光参数
        self.power_spin.setValue(1000.0)
        self.wavelength_spin.setValue(1064.0)
        self.beam_diameter_spin.setValue(5.0)
        self.pulse_duration_spin.setValue(0.001)
        self.repetition_rate_spin.setValue(1.0)
        
        # 重置材料参数
        self.material_combo.setCurrentText("铝合金 6061")
        self.load_preset_material("铝合金 6061")
        
        # 重置环境参数
        self.ambient_temp_spin.setValue(293.15)
        self.pressure_spin.setValue(101325.0)
        self.humidity_spin.setValue(0.5)
        self.wind_speed_spin.setValue(0.0)
        self.transmission_spin.setValue(0.8)
        
        # 清除模型文件
        self.model_file_path = None
        self.model_path_edit.clear()
    
    def start_simulation(self):
        """开始仿真"""
        if self.validate_parameters():
            config = self.get_simulation_config()
            self.simulation_requested.emit(config)
    
    def get_simulation_config(self) -> Optional[Dict[str, Any]]:
        """获取仿真配置"""
        if not self.model_file_path:
            return None
        
        return {
            "model_path": self.model_file_path,
            "laser_parameters": {
                "power": self.power_spin.value(),
                "wavelength": self.wavelength_spin.value(),
                "beam_diameter": self.beam_diameter_spin.value(),
                "pulse_duration": self.pulse_duration_spin.value(),
                "repetition_rate": self.repetition_rate_spin.value(),
                "beam_profile": self.beam_profile_combo.currentText(),
                "divergence_angle": self.divergence_spin.value()
            },
            "material_parameters": {
                "name": self.material_combo.currentText(),
                "thermal_conductivity": self.thermal_conductivity_spin.value(),
                "specific_heat": self.specific_heat_spin.value(),
                "density": self.density_spin.value(),
                "melting_point": self.melting_point_spin.value(),
                "absorption_coefficient": self.absorption_spin.value(),
                "reflectivity": self.reflectivity_spin.value()
            },
            "environment_parameters": {
                "ambient_temperature": self.ambient_temp_spin.value(),
                "pressure": self.pressure_spin.value(),
                "humidity": self.humidity_spin.value(),
                "wind_speed": self.wind_speed_spin.value(),
                "atmospheric_transmission": self.transmission_spin.value()
            },
            "mesh_parameters": {
                "element_size": self.element_size_spin.value(),
                "mesh_quality": self.mesh_quality_combo.currentText(),
                "adaptive_mesh": self.adaptive_mesh_check.isChecked()
            }
        }
    
    def reset(self):
        """重置面板"""
        self.reset_parameters()

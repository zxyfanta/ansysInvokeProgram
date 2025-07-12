"""
GUI - 增强版仿真控制面板

支持飞行器模型的仿真控制界面组件。
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QPushButton, QLabel, QProgressBar, QGroupBox,
        QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox,
        QLineEdit, QTextEdit, QTabWidget, QFrame
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont, QColor, QPalette
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

if PYQT5_AVAILABLE:
    from aircraft_modeling.aircraft_types import AircraftType
    from aircraft_modeling.fluid_domain_setup import FlightConditions

class EnhancedSimulationControlPanel(QWidget):
    """增强版仿真控制面板"""
    
    # 信号定义
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    aircraft_modeling_requested = pyqtSignal()
    flight_conditions_changed = pyqtSignal(object)  # FlightConditions对象
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5不可用，无法创建控制面板")
        
        # 当前状态
        self.aircraft_model: Optional[Dict[str, Any]] = None
        self.flight_conditions: Optional[FlightConditions] = None
        self.simulation_running = False
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        self.tab_widget = QTabWidget()
        
        # 模型配置选项卡
        self.model_tab = self.create_model_tab()
        self.tab_widget.addTab(self.model_tab, "模型配置")
        
        # 飞行条件选项卡
        self.flight_tab = self.create_flight_conditions_tab()
        self.tab_widget.addTab(self.flight_tab, "飞行条件")
        
        # 仿真控制选项卡
        self.control_tab = self.create_simulation_control_tab()
        self.tab_widget.addTab(self.control_tab, "仿真控制")
        
        layout.addWidget(self.tab_widget)
        
        # 状态显示
        self.status_group = self.create_status_group()
        layout.addWidget(self.status_group)
    
    def create_model_tab(self) -> QWidget:
        """创建模型配置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 飞行器模型状态
        model_group = QGroupBox("飞行器模型")
        model_layout = QGridLayout()
        
        model_layout.addWidget(QLabel("模型状态:"), 0, 0)
        self.model_status_label = QLabel("未配置")
        self.model_status_label.setStyleSheet("color: red; font-weight: bold;")
        model_layout.addWidget(self.model_status_label, 0, 1)
        
        self.aircraft_modeling_btn = QPushButton("飞行器建模")
        self.aircraft_modeling_btn.clicked.connect(self.aircraft_modeling_requested.emit)
        model_layout.addWidget(self.aircraft_modeling_btn, 0, 2)
        
        model_layout.addWidget(QLabel("模型名称:"), 1, 0)
        self.model_name_label = QLabel("无")
        model_layout.addWidget(self.model_name_label, 1, 1, 1, 2)
        
        model_layout.addWidget(QLabel("模型类型:"), 2, 0)
        self.model_type_label = QLabel("无")
        model_layout.addWidget(self.model_type_label, 2, 1, 1, 2)
        
        model_layout.addWidget(QLabel("模型尺寸:"), 3, 0)
        self.model_dimensions_label = QLabel("无")
        model_layout.addWidget(self.model_dimensions_label, 3, 1, 1, 2)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # 网格配置
        mesh_group = QGroupBox("网格配置")
        mesh_layout = QGridLayout()
        
        mesh_layout.addWidget(QLabel("最大单元尺寸:"), 0, 0)
        self.max_element_size_spin = QDoubleSpinBox()
        self.max_element_size_spin.setRange(0.001, 1.0)
        self.max_element_size_spin.setValue(0.05)
        self.max_element_size_spin.setSuffix(" m")
        mesh_layout.addWidget(self.max_element_size_spin, 0, 1)
        
        mesh_layout.addWidget(QLabel("边界层层数:"), 1, 0)
        self.boundary_layers_spin = QSpinBox()
        self.boundary_layers_spin.setRange(0, 20)
        self.boundary_layers_spin.setValue(5)
        mesh_layout.addWidget(self.boundary_layers_spin, 1, 1)
        
        mesh_layout.addWidget(QLabel("网格类型:"), 2, 0)
        self.mesh_type_combo = QComboBox()
        self.mesh_type_combo.addItems(["非结构化网格", "结构化网格", "混合网格"])
        mesh_layout.addWidget(self.mesh_type_combo, 2, 1)
        
        mesh_group.setLayout(mesh_layout)
        layout.addWidget(mesh_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_flight_conditions_tab(self) -> QWidget:
        """创建飞行条件选项卡"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 基本飞行参数
        basic_group = QGroupBox("基本飞行参数")
        basic_layout = QGridLayout()
        
        basic_layout.addWidget(QLabel("高度:"), 0, 0)
        self.altitude_spin = QDoubleSpinBox()
        self.altitude_spin.setRange(0, 30000)
        self.altitude_spin.setValue(0)
        self.altitude_spin.setSuffix(" m")
        basic_layout.addWidget(self.altitude_spin, 0, 1)
        
        basic_layout.addWidget(QLabel("马赫数:"), 0, 2)
        self.mach_spin = QDoubleSpinBox()
        self.mach_spin.setRange(0.1, 5.0)
        self.mach_spin.setValue(0.3)
        self.mach_spin.setDecimals(2)
        basic_layout.addWidget(self.mach_spin, 0, 3)
        
        basic_layout.addWidget(QLabel("速度:"), 1, 0)
        self.velocity_spin = QDoubleSpinBox()
        self.velocity_spin.setRange(10, 2000)
        self.velocity_spin.setValue(100)
        self.velocity_spin.setSuffix(" m/s")
        basic_layout.addWidget(self.velocity_spin, 1, 1)
        
        basic_layout.addWidget(QLabel("攻角:"), 1, 2)
        self.aoa_spin = QDoubleSpinBox()
        self.aoa_spin.setRange(-30, 30)
        self.aoa_spin.setValue(0)
        self.aoa_spin.setSuffix(" °")
        basic_layout.addWidget(self.aoa_spin, 1, 3)
        
        basic_layout.addWidget(QLabel("侧滑角:"), 2, 0)
        self.sideslip_spin = QDoubleSpinBox()
        self.sideslip_spin.setRange(-30, 30)
        self.sideslip_spin.setValue(0)
        self.sideslip_spin.setSuffix(" °")
        basic_layout.addWidget(self.sideslip_spin, 2, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 大气条件
        atmosphere_group = QGroupBox("大气条件")
        atmosphere_layout = QGridLayout()
        
        atmosphere_layout.addWidget(QLabel("温度:"), 0, 0)
        self.temperature_spin = QDoubleSpinBox()
        self.temperature_spin.setRange(200, 350)
        self.temperature_spin.setValue(288.15)
        self.temperature_spin.setSuffix(" K")
        atmosphere_layout.addWidget(self.temperature_spin, 0, 1)
        
        atmosphere_layout.addWidget(QLabel("压力:"), 0, 2)
        self.pressure_spin = QDoubleSpinBox()
        self.pressure_spin.setRange(1000, 120000)
        self.pressure_spin.setValue(101325)
        self.pressure_spin.setSuffix(" Pa")
        atmosphere_layout.addWidget(self.pressure_spin, 0, 3)
        
        atmosphere_layout.addWidget(QLabel("密度:"), 1, 0)
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0.1, 2.0)
        self.density_spin.setValue(1.225)
        self.density_spin.setSuffix(" kg/m³")
        atmosphere_layout.addWidget(self.density_spin, 1, 1)
        
        # 标准大气按钮
        self.std_atmosphere_btn = QPushButton("标准大气")
        self.std_atmosphere_btn.clicked.connect(self.set_standard_atmosphere)
        atmosphere_layout.addWidget(self.std_atmosphere_btn, 1, 2, 1, 2)
        
        atmosphere_group.setLayout(atmosphere_layout)
        layout.addWidget(atmosphere_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_simulation_control_tab(self) -> QWidget:
        """创建仿真控制选项卡"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 仿真控制按钮
        control_group = QGroupBox("仿真控制")
        control_layout = QGridLayout()
        
        self.start_btn = QPushButton("开始仿真")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        control_layout.addWidget(self.start_btn, 0, 0)
        
        self.pause_btn = QPushButton("暂停仿真")
        self.pause_btn.setMinimumHeight(50)
        self.pause_btn.setEnabled(False)
        control_layout.addWidget(self.pause_btn, 0, 1)
        
        self.stop_btn = QPushButton("停止仿真")
        self.stop_btn.setMinimumHeight(50)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; font-weight: bold; }")
        control_layout.addWidget(self.stop_btn, 0, 2)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # 仿真选项
        options_group = QGroupBox("仿真选项")
        options_layout = QGridLayout()
        
        self.thermal_analysis_check = QCheckBox("热分析")
        self.thermal_analysis_check.setChecked(True)
        options_layout.addWidget(self.thermal_analysis_check, 0, 0)
        
        self.structural_analysis_check = QCheckBox("结构分析")
        self.structural_analysis_check.setChecked(True)
        options_layout.addWidget(self.structural_analysis_check, 0, 1)
        
        self.aerodynamic_analysis_check = QCheckBox("气动分析")
        self.aerodynamic_analysis_check.setChecked(True)
        options_layout.addWidget(self.aerodynamic_analysis_check, 1, 0)
        
        self.comprehensive_assessment_check = QCheckBox("综合评估")
        self.comprehensive_assessment_check.setChecked(True)
        options_layout.addWidget(self.comprehensive_assessment_check, 1, 1)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 进度显示
        progress_group = QGroupBox("仿真进度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("就绪")
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_status_group(self) -> QGroupBox:
        """创建状态显示组"""
        status_group = QGroupBox("系统状态")
        status_layout = QGridLayout()
        
        # 配置状态指示器
        status_layout.addWidget(QLabel("飞行器模型:"), 0, 0)
        self.aircraft_status_indicator = QLabel("●")
        self.aircraft_status_indicator.setStyleSheet("color: red; font-size: 16px;")
        status_layout.addWidget(self.aircraft_status_indicator, 0, 1)
        
        status_layout.addWidget(QLabel("激光参数:"), 0, 2)
        self.laser_status_indicator = QLabel("●")
        self.laser_status_indicator.setStyleSheet("color: red; font-size: 16px;")
        status_layout.addWidget(self.laser_status_indicator, 0, 3)
        
        status_layout.addWidget(QLabel("飞行条件:"), 1, 0)
        self.flight_status_indicator = QLabel("●")
        self.flight_status_indicator.setStyleSheet("color: orange; font-size: 16px;")
        status_layout.addWidget(self.flight_status_indicator, 1, 1)
        
        status_layout.addWidget(QLabel("网格生成:"), 1, 2)
        self.mesh_status_indicator = QLabel("●")
        self.mesh_status_indicator.setStyleSheet("color: red; font-size: 16px;")
        status_layout.addWidget(self.mesh_status_indicator, 1, 3)
        
        status_group.setLayout(status_layout)
        return status_group
    
    def setup_connections(self):
        """设置信号连接"""
        # 仿真控制按钮
        self.start_btn.clicked.connect(self.start_requested.emit)
        self.pause_btn.clicked.connect(self.pause_requested.emit)
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        
        # 飞行条件变化
        self.altitude_spin.valueChanged.connect(self.on_flight_conditions_changed)
        self.mach_spin.valueChanged.connect(self.on_flight_conditions_changed)
        self.velocity_spin.valueChanged.connect(self.on_flight_conditions_changed)
        self.aoa_spin.valueChanged.connect(self.on_flight_conditions_changed)
        self.sideslip_spin.valueChanged.connect(self.on_flight_conditions_changed)
        self.temperature_spin.valueChanged.connect(self.on_flight_conditions_changed)
        self.pressure_spin.valueChanged.connect(self.on_flight_conditions_changed)
        self.density_spin.valueChanged.connect(self.on_flight_conditions_changed)
    
    def set_aircraft_model(self, model_data: Dict[str, Any]):
        """设置飞行器模型"""
        self.aircraft_model = model_data
        
        # 更新界面显示
        metadata = model_data.get('metadata', {})
        self.model_name_label.setText(metadata.get('name', '未知'))
        self.model_type_label.setText(metadata.get('aircraft_type', '未知'))
        
        # 更新尺寸信息
        if 'dimensions' in model_data:
            dims = model_data['dimensions']
            dimensions_text = f"长:{dims.get('length', 0):.1f}m, 宽:{dims.get('wingspan', 0):.1f}m, 高:{dims.get('height', 0):.1f}m"
            self.model_dimensions_label.setText(dimensions_text)
        
        # 更新状态
        self.model_status_label.setText("已配置")
        self.model_status_label.setStyleSheet("color: green; font-weight: bold;")
        self.aircraft_status_indicator.setStyleSheet("color: green; font-size: 16px;")
        
        # 更新飞行条件状态
        self.flight_status_indicator.setStyleSheet("color: green; font-size: 16px;")
    
    def on_flight_conditions_changed(self):
        """飞行条件改变时的处理"""
        # 创建飞行条件对象
        flight_conditions = FlightConditions(
            altitude=self.altitude_spin.value(),
            mach_number=self.mach_spin.value(),
            velocity=self.velocity_spin.value(),
            angle_of_attack=self.aoa_spin.value(),
            angle_of_sideslip=self.sideslip_spin.value(),
            temperature=self.temperature_spin.value(),
            pressure=self.pressure_spin.value(),
            density=self.density_spin.value()
        )
        
        self.flight_conditions = flight_conditions
        
        # 发射信号
        self.flight_conditions_changed.emit(flight_conditions)
    
    def set_standard_atmosphere(self):
        """设置标准大气条件"""
        altitude = self.altitude_spin.value()
        
        # 标准大气模型（简化）
        if altitude <= 11000:  # 对流层
            temperature = 288.15 - 0.0065 * altitude
            pressure = 101325.0 * (1 - 0.0065 * altitude / 288.15) ** 5.256
        else:  # 平流层（简化）
            temperature = 216.65
            pressure = 22632.0 * np.exp(-0.0001577 * (altitude - 11000))
        
        density = pressure / (287.0 * temperature)
        
        # 更新界面
        self.temperature_spin.setValue(temperature)
        self.pressure_spin.setValue(pressure)
        self.density_spin.setValue(density)
    
    def set_simulation_running(self, running: bool):
        """设置仿真运行状态"""
        self.simulation_running = running
        
        # 更新按钮状态
        self.start_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running)
        self.stop_btn.setEnabled(running)
        
        # 更新界面状态
        if running:
            self.progress_label.setText("仿真运行中...")
        else:
            self.progress_label.setText("就绪")
            self.progress_bar.setValue(0)
    
    def update_progress(self, value: int, message: str = ""):
        """更新进度"""
        self.progress_bar.setValue(value)
        if message:
            self.progress_label.setText(message)
    
    def get_simulation_options(self) -> Dict[str, bool]:
        """获取仿真选项"""
        return {
            'thermal_analysis': self.thermal_analysis_check.isChecked(),
            'structural_analysis': self.structural_analysis_check.isChecked(),
            'aerodynamic_analysis': self.aerodynamic_analysis_check.isChecked(),
            'comprehensive_assessment': self.comprehensive_assessment_check.isChecked()
        }
    
    def get_mesh_parameters(self) -> Dict[str, Any]:
        """获取网格参数"""
        return {
            'max_element_size': self.max_element_size_spin.value(),
            'boundary_layers': self.boundary_layers_spin.value(),
            'mesh_type': self.mesh_type_combo.currentText()
        }
    
    def get_flight_conditions(self) -> Optional[FlightConditions]:
        """获取飞行条件"""
        return self.flight_conditions

"""
GUI - 材料配置对话框

材料参数配置界面。
"""

import sys
from pathlib import Path
from typing import Optional

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QFormLayout, QGroupBox, QDialogButtonBox,
        QLineEdit, QDoubleSpinBox, QComboBox, QTabWidget, QWidget,
        QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
    )
    from PyQt5.QtCore import Qt
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

from core.data_models import MaterialData

class MaterialConfigDialog(QDialog):
    """材料配置对话框"""
    
    def __init__(self, material_data: Optional[MaterialData] = None, parent=None):
        super().__init__(parent)
        
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5不可用，无法创建对话框")
        
        self.material_data = material_data
        self.init_ui()
        self.load_parameters()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("材料参数配置")
        self.setModal(True)
        self.resize(600, 500)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # 基本属性选项卡
        basic_tab = self.create_basic_properties_tab()
        tab_widget.addTab(basic_tab, "基本属性")
        
        # 热学属性选项卡
        thermal_tab = self.create_thermal_properties_tab()
        tab_widget.addTab(thermal_tab, "热学属性")
        
        # 机械属性选项卡
        mechanical_tab = self.create_mechanical_properties_tab()
        tab_widget.addTab(mechanical_tab, "机械属性")
        
        # 材料库选项卡
        database_tab = self.create_material_database_tab()
        tab_widget.addTab(database_tab, "材料库")
        
        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
    
    def create_basic_properties_tab(self) -> QWidget:
        """创建基本属性选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        basic_layout.addRow("材料名称:", self.name_edit)
        
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(100.0, 50000.0)
        self.density_spin.setValue(2780.0)
        self.density_spin.setSuffix(" kg/m³")
        self.density_spin.setDecimals(1)
        basic_layout.addRow("密度:", self.density_spin)
        
        layout.addWidget(basic_group)
        
        # 光学属性组
        optical_group = QGroupBox("光学属性")
        optical_layout = QFormLayout(optical_group)
        
        self.absorptivity_spin = QDoubleSpinBox()
        self.absorptivity_spin.setRange(0.01, 1.0)
        self.absorptivity_spin.setValue(0.15)
        self.absorptivity_spin.setDecimals(3)
        optical_layout.addRow("吸收率:", self.absorptivity_spin)
        
        self.reflectivity_spin = QDoubleSpinBox()
        self.reflectivity_spin.setRange(0.0, 0.99)
        self.reflectivity_spin.setValue(0.85)
        self.reflectivity_spin.setDecimals(3)
        optical_layout.addRow("反射率:", self.reflectivity_spin)
        
        layout.addWidget(optical_group)
        
        return widget
    
    def create_thermal_properties_tab(self) -> QWidget:
        """创建热学属性选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 热学参数组
        thermal_group = QGroupBox("热学参数")
        thermal_layout = QFormLayout(thermal_group)
        
        self.thermal_conductivity_spin = QDoubleSpinBox()
        self.thermal_conductivity_spin.setRange(0.1, 1000.0)
        self.thermal_conductivity_spin.setValue(121.0)
        self.thermal_conductivity_spin.setSuffix(" W/(m·K)")
        self.thermal_conductivity_spin.setDecimals(1)
        thermal_layout.addRow("热导率:", self.thermal_conductivity_spin)
        
        self.specific_heat_spin = QDoubleSpinBox()
        self.specific_heat_spin.setRange(100.0, 5000.0)
        self.specific_heat_spin.setValue(875.0)
        self.specific_heat_spin.setSuffix(" J/(kg·K)")
        self.specific_heat_spin.setDecimals(1)
        thermal_layout.addRow("比热容:", self.specific_heat_spin)
        
        self.thermal_expansion_spin = QDoubleSpinBox()
        self.thermal_expansion_spin.setRange(1e-6, 100e-6)
        self.thermal_expansion_spin.setValue(22.3e-6)
        self.thermal_expansion_spin.setSuffix(" /K")
        self.thermal_expansion_spin.setDecimals(8)
        thermal_layout.addRow("热膨胀系数:", self.thermal_expansion_spin)
        
        layout.addWidget(thermal_group)
        
        # 相变参数组
        phase_group = QGroupBox("相变参数")
        phase_layout = QFormLayout(phase_group)
        
        self.melting_point_spin = QDoubleSpinBox()
        self.melting_point_spin.setRange(200.0, 5000.0)
        self.melting_point_spin.setValue(916.0)
        self.melting_point_spin.setSuffix(" K")
        self.melting_point_spin.setDecimals(1)
        phase_layout.addRow("熔点:", self.melting_point_spin)
        
        self.boiling_point_spin = QDoubleSpinBox()
        self.boiling_point_spin.setRange(500.0, 10000.0)
        self.boiling_point_spin.setValue(2740.0)
        self.boiling_point_spin.setSuffix(" K")
        self.boiling_point_spin.setDecimals(1)
        phase_layout.addRow("沸点:", self.boiling_point_spin)
        
        layout.addWidget(phase_group)
        
        return widget
    
    def create_mechanical_properties_tab(self) -> QWidget:
        """创建机械属性选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 弹性参数组
        elastic_group = QGroupBox("弹性参数")
        elastic_layout = QFormLayout(elastic_group)
        
        self.youngs_modulus_spin = QDoubleSpinBox()
        self.youngs_modulus_spin.setRange(1e9, 1000e9)
        self.youngs_modulus_spin.setValue(73.1e9)
        self.youngs_modulus_spin.setSuffix(" Pa")
        self.youngs_modulus_spin.setDecimals(0)
        elastic_layout.addRow("杨氏模量:", self.youngs_modulus_spin)
        
        self.poissons_ratio_spin = QDoubleSpinBox()
        self.poissons_ratio_spin.setRange(0.1, 0.5)
        self.poissons_ratio_spin.setValue(0.33)
        self.poissons_ratio_spin.setDecimals(3)
        elastic_layout.addRow("泊松比:", self.poissons_ratio_spin)
        
        layout.addWidget(elastic_group)
        
        # 强度参数组
        strength_group = QGroupBox("强度参数")
        strength_layout = QFormLayout(strength_group)
        
        self.yield_strength_spin = QDoubleSpinBox()
        self.yield_strength_spin.setRange(1e6, 5000e6)
        self.yield_strength_spin.setValue(324e6)
        self.yield_strength_spin.setSuffix(" Pa")
        self.yield_strength_spin.setDecimals(0)
        strength_layout.addRow("屈服强度:", self.yield_strength_spin)
        
        self.ultimate_strength_spin = QDoubleSpinBox()
        self.ultimate_strength_spin.setRange(1e6, 5000e6)
        self.ultimate_strength_spin.setValue(483e6)
        self.ultimate_strength_spin.setSuffix(" Pa")
        self.ultimate_strength_spin.setDecimals(0)
        strength_layout.addRow("抗拉强度:", self.ultimate_strength_spin)
        
        layout.addWidget(strength_group)
        
        return widget
    
    def create_material_database_tab(self) -> QWidget:
        """创建材料库选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 材料选择
        material_combo = QComboBox()
        material_combo.addItems([
            "铝合金2024-T3",
            "钢材Q235",
            "钛合金TC4",
            "铜合金",
            "碳纤维复合材料",
            "自定义材料"
        ])
        layout.addWidget(material_combo)
        
        # 应用材料按钮
        apply_material_btn = QPushButton("应用选中材料")
        apply_material_btn.clicked.connect(lambda: self.apply_material(material_combo.currentText()))
        layout.addWidget(apply_material_btn)
        
        # 材料属性表格
        self.material_table = QTableWidget()
        self.material_table.setColumnCount(2)
        self.material_table.setHorizontalHeaderLabels(["属性", "数值"])
        self.material_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.material_table)
        
        return widget
    
    def apply_material(self, material_name: str):
        """应用材料"""
        materials = {
            "铝合金2024-T3": {
                "name": "铝合金2024-T3",
                "density": 2780.0,
                "thermal_conductivity": 121.0,
                "specific_heat": 875.0,
                "melting_point": 916.0,
                "boiling_point": 2740.0,
                "absorptivity": 0.15,
                "youngs_modulus": 73.1e9,
                "poissons_ratio": 0.33,
                "thermal_expansion": 22.3e-6,
                "yield_strength": 324e6
            },
            "钢材Q235": {
                "name": "钢材Q235",
                "density": 7850.0,
                "thermal_conductivity": 50.0,
                "specific_heat": 460.0,
                "melting_point": 1811.0,
                "boiling_point": 3134.0,
                "absorptivity": 0.8,
                "youngs_modulus": 200e9,
                "poissons_ratio": 0.30,
                "thermal_expansion": 12e-6,
                "yield_strength": 235e6
            },
            "钛合金TC4": {
                "name": "钛合金TC4",
                "density": 4430.0,
                "thermal_conductivity": 7.0,
                "specific_heat": 520.0,
                "melting_point": 1933.0,
                "boiling_point": 3560.0,
                "absorptivity": 0.7,
                "youngs_modulus": 114e9,
                "poissons_ratio": 0.34,
                "thermal_expansion": 8.6e-6,
                "yield_strength": 880e6
            }
        }
        
        if material_name in materials:
            material = materials[material_name]
            
            self.name_edit.setText(material["name"])
            self.density_spin.setValue(material["density"])
            self.thermal_conductivity_spin.setValue(material["thermal_conductivity"])
            self.specific_heat_spin.setValue(material["specific_heat"])
            self.melting_point_spin.setValue(material["melting_point"])
            self.boiling_point_spin.setValue(material["boiling_point"])
            self.absorptivity_spin.setValue(material["absorptivity"])
            self.youngs_modulus_spin.setValue(material["youngs_modulus"])
            self.poissons_ratio_spin.setValue(material["poissons_ratio"])
            self.thermal_expansion_spin.setValue(material["thermal_expansion"])
            self.yield_strength_spin.setValue(material["yield_strength"])
            
            # 更新材料属性表格
            self.update_material_table(material)
    
    def update_material_table(self, material: dict):
        """更新材料属性表格"""
        self.material_table.setRowCount(len(material))
        
        for i, (key, value) in enumerate(material.items()):
            self.material_table.setItem(i, 0, QTableWidgetItem(key))
            self.material_table.setItem(i, 1, QTableWidgetItem(str(value)))
    
    def load_parameters(self):
        """加载参数"""
        if self.material_data:
            self.name_edit.setText(self.material_data.name)
            self.density_spin.setValue(self.material_data.density)
            self.thermal_conductivity_spin.setValue(self.material_data.thermal_conductivity)
            self.specific_heat_spin.setValue(self.material_data.specific_heat)
            self.melting_point_spin.setValue(self.material_data.melting_point)
            self.boiling_point_spin.setValue(self.material_data.boiling_point)
            self.absorptivity_spin.setValue(self.material_data.absorptivity)
            self.youngs_modulus_spin.setValue(self.material_data.youngs_modulus)
            self.poissons_ratio_spin.setValue(self.material_data.poissons_ratio)
            self.thermal_expansion_spin.setValue(self.material_data.thermal_expansion)
            self.yield_strength_spin.setValue(self.material_data.yield_strength)
    
    def get_material_data(self) -> MaterialData:
        """获取材料数据"""
        return MaterialData(
            name=self.name_edit.text(),
            density=self.density_spin.value(),
            thermal_conductivity=self.thermal_conductivity_spin.value(),
            specific_heat=self.specific_heat_spin.value(),
            melting_point=self.melting_point_spin.value(),
            boiling_point=self.boiling_point_spin.value(),
            absorptivity=self.absorptivity_spin.value(),
            youngs_modulus=self.youngs_modulus_spin.value(),
            poissons_ratio=self.poissons_ratio_spin.value(),
            thermal_expansion=self.thermal_expansion_spin.value(),
            yield_strength=self.yield_strength_spin.value()
        )

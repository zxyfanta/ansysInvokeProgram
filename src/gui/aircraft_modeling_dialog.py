"""
GUI - 飞行器建模对话框

提供飞行器模型生成、导入和配置的图形界面。
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                                QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
                                QSpinBox, QDoubleSpinBox, QTextEdit, QGroupBox,
                                QGridLayout, QFileDialog, QMessageBox, QProgressBar,
                                QTableWidget, QTableWidgetItem, QCheckBox)
    from PyQt5.QtCore import Qt, pyqtSignal, QThread
    from PyQt5.QtGui import QFont, QPixmap
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

if GUI_AVAILABLE:
    from aircraft_modeling.aircraft_types import (AircraftType, AircraftParameters, 
                                                 AircraftDimensions, FlightParameters,
                                                 MaterialType, get_aircraft_template,
                                                 get_available_aircraft_types)
    from aircraft_modeling.aircraft_generator import AircraftGenerator
    from aircraft_modeling.model_manager import ModelManager

class AircraftModelingDialog(QDialog):
    """飞行器建模对话框"""
    
    # 信号
    model_generated = pyqtSignal(dict)  # 模型生成完成
    model_imported = pyqtSignal(dict)   # 模型导入完成
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not GUI_AVAILABLE:
            raise ImportError("PyQt5不可用")
        
        self.aircraft_generator = AircraftGenerator()
        self.model_manager = ModelManager()
        
        self.current_aircraft_params: Optional[AircraftParameters] = None
        self.generated_model: Optional[Dict[str, Any]] = None
        
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("飞行器建模")
        self.setFixedSize(800, 600)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 模型生成选项卡
        self.generation_tab = self.create_generation_tab()
        self.tab_widget.addTab(self.generation_tab, "模型生成")
        
        # 模型导入选项卡
        self.import_tab = self.create_import_tab()
        self.tab_widget.addTab(self.import_tab, "模型导入")
        
        # 模型管理选项卡
        self.management_tab = self.create_management_tab()
        self.tab_widget.addTab(self.management_tab, "模型管理")
        
        main_layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("生成模型")
        self.import_btn = QPushButton("导入模型")
        self.preview_btn = QPushButton("预览模型")
        self.export_btn = QPushButton("导出模型")
        self.close_btn = QPushButton("关闭")
        
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.preview_btn)
        button_layout.addWidget(self.export_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        
        # 状态栏
        self.status_label = QLabel("就绪")
        main_layout.addWidget(self.status_label)
        
        self.setLayout(main_layout)
    
    def create_generation_tab(self) -> QWidget:
        """创建模型生成选项卡"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 飞行器类型选择
        type_group = QGroupBox("飞行器类型")
        type_layout = QGridLayout()
        
        type_layout.addWidget(QLabel("类型:"), 0, 0)
        self.aircraft_type_combo = QComboBox()
        for aircraft_type in get_available_aircraft_types():
            self.aircraft_type_combo.addItem(aircraft_type.value, aircraft_type)
        type_layout.addWidget(self.aircraft_type_combo, 0, 1)
        
        type_layout.addWidget(QLabel("名称:"), 1, 0)
        self.aircraft_name_edit = QLineEdit("自定义飞行器")
        type_layout.addWidget(self.aircraft_name_edit, 1, 1)
        
        self.load_template_btn = QPushButton("加载模板")
        type_layout.addWidget(self.load_template_btn, 0, 2)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # 尺寸参数
        dimensions_group = QGroupBox("尺寸参数")
        dimensions_layout = QGridLayout()
        
        # 尺寸输入控件
        self.length_spin = QDoubleSpinBox()
        self.length_spin.setRange(0.1, 100.0)
        self.length_spin.setValue(15.0)
        self.length_spin.setSuffix(" m")
        dimensions_layout.addWidget(QLabel("机身长度:"), 0, 0)
        dimensions_layout.addWidget(self.length_spin, 0, 1)
        
        self.wingspan_spin = QDoubleSpinBox()
        self.wingspan_spin.setRange(0.1, 100.0)
        self.wingspan_spin.setValue(10.0)
        self.wingspan_spin.setSuffix(" m")
        dimensions_layout.addWidget(QLabel("翼展:"), 0, 2)
        dimensions_layout.addWidget(self.wingspan_spin, 0, 3)
        
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(0.1, 20.0)
        self.height_spin.setValue(4.5)
        self.height_spin.setSuffix(" m")
        dimensions_layout.addWidget(QLabel("机身高度:"), 1, 0)
        dimensions_layout.addWidget(self.height_spin, 1, 1)
        
        self.wing_chord_spin = QDoubleSpinBox()
        self.wing_chord_spin.setRange(0.1, 20.0)
        self.wing_chord_spin.setValue(3.0)
        self.wing_chord_spin.setSuffix(" m")
        dimensions_layout.addWidget(QLabel("翼弦长:"), 1, 2)
        dimensions_layout.addWidget(self.wing_chord_spin, 1, 3)
        
        self.wing_thickness_spin = QDoubleSpinBox()
        self.wing_thickness_spin.setRange(0.01, 2.0)
        self.wing_thickness_spin.setValue(0.3)
        self.wing_thickness_spin.setSuffix(" m")
        dimensions_layout.addWidget(QLabel("翼厚:"), 2, 0)
        dimensions_layout.addWidget(self.wing_thickness_spin, 2, 1)
        
        self.fuselage_diameter_spin = QDoubleSpinBox()
        self.fuselage_diameter_spin.setRange(0.1, 10.0)
        self.fuselage_diameter_spin.setValue(1.5)
        self.fuselage_diameter_spin.setSuffix(" m")
        dimensions_layout.addWidget(QLabel("机身直径:"), 2, 2)
        dimensions_layout.addWidget(self.fuselage_diameter_spin, 2, 3)
        
        dimensions_group.setLayout(dimensions_layout)
        layout.addWidget(dimensions_group)
        
        # 飞行参数
        flight_group = QGroupBox("飞行参数")
        flight_layout = QGridLayout()
        
        self.cruise_speed_spin = QDoubleSpinBox()
        self.cruise_speed_spin.setRange(10.0, 1000.0)
        self.cruise_speed_spin.setValue(250.0)
        self.cruise_speed_spin.setSuffix(" m/s")
        flight_layout.addWidget(QLabel("巡航速度:"), 0, 0)
        flight_layout.addWidget(self.cruise_speed_spin, 0, 1)
        
        self.max_speed_spin = QDoubleSpinBox()
        self.max_speed_spin.setRange(10.0, 2000.0)
        self.max_speed_spin.setValue(600.0)
        self.max_speed_spin.setSuffix(" m/s")
        flight_layout.addWidget(QLabel("最大速度:"), 0, 2)
        flight_layout.addWidget(self.max_speed_spin, 0, 3)
        
        self.service_ceiling_spin = QDoubleSpinBox()
        self.service_ceiling_spin.setRange(100.0, 30000.0)
        self.service_ceiling_spin.setValue(15000.0)
        self.service_ceiling_spin.setSuffix(" m")
        flight_layout.addWidget(QLabel("实用升限:"), 1, 0)
        flight_layout.addWidget(self.service_ceiling_spin, 1, 1)
        
        self.empty_weight_spin = QDoubleSpinBox()
        self.empty_weight_spin.setRange(10.0, 100000.0)
        self.empty_weight_spin.setValue(8000.0)
        self.empty_weight_spin.setSuffix(" kg")
        flight_layout.addWidget(QLabel("空重:"), 1, 2)
        flight_layout.addWidget(self.empty_weight_spin, 1, 3)
        
        flight_group.setLayout(flight_layout)
        layout.addWidget(flight_group)
        
        # 材料选择
        material_group = QGroupBox("材料配置")
        material_layout = QGridLayout()
        
        material_layout.addWidget(QLabel("主要材料:"), 0, 0)
        self.primary_material_combo = QComboBox()
        for material in MaterialType:
            self.primary_material_combo.addItem(material.value, material)
        material_layout.addWidget(self.primary_material_combo, 0, 1)
        
        material_group.setLayout(material_layout)
        layout.addWidget(material_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_import_tab(self) -> QWidget:
        """创建模型导入选项卡"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 文件选择
        file_group = QGroupBox("文件选择")
        file_layout = QGridLayout()
        
        file_layout.addWidget(QLabel("模型文件:"), 0, 0)
        self.file_path_edit = QLineEdit()
        file_layout.addWidget(self.file_path_edit, 0, 1)
        
        self.browse_btn = QPushButton("浏览...")
        file_layout.addWidget(self.browse_btn, 0, 2)
        
        file_layout.addWidget(QLabel("文件格式:"), 1, 0)
        self.file_format_combo = QComboBox()
        self.file_format_combo.addItems(["自动检测", "STEP", "IGES", "STL", "OBJ", "JSON"])
        file_layout.addWidget(self.file_format_combo, 1, 1)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 导入选项
        options_group = QGroupBox("导入选项")
        options_layout = QGridLayout()
        
        self.validate_geometry_check = QCheckBox("验证几何")
        self.validate_geometry_check.setChecked(True)
        options_layout.addWidget(self.validate_geometry_check, 0, 0)
        
        self.auto_repair_check = QCheckBox("自动修复")
        options_layout.addWidget(self.auto_repair_check, 0, 1)
        
        self.generate_mesh_check = QCheckBox("生成网格")
        options_layout.addWidget(self.generate_mesh_check, 1, 0)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 模型信息显示
        info_group = QGroupBox("模型信息")
        info_layout = QVBoxLayout()
        
        self.model_info_text = QTextEdit()
        self.model_info_text.setReadOnly(True)
        self.model_info_text.setMaximumHeight(200)
        info_layout.addWidget(self.model_info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        layout.addStretch()
        tab.setLayout(layout)
        return tab
    
    def create_management_tab(self) -> QWidget:
        """创建模型管理选项卡"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 模型列表
        self.model_table = QTableWidget()
        self.model_table.setColumnCount(5)
        self.model_table.setHorizontalHeaderLabels(["名称", "类型", "来源", "状态", "操作"])
        layout.addWidget(self.model_table)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新")
        self.delete_btn = QPushButton("删除")
        self.duplicate_btn = QPushButton("复制")
        self.export_model_btn = QPushButton("导出")
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.duplicate_btn)
        button_layout.addWidget(self.export_model_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        tab.setLayout(layout)
        return tab
    
    def setup_connections(self):
        """设置信号连接"""
        # 按钮连接
        self.generate_btn.clicked.connect(self.generate_model)
        self.import_btn.clicked.connect(self.import_model)
        self.preview_btn.clicked.connect(self.preview_model)
        self.export_btn.clicked.connect(self.export_model)
        self.close_btn.clicked.connect(self.close)
        
        # 生成选项卡连接
        self.load_template_btn.clicked.connect(self.load_template)
        self.aircraft_type_combo.currentTextChanged.connect(self.on_aircraft_type_changed)
        
        # 导入选项卡连接
        self.browse_btn.clicked.connect(self.browse_file)
        
        # 管理选项卡连接
        self.refresh_btn.clicked.connect(self.refresh_model_list)
        self.delete_btn.clicked.connect(self.delete_model)
    
    def load_template(self):
        """加载飞行器模板"""
        try:
            aircraft_type = self.aircraft_type_combo.currentData()
            template = get_aircraft_template(aircraft_type)
            
            if template:
                self.load_aircraft_parameters(template)
                self.status_label.setText(f"已加载{aircraft_type.value}模板")
            else:
                QMessageBox.warning(self, "警告", "未找到对应模板")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载模板失败: {e}")
    
    def load_aircraft_parameters(self, params: AircraftParameters):
        """加载飞行器参数到界面"""
        # 尺寸参数
        dims = params.dimensions
        self.length_spin.setValue(dims.length)
        self.wingspan_spin.setValue(dims.wingspan)
        self.height_spin.setValue(dims.height)
        self.wing_chord_spin.setValue(dims.wing_chord)
        self.wing_thickness_spin.setValue(dims.wing_thickness)
        self.fuselage_diameter_spin.setValue(dims.fuselage_diameter)
        
        # 飞行参数
        flight = params.flight_params
        self.cruise_speed_spin.setValue(flight.cruise_speed)
        self.max_speed_spin.setValue(flight.max_speed)
        self.service_ceiling_spin.setValue(flight.service_ceiling)
        self.empty_weight_spin.setValue(flight.empty_weight)
        
        # 材料
        material_index = self.primary_material_combo.findData(params.primary_material)
        if material_index >= 0:
            self.primary_material_combo.setCurrentIndex(material_index)
        
        # 名称
        self.aircraft_name_edit.setText(params.name)
    
    def get_aircraft_parameters(self) -> AircraftParameters:
        """从界面获取飞行器参数"""
        dimensions = AircraftDimensions(
            length=self.length_spin.value(),
            wingspan=self.wingspan_spin.value(),
            height=self.height_spin.value(),
            wing_chord=self.wing_chord_spin.value(),
            wing_thickness=self.wing_thickness_spin.value(),
            fuselage_diameter=self.fuselage_diameter_spin.value()
        )
        
        flight_params = FlightParameters(
            cruise_speed=self.cruise_speed_spin.value(),
            max_speed=self.max_speed_spin.value(),
            service_ceiling=self.service_ceiling_spin.value(),
            max_load_factor=9.0,  # 默认值
            empty_weight=self.empty_weight_spin.value(),
            max_takeoff_weight=self.empty_weight_spin.value() * 1.5  # 估算
        )
        
        # 获取飞行器类型，如果为None则使用默认值
        aircraft_type = self.aircraft_type_combo.currentData()
        if aircraft_type is None:
            aircraft_type = AircraftType.FIXED_WING_FIGHTER

        # 获取材料类型，如果为None则使用默认值
        primary_material = self.primary_material_combo.currentData()
        if primary_material is None:
            primary_material = MaterialType.ALUMINUM_ALLOY

        # 获取名称，如果为空则使用默认值
        aircraft_name = self.aircraft_name_edit.text().strip()
        if not aircraft_name:
            aircraft_name = f"自定义{aircraft_type.value}"

        aircraft_params = AircraftParameters(
            aircraft_type=aircraft_type,
            name=aircraft_name,
            dimensions=dimensions,
            flight_params=flight_params,
            primary_material=primary_material,
            material_distribution={"body": primary_material},
            description=f"用户定义的{self.aircraft_type_combo.currentText()}"
        )
        
        return aircraft_params
    
    def generate_model(self):
        """生成飞行器模型"""
        try:
            self.status_label.setText("正在生成模型...")
            
            # 获取参数
            aircraft_params = self.get_aircraft_parameters()
            
            # 让用户选择保存格式
            from PyQt5.QtWidgets import QFileDialog

            # 默认文件名
            default_name = aircraft_params.name.replace(" ", "_")

            # 文件对话框
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "保存飞行器模型",
                f"models/{default_name}",
                "STL文件 (*.stl);;OBJ文件 (*.obj);;JSON文件 (*.json);;所有文件 (*.*)"
            )

            if not file_path:
                self.status_label.setText("用户取消保存")
                return

            # 生成模型
            model_data = self.aircraft_generator.generate_aircraft_model(
                aircraft_params,
                file_path
            )
            
            if model_data:
                self.generated_model = model_data
                self.current_aircraft_params = aircraft_params
                self.status_label.setText("模型生成完成")
                
                # 发射信号
                self.model_generated.emit(model_data)
                
                QMessageBox.information(self, "成功", "飞行器模型生成完成！")
            else:
                QMessageBox.critical(self, "错误", "模型生成失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"模型生成失败: {e}")
            self.status_label.setText("模型生成失败")
    
    def import_model(self):
        """导入飞行器模型"""
        try:
            file_path = self.file_path_edit.text()
            if not file_path:
                QMessageBox.warning(self, "警告", "请选择模型文件")
                return
            
            self.status_label.setText("正在导入模型...")
            
            # 导入模型
            model_name = Path(file_path).stem
            model_data = self.model_manager.import_cad_model(file_path, model_name)
            
            if model_data:
                self.generated_model = model_data
                self.update_model_info(model_data)
                self.status_label.setText("模型导入完成")
                
                # 发射信号
                self.model_imported.emit(model_data)
                
                QMessageBox.information(self, "成功", "模型导入完成！")
            else:
                QMessageBox.critical(self, "错误", "模型导入失败")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"模型导入失败: {e}")
            self.status_label.setText("模型导入失败")
    
    def preview_model(self):
        """预览模型"""
        if not self.generated_model:
            QMessageBox.warning(self, "警告", "没有可预览的模型")
            return
        
        # 这里可以实现3D预览功能
        QMessageBox.information(self, "预览", "3D预览功能正在开发中...")
    
    def export_model(self):
        """导出模型"""
        if not self.generated_model:
            QMessageBox.warning(self, "警告", "没有可导出的模型")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出模型", "", 
            "JSON文件 (*.json);;STEP文件 (*.step);;STL文件 (*.stl)"
        )
        
        if file_path:
            try:
                # 这里实现导出逻辑
                QMessageBox.information(self, "成功", f"模型已导出到: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出失败: {e}")
    
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "",
            "所有支持格式 (*.step *.stp *.iges *.igs *.stl *.obj *.json);;STEP文件 (*.step *.stp);;IGES文件 (*.iges *.igs);;STL文件 (*.stl);;OBJ文件 (*.obj);;JSON文件 (*.json)"
        )
        
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def update_model_info(self, model_data: Dict[str, Any]):
        """更新模型信息显示"""
        info_text = "模型信息:\n"
        info_text += f"类型: {model_data.get('type', 'Unknown')}\n"
        
        if 'metadata' in model_data:
            metadata = model_data['metadata']
            info_text += f"名称: {metadata.get('name', 'Unknown')}\n"
            info_text += f"导入时间: {metadata.get('import_time', 'Unknown')}\n"
        
        if 'validation' in model_data:
            validation = model_data['validation']
            info_text += f"验证状态: {'通过' if validation.get('is_valid') else '失败'}\n"
        
        self.model_info_text.setText(info_text)
    
    def refresh_model_list(self):
        """刷新模型列表"""
        # 实现模型列表刷新
        pass
    
    def delete_model(self):
        """删除模型"""
        # 实现模型删除
        pass
    
    def on_aircraft_type_changed(self):
        """飞行器类型改变时的处理"""
        aircraft_type = self.aircraft_type_combo.currentData()
        if aircraft_type:
            self.aircraft_name_edit.setText(f"自定义{aircraft_type.value}")
    
    def get_generated_model(self) -> Optional[Dict[str, Any]]:
        """获取生成的模型"""
        return self.generated_model
    
    def get_current_aircraft_parameters(self) -> Optional[AircraftParameters]:
        """获取当前飞行器参数"""
        return self.current_aircraft_params

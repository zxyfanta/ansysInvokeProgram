"""
GUI - 仿真控制面板

仿真控制界面组件。
"""

try:
    from PyQt5.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QPushButton, QLabel, QProgressBar, QGroupBox,
        QCheckBox, QSpinBox, QDoubleSpinBox, QComboBox
    )
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtGui import QFont
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

class SimulationControlPanel(QWidget):
    """仿真控制面板"""
    
    # 信号定义
    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5不可用，无法创建控制面板")
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        
        # 仿真控制按钮组
        control_group = QGroupBox("仿真控制")
        control_layout = QGridLayout(control_group)
        
        self.start_btn = QPushButton("开始仿真")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.clicked.connect(self.start_requested.emit)
        control_layout.addWidget(self.start_btn, 0, 0)
        
        self.pause_btn = QPushButton("暂停仿真")
        self.pause_btn.setMinimumHeight(40)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause_requested.emit)
        control_layout.addWidget(self.pause_btn, 0, 1)
        
        self.stop_btn = QPushButton("停止仿真")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_requested.emit)
        control_layout.addWidget(self.stop_btn, 1, 0, 1, 2)
        
        layout.addWidget(control_group)
        
        # 仿真选项组
        options_group = QGroupBox("仿真选项")
        options_layout = QVBoxLayout(options_group)
        
        self.enable_laser_damage = QCheckBox("激光毁伤仿真")
        self.enable_laser_damage.setChecked(True)
        options_layout.addWidget(self.enable_laser_damage)
        
        self.enable_post_damage = QCheckBox("毁伤后效分析")
        self.enable_post_damage.setChecked(True)
        options_layout.addWidget(self.enable_post_damage)
        
        self.enable_data_analysis = QCheckBox("数据分析")
        self.enable_data_analysis.setChecked(True)
        options_layout.addWidget(self.enable_data_analysis)
        
        layout.addWidget(options_group)
        
        # 计算设置组
        compute_group = QGroupBox("计算设置")
        compute_layout = QVBoxLayout(compute_group)
        
        # 并行核心数
        cores_layout = QHBoxLayout()
        cores_layout.addWidget(QLabel("并行核心数:"))
        self.cores_spin = QSpinBox()
        self.cores_spin.setRange(1, 16)
        self.cores_spin.setValue(4)
        cores_layout.addWidget(self.cores_spin)
        compute_layout.addLayout(cores_layout)
        
        # 求解器类型
        solver_layout = QHBoxLayout()
        solver_layout.addWidget(QLabel("求解器:"))
        self.solver_combo = QComboBox()
        self.solver_combo.addItems(["自动选择", "直接求解器", "迭代求解器"])
        solver_layout.addWidget(self.solver_combo)
        compute_layout.addLayout(solver_layout)
        
        layout.addWidget(compute_group)
    
    def set_simulation_running(self, running: bool):
        """设置仿真运行状态"""
        self.start_btn.setEnabled(not running)
        self.pause_btn.setEnabled(running)
        self.stop_btn.setEnabled(running)
    
    def get_simulation_options(self) -> dict:
        """获取仿真选项"""
        return {
            'enable_laser_damage': self.enable_laser_damage.isChecked(),
            'enable_post_damage': self.enable_post_damage.isChecked(),
            'enable_data_analysis': self.enable_data_analysis.isChecked(),
            'parallel_cores': self.cores_spin.value(),
            'solver_type': self.solver_combo.currentText()
        }

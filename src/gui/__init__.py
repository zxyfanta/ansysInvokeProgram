"""
激光毁伤效能分析软件 - GUI界面模块

实现专业的军用软件图形用户界面。
"""

# GUI可用性检查
try:
    from PyQt5.QtWidgets import QApplication
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("PyQt5不可用，GUI功能将受限")

if GUI_AVAILABLE:
    from .main_window import MainWindow
    from .laser_config_dialog import LaserConfigDialog
    from .material_config_dialog import MaterialConfigDialog
    from .simulation_control_panel import SimulationControlPanel
    from .results_viewer import ResultsViewer
    from .chart_viewer import ChartViewer
    
    # 保持向后兼容
    AircraftModelingGUI = MainWindow
    
    __all__ = [
        'MainWindow',
        'LaserConfigDialog',
        'MaterialConfigDialog', 
        'SimulationControlPanel',
        'ResultsViewer',
        'ChartViewer',
        'AircraftModelingGUI',  # 向后兼容
        'GUI_AVAILABLE'
    ]
else:
    __all__ = ['GUI_AVAILABLE']

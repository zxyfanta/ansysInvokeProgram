"""
GUI - 主窗口

激光毁伤效能分析软件的主界面。
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
        QMenuBar, QStatusBar, QToolBar, QAction, QSplitter,
        QTabWidget, QTextEdit, QProgressBar, QLabel, QPushButton,
        QMessageBox, QFileDialog, QGroupBox, QFrame
    )
    from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
    from PyQt5.QtGui import QIcon, QFont, QPixmap, QPalette, QColor
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False

if PYQT5_AVAILABLE:
    from .laser_config_dialog import LaserConfigDialog
    from .material_config_dialog import MaterialConfigDialog
    from .simulation_control_panel import SimulationControlPanel
    from .results_viewer import ResultsViewer
    from .chart_viewer import ChartViewer

# 导入核心模块
from core.data_models import LaserParameters, MaterialData, GeometryData, LaserType
from laser_damage import LaserDamageSimulator
from post_damage import PostDamageAnalyzer
from data_analysis import DataAnalyzer

class SimulationWorker(QThread):
    """仿真工作线程"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    simulation_completed = pyqtSignal(dict)
    simulation_failed = pyqtSignal(str)
    
    def __init__(self, simulation_params):
        super().__init__()
        self.simulation_params = simulation_params
        self.is_running = False
    
    def run(self):
        """运行仿真"""
        try:
            self.is_running = True
            self.status_updated.emit("初始化仿真...")
            self.progress_updated.emit(10)
            
            # 创建仿真器
            laser_simulator = LaserDamageSimulator()
            post_damage_analyzer = PostDamageAnalyzer()
            data_analyzer = DataAnalyzer()
            
            # 激光毁伤仿真
            self.status_updated.emit("执行激光毁伤仿真...")
            self.progress_updated.emit(30)
            
            laser_success = laser_simulator.run_simulation()
            if not laser_success:
                raise RuntimeError("激光毁伤仿真失败")
            
            # 毁伤后效分析
            self.status_updated.emit("执行毁伤后效分析...")
            self.progress_updated.emit(60)
            
            post_damage_success = post_damage_analyzer.run_simulation()
            if not post_damage_success:
                self.status_updated.emit("毁伤后效分析失败，继续数据分析...")
            
            # 数据分析
            self.status_updated.emit("执行数据分析...")
            self.progress_updated.emit(80)
            
            # 收集结果
            results = {
                'laser_damage_results': laser_simulator.get_results(),
                'post_damage_results': post_damage_analyzer.get_results() if post_damage_success else {},
                'simulation_params': self.simulation_params
            }
            
            # 数据分析
            analysis_results = data_analyzer.analyze_simulation_results(results)
            results['analysis_results'] = analysis_results
            
            self.progress_updated.emit(100)
            self.status_updated.emit("仿真完成")
            self.simulation_completed.emit(results)
            
        except Exception as e:
            self.simulation_failed.emit(str(e))
        finally:
            self.is_running = False
    
    def stop(self):
        """停止仿真"""
        self.is_running = False
        self.terminate()

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        if not PYQT5_AVAILABLE:
            raise ImportError("PyQt5不可用，无法创建GUI")
        
        self.logger = logging.getLogger(__name__)
        
        # 仿真参数
        self.laser_params: Optional[LaserParameters] = None
        self.material_data: Optional[MaterialData] = None
        self.geometry_data: Optional[GeometryData] = None
        
        # 仿真结果
        self.simulation_results: Optional[Dict] = None
        
        # 工作线程
        self.simulation_worker: Optional[SimulationWorker] = None
        
        # 初始化界面
        self.init_ui()
        self.setup_connections()
        self.setup_style()
        
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # 每秒更新一次
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("激光毁伤效能分析软件 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)
        
        # 设置窗口图标
        self.setWindowIcon(self.create_app_icon())
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # 左侧控制面板
        self.create_control_panel(main_splitter)
        
        # 右侧结果显示区域
        self.create_results_area(main_splitter)
        
        # 设置分割器比例
        main_splitter.setSizes([400, 1000])
        
        # 创建菜单栏
        self.create_menu_bar()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        control_frame = QFrame()
        control_frame.setFrameStyle(QFrame.StyledPanel)
        control_frame.setMaximumWidth(450)
        
        layout = QVBoxLayout(control_frame)
        
        # 标题
        title_label = QLabel("仿真控制面板")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # 参数配置组
        config_group = QGroupBox("参数配置")
        config_layout = QVBoxLayout(config_group)
        
        # 激光参数配置按钮
        self.laser_config_btn = QPushButton("激光参数配置")
        self.laser_config_btn.setMinimumHeight(40)
        config_layout.addWidget(self.laser_config_btn)
        
        # 材料参数配置按钮
        self.material_config_btn = QPushButton("材料参数配置")
        self.material_config_btn.setMinimumHeight(40)
        config_layout.addWidget(self.material_config_btn)
        
        # 几何参数配置按钮
        self.geometry_config_btn = QPushButton("几何参数配置")
        self.geometry_config_btn.setMinimumHeight(40)
        config_layout.addWidget(self.geometry_config_btn)
        
        layout.addWidget(config_group)
        
        # 仿真控制组
        simulation_group = QGroupBox("仿真控制")
        simulation_layout = QVBoxLayout(simulation_group)
        
        # 仿真控制面板
        self.simulation_control = SimulationControlPanel()
        simulation_layout.addWidget(self.simulation_control)
        
        layout.addWidget(simulation_group)
        
        # 进度显示
        progress_group = QGroupBox("仿真进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(25)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        parent.addWidget(control_frame)
    
    def create_results_area(self, parent):
        """创建结果显示区域"""
        results_widget = QTabWidget()
        
        # 结果查看器
        self.results_viewer = ResultsViewer()
        results_widget.addTab(self.results_viewer, "仿真结果")
        
        # 图表查看器
        self.chart_viewer = ChartViewer()
        results_widget.addTab(self.chart_viewer, "图表分析")
        
        # 日志查看器
        self.log_viewer = QTextEdit()
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setFont(QFont("Consolas", 10))
        results_widget.addTab(self.log_viewer, "运行日志")
        
        parent.addWidget(results_widget)
    
    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction('打开项目(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        save_action = QAction('保存项目(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('导出结果(&E)', self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 仿真菜单
        simulation_menu = menubar.addMenu('仿真(&S)')
        
        start_action = QAction('开始仿真(&S)', self)
        start_action.setShortcut('F5')
        start_action.triggered.connect(self.start_simulation)
        simulation_menu.addAction(start_action)
        
        stop_action = QAction('停止仿真(&T)', self)
        stop_action.setShortcut('F6')
        stop_action.triggered.connect(self.stop_simulation)
        simulation_menu.addAction(stop_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')
        
        settings_action = QAction('设置(&S)', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)
        
        # 新建项目
        new_action = QAction("新建", self)
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # 打开项目
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # 保存项目
        save_action = QAction("保存", self)
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 开始仿真
        self.start_action = QAction("开始仿真", self)
        self.start_action.triggered.connect(self.start_simulation)
        toolbar.addAction(self.start_action)
        
        # 停止仿真
        self.stop_action = QAction("停止仿真", self)
        self.stop_action.triggered.connect(self.stop_simulation)
        self.stop_action.setEnabled(False)
        toolbar.addAction(self.stop_action)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 状态标签
        self.status_bar.showMessage("就绪")
        
        # 进度条
        self.status_progress = QProgressBar()
        self.status_progress.setMaximumWidth(200)
        self.status_progress.setVisible(False)
        self.status_bar.addPermanentWidget(self.status_progress)
    
    def setup_connections(self):
        """设置信号连接"""
        # 配置按钮连接
        self.laser_config_btn.clicked.connect(self.configure_laser_parameters)
        self.material_config_btn.clicked.connect(self.configure_material_parameters)
        self.geometry_config_btn.clicked.connect(self.configure_geometry_parameters)
        
        # 仿真控制连接
        self.simulation_control.start_requested.connect(self.start_simulation)
        self.simulation_control.stop_requested.connect(self.stop_simulation)
        self.simulation_control.pause_requested.connect(self.pause_simulation)
    
    def setup_style(self):
        """设置界面样式"""
        # 设置应用程序样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
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
            
            QPushButton {
                background-color: #3498db;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
            
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
    
    def create_app_icon(self) -> QIcon:
        """创建应用程序图标"""
        # 创建简单的图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(52, 152, 219))  # 蓝色背景
        return QIcon(pixmap)

    def configure_laser_parameters(self):
        """配置激光参数"""
        try:
            dialog = LaserConfigDialog(self.laser_params, self)
            if dialog.exec_() == dialog.Accepted:
                self.laser_params = dialog.get_laser_parameters()
                self.log_message("激光参数配置完成")
                self.update_config_status()
        except Exception as e:
            self.show_error(f"激光参数配置失败: {e}")

    def configure_material_parameters(self):
        """配置材料参数"""
        try:
            dialog = MaterialConfigDialog(self.material_data, self)
            if dialog.exec_() == dialog.Accepted:
                self.material_data = dialog.get_material_data()
                self.log_message("材料参数配置完成")
                self.update_config_status()
        except Exception as e:
            self.show_error(f"材料参数配置失败: {e}")

    def configure_geometry_parameters(self):
        """配置几何参数"""
        try:
            # 简化的几何参数配置
            from PyQt5.QtWidgets import QDialog, QFormLayout, QDoubleSpinBox, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("几何参数配置")
            dialog.setModal(True)

            layout = QFormLayout(dialog)

            # 尺寸输入
            length_spin = QDoubleSpinBox()
            length_spin.setRange(0.001, 10.0)
            length_spin.setValue(0.1)
            length_spin.setSuffix(" m")
            layout.addRow("长度:", length_spin)

            width_spin = QDoubleSpinBox()
            width_spin.setRange(0.001, 10.0)
            width_spin.setValue(0.1)
            width_spin.setSuffix(" m")
            layout.addRow("宽度:", width_spin)

            height_spin = QDoubleSpinBox()
            height_spin.setRange(0.001, 1.0)
            height_spin.setValue(0.02)
            height_spin.setSuffix(" m")
            layout.addRow("厚度:", height_spin)

            # 按钮
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec_() == QDialog.Accepted:
                self.geometry_data = GeometryData(
                    model_file="target_model.step",
                    dimensions=(length_spin.value(), width_spin.value(), height_spin.value()),
                    volume=length_spin.value() * width_spin.value() * height_spin.value(),
                    surface_area=2 * (length_spin.value() * width_spin.value() +
                                    length_spin.value() * height_spin.value() +
                                    width_spin.value() * height_spin.value()),
                    mesh_size=min(length_spin.value(), width_spin.value(), height_spin.value()) / 50
                )
                self.log_message("几何参数配置完成")
                self.update_config_status()

        except Exception as e:
            self.show_error(f"几何参数配置失败: {e}")

    def update_config_status(self):
        """更新配置状态"""
        status_parts = []

        if self.laser_params:
            status_parts.append("激光✓")
        else:
            status_parts.append("激光✗")

        if self.material_data:
            status_parts.append("材料✓")
        else:
            status_parts.append("材料✗")

        if self.geometry_data:
            status_parts.append("几何✓")
        else:
            status_parts.append("几何✗")

        status_text = " | ".join(status_parts)
        self.status_bar.showMessage(f"配置状态: {status_text}")

        # 检查是否可以开始仿真
        can_simulate = all([self.laser_params, self.material_data, self.geometry_data])
        self.start_action.setEnabled(can_simulate and not self.is_simulation_running())

    def start_simulation(self):
        """开始仿真"""
        try:
            # 检查参数
            if not all([self.laser_params, self.material_data, self.geometry_data]):
                self.show_warning("请先配置所有必要参数")
                return

            if self.is_simulation_running():
                self.show_warning("仿真正在运行中")
                return

            # 准备仿真参数
            simulation_params = {
                'laser_params': self.laser_params,
                'material_data': self.material_data,
                'geometry_data': self.geometry_data
            }

            # 创建并启动工作线程
            self.simulation_worker = SimulationWorker(simulation_params)
            self.simulation_worker.progress_updated.connect(self.update_progress)
            self.simulation_worker.status_updated.connect(self.update_status_message)
            self.simulation_worker.simulation_completed.connect(self.on_simulation_completed)
            self.simulation_worker.simulation_failed.connect(self.on_simulation_failed)

            self.simulation_worker.start()

            # 更新界面状态
            self.start_action.setEnabled(False)
            self.stop_action.setEnabled(True)
            self.progress_bar.setVisible(True)
            self.status_progress.setVisible(True)

            self.log_message("仿真开始...")

        except Exception as e:
            self.show_error(f"仿真启动失败: {e}")

    def stop_simulation(self):
        """停止仿真"""
        try:
            if self.simulation_worker and self.simulation_worker.isRunning():
                self.simulation_worker.stop()
                self.simulation_worker.wait(3000)  # 等待3秒

                if self.simulation_worker.isRunning():
                    self.simulation_worker.terminate()
                    self.simulation_worker.wait()

                self.log_message("仿真已停止")

            # 重置界面状态
            self.reset_simulation_ui()

        except Exception as e:
            self.show_error(f"停止仿真失败: {e}")

    def pause_simulation(self):
        """暂停仿真"""
        # 简化实现，实际可以添加暂停逻辑
        self.log_message("暂停功能暂未实现")

    def update_progress(self, value: int):
        """更新进度"""
        self.progress_bar.setValue(value)
        self.status_progress.setValue(value)

    def update_status_message(self, message: str):
        """更新状态消息"""
        self.status_label.setText(message)
        self.status_bar.showMessage(message)
        self.log_message(f"状态: {message}")

    def on_simulation_completed(self, results: Dict):
        """仿真完成处理"""
        try:
            self.simulation_results = results

            # 显示结果
            self.results_viewer.display_results(results)

            # 显示图表
            if 'analysis_results' in results:
                analysis_results = results['analysis_results']
                if 'chart_files' in analysis_results:
                    self.chart_viewer.load_charts(analysis_results['chart_files'])

            # 重置界面
            self.reset_simulation_ui()

            self.log_message("仿真完成！")
            self.show_info("仿真已成功完成，请查看结果。")

        except Exception as e:
            self.show_error(f"结果处理失败: {e}")

    def on_simulation_failed(self, error_message: str):
        """仿真失败处理"""
        self.reset_simulation_ui()
        self.log_message(f"仿真失败: {error_message}")
        self.show_error(f"仿真失败: {error_message}")

    def reset_simulation_ui(self):
        """重置仿真界面状态"""
        self.start_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
        self.status_progress.setVisible(False)
        self.status_progress.setValue(0)
        self.status_label.setText("就绪")
        self.update_config_status()

    def is_simulation_running(self) -> bool:
        """检查仿真是否正在运行"""
        return self.simulation_worker is not None and self.simulation_worker.isRunning()

    def log_message(self, message: str):
        """记录日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_viewer.append(formatted_message)
        self.logger.info(message)

    def update_status(self):
        """定时状态更新"""
        # 这里可以添加定期状态检查逻辑
        pass

    def new_project(self):
        """新建项目"""
        try:
            # 检查是否有未保存的更改
            if self.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, '新建项目',
                    '当前项目有未保存的更改，是否继续？',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            # 重置所有参数
            self.laser_params = None
            self.material_data = None
            self.geometry_data = None
            self.simulation_results = None

            # 清空界面
            self.results_viewer.clear_results()
            self.chart_viewer.clear_charts()
            self.log_viewer.clear()

            # 重置状态
            self.reset_simulation_ui()

            self.log_message("新建项目")

        except Exception as e:
            self.show_error(f"新建项目失败: {e}")

    def open_project(self):
        """打开项目"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, '打开项目', '',
                'JSON文件 (*.json);;所有文件 (*)'
            )

            if file_path:
                import json
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)

                # 加载项目数据
                self.load_project_data(project_data)

                self.log_message(f"项目已打开: {file_path}")

        except Exception as e:
            self.show_error(f"打开项目失败: {e}")

    def save_project(self):
        """保存项目"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, '保存项目', '',
                'JSON文件 (*.json);;所有文件 (*)'
            )

            if file_path:
                project_data = self.get_project_data()

                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False, default=str)

                self.log_message(f"项目已保存: {file_path}")

        except Exception as e:
            self.show_error(f"保存项目失败: {e}")

    def export_results(self):
        """导出结果"""
        try:
            if not self.simulation_results:
                self.show_warning("没有可导出的结果")
                return

            dir_path = QFileDialog.getExistingDirectory(self, '选择导出目录')

            if dir_path:
                # 导出结果数据
                results_file = os.path.join(dir_path, "simulation_results.json")
                import json
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(self.simulation_results, f, indent=2, ensure_ascii=False, default=str)

                # 如果有分析结果，也导出
                if 'analysis_results' in self.simulation_results:
                    analysis_results = self.simulation_results['analysis_results']

                    # 导出图表
                    if 'chart_files' in analysis_results:
                        import shutil
                        charts_dir = os.path.join(dir_path, "charts")
                        os.makedirs(charts_dir, exist_ok=True)

                        for chart_file in analysis_results['chart_files']:
                            if os.path.exists(chart_file):
                                shutil.copy2(chart_file, charts_dir)

                    # 导出报告
                    if 'report_files' in analysis_results:
                        import shutil
                        reports_dir = os.path.join(dir_path, "reports")
                        os.makedirs(reports_dir, exist_ok=True)

                        for report_file in analysis_results['report_files']:
                            if os.path.exists(report_file):
                                shutil.copy2(report_file, reports_dir)

                self.log_message(f"结果已导出到: {dir_path}")
                self.show_info(f"结果已成功导出到:\n{dir_path}")

        except Exception as e:
            self.show_error(f"导出结果失败: {e}")

    def show_settings(self):
        """显示设置对话框"""
        self.show_info("设置功能正在开发中...")

    def show_about(self):
        """显示关于对话框"""
        about_text = """
        <h2>激光毁伤效能分析软件</h2>
        <p><b>版本:</b> 1.0.0</p>
        <p><b>基于:</b> ANSYS 2021 R1 + PyANSYS</p>
        <p><b>功能:</b></p>
        <ul>
        <li>激光毁伤仿真</li>
        <li>毁伤后效分析</li>
        <li>数据分析与报告生成</li>
        <li>激光毁伤效果评估</li>
        </ul>
        <p><b>开发:</b> 军用软件开发部门</p>
        """

        QMessageBox.about(self, "关于", about_text)

    def has_unsaved_changes(self) -> bool:
        """检查是否有未保存的更改"""
        # 简化实现，实际可以添加更复杂的检查逻辑
        return any([self.laser_params, self.material_data, self.geometry_data])

    def get_project_data(self) -> Dict:
        """获取项目数据"""
        return {
            'laser_params': self.laser_params.__dict__ if self.laser_params else None,
            'material_data': self.material_data.__dict__ if self.material_data else None,
            'geometry_data': self.geometry_data.__dict__ if self.geometry_data else None,
            'simulation_results': self.simulation_results
        }

    def load_project_data(self, project_data: Dict):
        """加载项目数据"""
        try:
            # 加载激光参数
            if project_data.get('laser_params'):
                laser_data = project_data['laser_params']
                self.laser_params = LaserParameters(
                    power=laser_data.get('power', 1000.0),
                    wavelength=laser_data.get('wavelength', 1064.0),
                    beam_diameter=laser_data.get('beam_diameter', 0.01),
                    laser_type=LaserType(laser_data.get('laser_type', 'continuous'))
                )

            # 加载材料数据
            if project_data.get('material_data'):
                material_data = project_data['material_data']
                self.material_data = MaterialData(
                    name=material_data.get('name', ''),
                    density=material_data.get('density', 2780.0),
                    thermal_conductivity=material_data.get('thermal_conductivity', 121.0),
                    specific_heat=material_data.get('specific_heat', 875.0),
                    melting_point=material_data.get('melting_point', 916.0),
                    boiling_point=material_data.get('boiling_point', 2740.0),
                    absorptivity=material_data.get('absorptivity', 0.15),
                    youngs_modulus=material_data.get('youngs_modulus', 73.1e9),
                    poissons_ratio=material_data.get('poissons_ratio', 0.33),
                    thermal_expansion=material_data.get('thermal_expansion', 22.3e-6),
                    yield_strength=material_data.get('yield_strength', 324e6)
                )

            # 加载几何数据
            if project_data.get('geometry_data'):
                geometry_data = project_data['geometry_data']
                self.geometry_data = GeometryData(
                    model_file=geometry_data.get('model_file', ''),
                    dimensions=tuple(geometry_data.get('dimensions', [0.1, 0.1, 0.02])),
                    volume=geometry_data.get('volume', 0.0002),
                    surface_area=geometry_data.get('surface_area', 0.024),
                    mesh_size=geometry_data.get('mesh_size', 0.002)
                )

            # 加载仿真结果
            if project_data.get('simulation_results'):
                self.simulation_results = project_data['simulation_results']
                self.results_viewer.display_results(self.simulation_results)

            # 更新状态
            self.update_config_status()

        except Exception as e:
            raise Exception(f"项目数据加载失败: {e}")

    def show_info(self, message: str):
        """显示信息对话框"""
        QMessageBox.information(self, "信息", message)

    def show_warning(self, message: str):
        """显示警告对话框"""
        QMessageBox.warning(self, "警告", message)

    def show_error(self, message: str):
        """显示错误对话框"""
        QMessageBox.critical(self, "错误", message)

    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 检查是否有正在运行的仿真
            if self.is_simulation_running():
                reply = QMessageBox.question(
                    self, '退出确认',
                    '仿真正在运行中，是否强制退出？',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    event.ignore()
                    return
                else:
                    self.stop_simulation()

            # 检查未保存的更改
            if self.has_unsaved_changes():
                reply = QMessageBox.question(
                    self, '退出确认',
                    '有未保存的更改，是否退出？',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    event.ignore()
                    return

            # 停止定时器
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()

            event.accept()

        except Exception as e:
            self.logger.error(f"窗口关闭处理失败: {e}")
            event.accept()

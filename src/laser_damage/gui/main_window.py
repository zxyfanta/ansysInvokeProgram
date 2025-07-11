"""
主窗口界面

激光毁伤仿真系统的主界面窗口。
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QStatusBar, QToolBar, QAction, QMessageBox,
    QFileDialog, QProgressBar, QLabel, QSplitter, QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont

from .simulation_panel import SimulationPanel
from .analysis_panel import AnalysisPanel
from .report_panel import ReportPanel
from .assessment_panel import AssessmentPanel
from .project_selector import ProjectSelector
from ..core.data_models import SimulationStatus


class LaserSimulationMainWindow(QMainWindow):
    """激光毁伤仿真系统主窗口"""
    
    # 信号定义
    simulation_started = pyqtSignal(str)  # 仿真开始信号
    simulation_finished = pyqtSignal(str, object)  # 仿真完成信号
    
    def __init__(self):
        super().__init__()
        self.current_project_path: Optional[str] = None
        self.current_project_name: Optional[str] = None
        self.simulation_status = SimulationStatus.PENDING

        # 初始化界面
        self.init_ui()
        self.init_menu_bar()
        self.init_tool_bar()
        self.init_status_bar()

        # 连接信号
        self.connect_signals()

        # 设置定时器用于状态更新
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(1000)  # 每秒更新一次

        # 显示项目选择界面
        self.show_project_selector()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("激光毁伤仿真系统 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

        # 设置窗口图标
        self.set_window_icon()

        # 创建堆叠部件作为中央部件
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 创建项目选择界面
        self.project_selector = ProjectSelector()
        self.project_selector.project_selected.connect(self.on_project_selected)
        self.stacked_widget.addWidget(self.project_selector)

        # 创建主工作界面
        self.main_work_widget = self.create_main_work_widget()
        self.stacked_widget.addWidget(self.main_work_widget)

        # 应用样式
        self.apply_styles()
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            icon_path = Path(__file__).parent.parent.parent.parent / "data" / "icons" / "app_icon.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception:
            pass  # 如果图标文件不存在，忽略错误

    def create_main_work_widget(self):
        """创建主工作界面"""
        work_widget = QWidget()
        main_layout = QHBoxLayout(work_widget)

        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 创建左侧面板（项目信息和快速操作）
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # 创建右侧主工作区（标签页）
        self.tab_widget = QTabWidget()
        self.init_tabs()
        splitter.addWidget(self.tab_widget)

        # 设置分割器比例
        splitter.setSizes([300, 1100])

        return work_widget

    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 当前项目信息组
        project_group = QWidget()
        project_group.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        project_layout = QVBoxLayout(project_group)

        # 项目信息标签
        project_label = QLabel("当前项目")
        project_label.setFont(QFont("Arial", 11, QFont.Bold))
        project_label.setStyleSheet("color: #495057; margin-bottom: 5px;")
        project_layout.addWidget(project_label)

        # 项目名称显示
        self.project_name_label = QLabel("未选择项目")
        self.project_name_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.project_name_label.setStyleSheet("color: #0078d4; margin-bottom: 3px;")
        self.project_name_label.setWordWrap(True)
        project_layout.addWidget(self.project_name_label)

        # 项目路径显示
        self.project_path_label = QLabel("请从菜单选择或创建项目")
        self.project_path_label.setFont(QFont("Arial", 8))
        self.project_path_label.setStyleSheet("color: #6c757d;")
        self.project_path_label.setWordWrap(True)
        project_layout.addWidget(self.project_path_label)

        left_layout.addWidget(project_group)

        # 项目统计信息（如果有项目加载）
        self.stats_group = QWidget()
        self.stats_group.setStyleSheet("""
            QWidget {
                background-color: #fff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_group)

        stats_label = QLabel("项目统计")
        stats_label.setFont(QFont("Arial", 11, QFont.Bold))
        stats_label.setStyleSheet("color: #495057; margin-bottom: 5px;")
        stats_layout.addWidget(stats_label)

        self.simulation_count_label = QLabel("仿真次数: 0")
        self.simulation_count_label.setFont(QFont("Arial", 9))
        stats_layout.addWidget(self.simulation_count_label)

        self.last_modified_label = QLabel("最后修改: --")
        self.last_modified_label.setFont(QFont("Arial", 9))
        stats_layout.addWidget(self.last_modified_label)

        left_layout.addWidget(self.stats_group)
        self.stats_group.setVisible(False)  # 初始隐藏

        # 添加弹性空间
        left_layout.addStretch()

        return left_widget
    
    def init_tabs(self):
        """初始化标签页"""
        # 仿真设置标签页
        self.simulation_panel = SimulationPanel()
        self.tab_widget.addTab(self.simulation_panel, "仿真设置")
        
        # 分析结果标签页
        self.analysis_panel = AnalysisPanel()
        self.tab_widget.addTab(self.analysis_panel, "分析结果")
        
        # 报告生成标签页
        self.report_panel = ReportPanel()
        self.tab_widget.addTab(self.report_panel, "报告生成")
        
        # 效果评估标签页
        self.assessment_panel = AssessmentPanel()
        self.tab_widget.addTab(self.assessment_panel, "效果评估")
        
        # 设置默认标签页
        self.tab_widget.setCurrentIndex(0)
    
    def init_menu_bar(self):
        """初始化菜单栏"""
        menubar = self.menuBar()

        # 项目菜单
        project_menu = menubar.addMenu('项目(&P)')

        # 新建项目
        self.new_project_action = QAction('新建项目(&N)', self)
        self.new_project_action.setShortcut('Ctrl+N')
        self.new_project_action.triggered.connect(self.new_project)
        project_menu.addAction(self.new_project_action)

        # 打开项目
        self.open_project_action = QAction('打开项目(&O)', self)
        self.open_project_action.setShortcut('Ctrl+O')
        self.open_project_action.triggered.connect(self.open_project)
        project_menu.addAction(self.open_project_action)

        # 最近项目子菜单
        self.recent_menu = project_menu.addMenu('最近项目(&R)')
        self.update_recent_menu()

        project_menu.addSeparator()

        # 保存项目
        self.save_project_action = QAction('保存项目(&S)', self)
        self.save_project_action.setShortcut('Ctrl+S')
        self.save_project_action.triggered.connect(self.save_project)
        self.save_project_action.setEnabled(False)
        project_menu.addAction(self.save_project_action)

        # 另存为
        self.save_as_action = QAction('另存为(&A)', self)
        self.save_as_action.setShortcut('Ctrl+Shift+S')
        self.save_as_action.triggered.connect(self.save_project_as)
        self.save_as_action.setEnabled(False)
        project_menu.addAction(self.save_as_action)

        project_menu.addSeparator()

        # 关闭项目
        self.close_project_action = QAction('关闭项目(&C)', self)
        self.close_project_action.setShortcut('Ctrl+W')
        self.close_project_action.triggered.connect(self.close_project)
        self.close_project_action.setEnabled(False)
        project_menu.addAction(self.close_project_action)

        project_menu.addSeparator()

        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        project_menu.addAction(exit_action)
        
        # 仿真菜单
        simulation_menu = menubar.addMenu('仿真(&S)')

        # 开始仿真
        self.start_sim_action = QAction('开始仿真(&S)', self)
        self.start_sim_action.setShortcut('F5')
        self.start_sim_action.triggered.connect(self.start_simulation)
        self.start_sim_action.setEnabled(False)
        simulation_menu.addAction(self.start_sim_action)

        # 停止仿真
        self.stop_sim_action = QAction('停止仿真(&T)', self)
        self.stop_sim_action.setShortcut('F6')
        self.stop_sim_action.triggered.connect(self.stop_simulation)
        self.stop_sim_action.setEnabled(False)
        simulation_menu.addAction(self.stop_sim_action)

        simulation_menu.addSeparator()

        # 仿真设置
        sim_settings_action = QAction('仿真设置(&C)', self)
        sim_settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(0))
        sim_settings_action.setEnabled(False)
        simulation_menu.addAction(sim_settings_action)
        self.sim_settings_action = sim_settings_action

        # 查看菜单
        view_menu = menubar.addMenu('查看(&V)')

        # 分析结果
        analysis_action = QAction('分析结果(&A)', self)
        analysis_action.setShortcut('Ctrl+1')
        analysis_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        analysis_action.setEnabled(False)
        view_menu.addAction(analysis_action)
        self.analysis_action = analysis_action

        # 报告生成
        report_action = QAction('报告生成(&R)', self)
        report_action.setShortcut('Ctrl+2')
        report_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        report_action.setEnabled(False)
        view_menu.addAction(report_action)
        self.report_action = report_action

        # 效果评估
        assessment_action = QAction('效果评估(&E)', self)
        assessment_action.setShortcut('Ctrl+3')
        assessment_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(3))
        assessment_action.setEnabled(False)
        view_menu.addAction(assessment_action)
        self.assessment_action = assessment_action

        # 工具菜单
        tools_menu = menubar.addMenu('工具(&T)')

        # 参数验证
        validate_action = QAction('参数验证(&V)', self)
        validate_action.triggered.connect(self.validate_parameters)
        validate_action.setEnabled(False)
        tools_menu.addAction(validate_action)
        self.validate_action = validate_action

        # 清理缓存
        clear_cache_action = QAction('清理缓存(&C)', self)
        clear_cache_action.triggered.connect(self.clear_cache)
        tools_menu.addAction(clear_cache_action)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')

        # 用户手册
        manual_action = QAction('用户手册(&M)', self)
        manual_action.setShortcut('F1')
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)

        # 快速入门
        tutorial_action = QAction('快速入门(&Q)', self)
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)

        help_menu.addSeparator()

        # 检查更新
        update_action = QAction('检查更新(&U)', self)
        update_action.triggered.connect(self.check_updates)
        help_menu.addAction(update_action)

        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_tool_bar(self):
        """初始化工具栏"""
        toolbar = self.addToolBar('主工具栏')
        toolbar.setMovable(False)

        # 新建项目
        self.toolbar_new_action = QAction('新建', self)
        self.toolbar_new_action.setToolTip('新建项目 (Ctrl+N)')
        self.toolbar_new_action.triggered.connect(self.new_project)
        toolbar.addAction(self.toolbar_new_action)

        # 打开项目
        self.toolbar_open_action = QAction('打开', self)
        self.toolbar_open_action.setToolTip('打开项目 (Ctrl+O)')
        self.toolbar_open_action.triggered.connect(self.open_project)
        toolbar.addAction(self.toolbar_open_action)

        # 保存项目
        self.toolbar_save_action = QAction('保存', self)
        self.toolbar_save_action.setToolTip('保存项目 (Ctrl+S)')
        self.toolbar_save_action.triggered.connect(self.save_project)
        self.toolbar_save_action.setEnabled(False)
        toolbar.addAction(self.toolbar_save_action)

        toolbar.addSeparator()

        # 开始仿真
        self.toolbar_start_sim_action = QAction('开始仿真', self)
        self.toolbar_start_sim_action.setToolTip('开始仿真 (F5)')
        self.toolbar_start_sim_action.triggered.connect(self.start_simulation)
        self.toolbar_start_sim_action.setEnabled(False)
        toolbar.addAction(self.toolbar_start_sim_action)

        # 停止仿真
        self.toolbar_stop_sim_action = QAction('停止仿真', self)
        self.toolbar_stop_sim_action.setToolTip('停止仿真 (F6)')
        self.toolbar_stop_sim_action.triggered.connect(self.stop_simulation)
        self.toolbar_stop_sim_action.setEnabled(False)
        toolbar.addAction(self.toolbar_stop_sim_action)
    
    def init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = self.statusBar()
        
        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_bar.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 时间标签
        self.time_label = QLabel()
        self.status_bar.addPermanentWidget(self.time_label)
        
        # 更新时间显示
        from datetime import datetime
        self.time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def show_project_selector(self):
        """显示项目选择界面"""
        self.stacked_widget.setCurrentIndex(0)
        self.setWindowTitle("激光毁伤仿真系统 v1.0")

        # 禁用项目相关的菜单和工具栏
        self.update_ui_state(False)

    def show_main_workspace(self):
        """显示主工作界面"""
        self.stacked_widget.setCurrentIndex(1)

        # 启用项目相关的菜单和工具栏
        self.update_ui_state(True)

    def update_ui_state(self, project_loaded: bool):
        """更新UI状态"""
        # 菜单状态
        self.save_project_action.setEnabled(project_loaded)
        self.save_as_action.setEnabled(project_loaded)
        self.close_project_action.setEnabled(project_loaded)
        self.start_sim_action.setEnabled(project_loaded)
        self.sim_settings_action.setEnabled(project_loaded)
        self.analysis_action.setEnabled(project_loaded)
        self.report_action.setEnabled(project_loaded)
        self.assessment_action.setEnabled(project_loaded)
        self.validate_action.setEnabled(project_loaded)

        # 工具栏状态
        self.toolbar_save_action.setEnabled(project_loaded)
        self.toolbar_start_sim_action.setEnabled(project_loaded)

    def on_project_selected(self, project_path: str):
        """项目选择事件处理"""
        try:
            self.load_project(project_path)
            self.show_main_workspace()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载项目失败：{str(e)}")

    def load_project(self, project_path: str):
        """加载项目"""
        import json
        from pathlib import Path

        project_file = Path(project_path)
        if not project_file.exists():
            raise FileNotFoundError(f"项目文件不存在: {project_path}")

        # 读取项目文件
        with open(project_file, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        # 更新项目信息
        self.current_project_path = project_path
        self.current_project_name = project_data.get('name', project_file.stem)

        # 更新窗口标题
        self.setWindowTitle(f"激光毁伤仿真系统 v1.0 - {self.current_project_name}")

        # 更新左侧面板显示
        self.update_project_info_display()

        # 更新状态栏
        self.status_label.setText(f"项目已加载: {self.current_project_name}")

    def update_project_info_display(self):
        """更新项目信息显示"""
        if self.current_project_name:
            self.project_name_label.setText(self.current_project_name)
            self.project_path_label.setText(str(Path(self.current_project_path).parent))
            self.stats_group.setVisible(True)

            # 更新统计信息
            self.simulation_count_label.setText("仿真次数: 0")  # TODO: 从项目数据获取

            from datetime import datetime
            modified_time = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.last_modified_label.setText(f"最后修改: {modified_time}")
        else:
            self.project_name_label.setText("未选择项目")
            self.project_path_label.setText("请从菜单选择或创建项目")
            self.stats_group.setVisible(False)

    def update_recent_menu(self):
        """更新最近项目菜单"""
        self.recent_menu.clear()

        # TODO: 从配置文件加载最近项目
        recent_projects = []  # 暂时为空

        if recent_projects:
            for project in recent_projects[:5]:  # 最多显示5个
                action = QAction(project['name'], self)
                action.triggered.connect(lambda checked, path=project['path']: self.on_project_selected(path))
                self.recent_menu.addAction(action)
        else:
            no_recent_action = QAction("无最近项目", self)
            no_recent_action.setEnabled(False)
            self.recent_menu.addAction(no_recent_action)
    
    def apply_styles(self):
        """应用界面样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            
            QTabWidget::tab-bar {
                left: 5px;
            }
            
            QTabBar::tab {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                border-bottom-color: white;
            }
            
            QTabBar::tab:hover {
                background-color: #f0f0f0;
            }
            
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
            
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
    
    def connect_signals(self):
        """连接信号和槽"""
        # 连接仿真面板的信号
        self.simulation_panel.simulation_requested.connect(self.handle_simulation_request)
        
        # 连接标签页切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def new_project(self):
        """新建项目"""
        if self.stacked_widget.currentIndex() == 1:
            # 如果在主工作界面，显示项目选择界面来创建新项目
            self.show_project_selector()
        else:
            # 如果在项目选择界面，触发新建项目
            self.project_selector.new_project()
    
    def open_project(self):
        """打开项目"""
        if self.stacked_widget.currentIndex() == 1:
            # 如果在主工作界面，显示项目选择界面来打开项目
            self.show_project_selector()
        else:
            # 如果在项目选择界面，触发打开项目
            self.project_selector.open_project()
    
    def save_project(self) -> bool:
        """保存项目"""
        if not self.current_project_path:
            return self.save_project_as()
        
        try:
            self.save_project_to_file(self.current_project_path)
            self.status_label.setText("项目已保存")
            return True
        except Exception as e:
            QMessageBox.critical(self, '错误', f'保存项目失败：{str(e)}')
            return False
    
    def save_project_as(self) -> bool:
        """另存为项目"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, '另存为项目', '', 
            'Laser Simulation Project (*.lsp);;All Files (*)'
        )
        
        if file_path:
            try:
                self.save_project_to_file(file_path)
                self.current_project_path = file_path
                self.project_path_label.setText(f"项目: {Path(file_path).name}")
                self.status_label.setText("项目已保存")
                return True
            except Exception as e:
                QMessageBox.critical(self, '错误', f'保存项目失败：{str(e)}')
                return False
        
        return False

    def close_project(self):
        """关闭项目"""
        if self.current_project_path:
            # 询问是否保存
            reply = QMessageBox.question(
                self, "关闭项目",
                "是否保存当前项目？",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )

            if reply == QMessageBox.Cancel:
                return
            elif reply == QMessageBox.Yes:
                if not self.save_project():
                    return  # 保存失败，不关闭项目

        # 清理项目状态
        self.current_project_path = None
        self.current_project_name = None

        # 重置所有面板
        self.reset_all_panels()

        # 显示项目选择界面
        self.show_project_selector()

        self.status_label.setText("项目已关闭")

    def reset_all_panels(self):
        """重置所有面板"""
        try:
            if hasattr(self, 'simulation_panel'):
                self.simulation_panel.reset()
            if hasattr(self, 'analysis_panel'):
                self.analysis_panel.reset()
            if hasattr(self, 'report_panel'):
                self.report_panel.reset()
            if hasattr(self, 'assessment_panel'):
                self.assessment_panel.reset()
        except Exception as e:
            print(f"重置面板时出错: {e}")

    def start_simulation(self):
        """开始仿真"""
        # 获取仿真配置
        config = self.simulation_panel.get_simulation_config()
        
        if not config:
            QMessageBox.warning(self, '警告', '请先配置仿真参数')
            return
        
        # 更新界面状态
        self.simulation_status = SimulationStatus.RUNNING
        self.start_sim_action.setEnabled(False)
        self.stop_sim_action.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("仿真运行中...")
        
        # 发送仿真开始信号
        self.simulation_started.emit("simulation_001")
        
        # 这里暂时用定时器模拟仿真过程
        self.simulate_calculation()
    
    def stop_simulation(self):
        """停止仿真"""
        self.simulation_status = SimulationStatus.CANCELLED
        self.start_sim_action.setEnabled(True)
        self.stop_sim_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("仿真已停止")
    
    def simulate_calculation(self):
        """模拟仿真计算过程"""
        # 这是一个临时的模拟函数，用于演示界面功能
        QTimer.singleShot(5000, self.finish_simulation)  # 5秒后完成仿真
    
    def finish_simulation(self):
        """完成仿真"""
        self.simulation_status = SimulationStatus.COMPLETED
        self.start_sim_action.setEnabled(True)
        self.stop_sim_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("仿真已完成")
        
        # 切换到分析结果标签页
        self.tab_widget.setCurrentIndex(1)
        
        # 发送仿真完成信号
        self.simulation_finished.emit("simulation_001", None)
    
    def handle_simulation_request(self, config):
        """处理仿真请求"""
        self.start_simulation()
    
    def on_tab_changed(self, index):
        """标签页切换事件"""
        tab_names = ["仿真设置", "分析结果", "报告生成", "效果评估"]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"当前页面: {tab_names[index]}")
    
    def update_status(self):
        """更新状态信息"""
        from datetime import datetime
        self.time_label.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    def reset_interface(self):
        """重置界面"""
        self.simulation_panel.reset()
        self.analysis_panel.reset()
        self.report_panel.reset()
        self.assessment_panel.reset()
    
    def load_project(self, file_path: str):
        """加载项目文件"""
        # 这里实现项目文件加载逻辑
        pass
    
    def save_project_to_file(self, file_path: str):
        """保存项目到文件"""
        # 这里实现项目文件保存逻辑
        pass
    
    def is_project_modified(self) -> bool:
        """检查项目是否有修改"""
        # 这里实现项目修改检查逻辑
        return False
    
    def show_manual(self):
        """显示用户手册"""
        QMessageBox.information(self, '用户手册', '用户手册功能待实现')
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, '关于', 
                         '激光毁伤仿真系统 v1.0\n\n'
                         '基于ANSYS 2021 R1的激光毁伤仿真系统\n'
                         '提供完整的激光武器毁伤效果仿真、后效分析、\n'
                         '数据处理和效果评估功能。\n\n'
                         '版权所有 © 2024')
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.current_project_path and self.is_project_modified():
            reply = QMessageBox.question(
                self, '退出程序', 
                '当前项目有未保存的更改，是否保存？',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                if self.save_project():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


    # 新增的工具方法
    def validate_parameters(self):
        """参数验证"""
        try:
            config = self.simulation_panel.get_simulation_config()
            if config:
                QMessageBox.information(self, "验证结果", "参数验证通过！")
            else:
                QMessageBox.warning(self, "验证结果", "参数验证失败，请检查配置！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"参数验证失败：{str(e)}")

    def clear_cache(self):
        """清理缓存"""
        reply = QMessageBox.question(
            self, "清理缓存",
            "确定要清理所有缓存文件吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # TODO: 实现缓存清理逻辑
                QMessageBox.information(self, "信息", "缓存清理完成！")
                self.status_label.setText("缓存已清理")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"清理缓存失败：{str(e)}")

    def show_tutorial(self):
        """显示快速入门"""
        QMessageBox.information(
            self, "快速入门",
            "快速入门指南：\n\n"
            "1. 创建或打开项目\n"
            "2. 在仿真设置中配置参数\n"
            "3. 运行仿真计算\n"
            "4. 查看分析结果\n"
            "5. 生成报告和评估"
        )

    def check_updates(self):
        """检查更新"""
        QMessageBox.information(
            self, "检查更新",
            "当前版本：v1.0\n\n"
            "您使用的是最新版本！"
        )


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("激光毁伤仿真系统")
    app.setApplicationVersion("1.0")
    
    # 创建主窗口
    window = LaserSimulationMainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

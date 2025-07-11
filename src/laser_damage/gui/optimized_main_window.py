"""
优化后的主窗口界面

基于工业GUI设计原则的优化版本。
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QMenuBar, QStatusBar, QToolBar, QAction, QMessageBox,
    QFileDialog, QProgressBar, QLabel, QSplitter, QDockWidget,
    QTreeWidget, QTreeWidgetItem, QPushButton, QComboBox, QFrame
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSettings
from PyQt5.QtGui import QIcon, QPixmap, QFont, QKeySequence

from .simulation_panel import SimulationPanel
from .analysis_panel import AnalysisPanel
from .report_panel import ReportPanel
from .assessment_panel import AssessmentPanel
from ..core.data_models import SimulationStatus


class ProjectExplorer(QDockWidget):
    """项目资源管理器"""
    
    project_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("项目资源管理器", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # 创建主部件
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 项目选择区域
        project_frame = QFrame()
        project_frame.setFrameStyle(QFrame.StyledPanel)
        project_layout = QVBoxLayout(project_frame)
        
        # 当前项目显示
        self.current_project_label = QLabel("当前项目: 未选择")
        self.current_project_label.setFont(QFont("Arial", 9, QFont.Bold))
        project_layout.addWidget(self.current_project_label)
        
        # 快速项目切换
        project_combo_layout = QHBoxLayout()
        project_combo_layout.addWidget(QLabel("快速切换:"))
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(150)
        self.project_combo.currentTextChanged.connect(self.on_project_changed)
        project_combo_layout.addWidget(self.project_combo)
        project_layout.addLayout(project_combo_layout)
        
        # 项目操作按钮
        button_layout = QHBoxLayout()
        self.new_btn = QPushButton("新建")
        self.new_btn.setMaximumWidth(50)
        self.open_btn = QPushButton("打开")
        self.open_btn.setMaximumWidth(50)
        button_layout.addWidget(self.new_btn)
        button_layout.addWidget(self.open_btn)
        button_layout.addStretch()
        project_layout.addLayout(button_layout)
        
        layout.addWidget(project_frame)
        
        # 项目文件树
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("项目文件")
        layout.addWidget(self.file_tree)
        
        # 快速操作区域
        quick_frame = QFrame()
        quick_frame.setFrameStyle(QFrame.StyledPanel)
        quick_layout = QVBoxLayout(quick_frame)
        
        quick_layout.addWidget(QLabel("快速操作"))
        self.run_simulation_btn = QPushButton("运行仿真")
        self.run_simulation_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        quick_layout.addWidget(self.run_simulation_btn)
        
        self.view_results_btn = QPushButton("查看结果")
        quick_layout.addWidget(self.view_results_btn)
        
        layout.addWidget(quick_frame)
        
        self.setWidget(widget)
        self.load_recent_projects()
    
    def load_recent_projects(self):
        """加载最近项目"""
        # TODO: 从配置文件加载
        recent_projects = ["项目1", "项目2", "项目3"]
        self.project_combo.addItems(["选择项目..."] + recent_projects)
    
    def on_project_changed(self, project_name):
        """项目切换事件"""
        if project_name and project_name != "选择项目...":
            self.current_project_label.setText(f"当前项目: {project_name}")
            self.project_selected.emit(project_name)


class OptimizedMainWindow(QMainWindow):
    """优化后的主窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_project_path: Optional[str] = None
        self.simulation_status = SimulationStatus.PENDING
        self.settings = QSettings("LaserSimulation", "MainWindow")
        
        self.init_ui()
        self.init_menu_bar()
        self.init_tool_bar()
        self.init_status_bar()
        self.init_dock_widgets()
        self.restore_layout()
        
        # 连接信号
        self.connect_signals()
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("激光毁伤仿真系统 v2.0")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1200, 800)
        
        # 创建中央标签页部件
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabPosition(QTabWidget.North)
        self.central_tabs.setMovable(True)
        self.setCentralWidget(self.central_tabs)
        
        # 创建功能面板
        self.simulation_panel = SimulationPanel()
        self.analysis_panel = AnalysisPanel()
        self.report_panel = ReportPanel()
        self.assessment_panel = AssessmentPanel()
        
        # 添加标签页
        self.central_tabs.addTab(self.simulation_panel, "仿真设置")
        self.central_tabs.addTab(self.analysis_panel, "结果分析")
        self.central_tabs.addTab(self.report_panel, "报告生成")
        self.central_tabs.addTab(self.assessment_panel, "效果评估")
        
        # 设置标签页图标（如果有的话）
        self.apply_styles()
    
    def init_menu_bar(self):
        """初始化菜单栏 - 极简版"""
        menubar = self.menuBar()

        # 文件菜单 - 整合项目管理和文件操作
        file_menu = menubar.addMenu('File')

        # 项目管理子菜单
        project_submenu = file_menu.addMenu('项目(&P)')

        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_project)
        project_submenu.addAction(new_action)

        open_action = QAction('打开项目(&O)', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_project)
        project_submenu.addAction(open_action)

        project_submenu.addSeparator()

        save_action = QAction('保存项目(&S)', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_project)
        project_submenu.addAction(save_action)

        save_as_action = QAction('另存为(&A)', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_project_as)
        project_submenu.addAction(save_as_action)

        # 仿真控制
        file_menu.addSeparator()

        run_action = QAction('运行仿真(&R)', self)
        run_action.setShortcut(Qt.Key_F5)
        run_action.triggered.connect(self.run_simulation)
        file_menu.addAction(run_action)

        stop_action = QAction('停止仿真(&T)', self)
        stop_action.setShortcut(Qt.Key_F6)
        stop_action.triggered.connect(self.stop_simulation)
        file_menu.addAction(stop_action)

        # 视图控制
        file_menu.addSeparator()

        view_submenu = file_menu.addMenu('视图(&V)')

        # 停靠窗口控制
        self.project_dock_action = QAction('项目资源管理器(&P)', self)
        self.project_dock_action.setCheckable(True)
        self.project_dock_action.setChecked(True)
        view_submenu.addAction(self.project_dock_action)

        # 标签页快速切换
        view_submenu.addSeparator()
        simulation_action = QAction('仿真设置(&1)', self)
        simulation_action.setShortcut('Ctrl+1')
        simulation_action.triggered.connect(lambda: self.central_tabs.setCurrentIndex(0))
        view_submenu.addAction(simulation_action)

        analysis_action = QAction('结果分析(&2)', self)
        analysis_action.setShortcut('Ctrl+2')
        analysis_action.triggered.connect(lambda: self.central_tabs.setCurrentIndex(1))
        view_submenu.addAction(analysis_action)

        report_action = QAction('报告生成(&3)', self)
        report_action.setShortcut('Ctrl+3')
        report_action.triggered.connect(lambda: self.central_tabs.setCurrentIndex(2))
        view_submenu.addAction(report_action)

        assessment_action = QAction('效果评估(&4)', self)
        assessment_action.setShortcut('Ctrl+4')
        assessment_action.triggered.connect(lambda: self.central_tabs.setCurrentIndex(3))
        view_submenu.addAction(assessment_action)

        # 退出
        file_menu.addSeparator()
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 帮助菜单 - 整合所有帮助和工具功能
        help_menu = menubar.addMenu('Help')

        # 用户帮助
        manual_action = QAction('用户手册(&M)', self)
        manual_action.setShortcut(Qt.Key_F1)
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)

        tutorial_action = QAction('快速入门(&Q)', self)
        tutorial_action.triggered.connect(self.show_tutorial)
        help_menu.addAction(tutorial_action)

        # 工具功能
        help_menu.addSeparator()

        tools_submenu = help_menu.addMenu('工具(&T)')

        validate_action = QAction('参数验证(&V)', self)
        validate_action.triggered.connect(self.validate_parameters)
        tools_submenu.addAction(validate_action)

        clear_cache_action = QAction('清理缓存(&C)', self)
        clear_cache_action.triggered.connect(self.clear_cache)
        tools_submenu.addAction(clear_cache_action)

        # 系统信息
        help_menu.addSeparator()

        check_update_action = QAction('检查更新(&U)', self)
        check_update_action.triggered.connect(self.check_updates)
        help_menu.addAction(check_update_action)

        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_tool_bar(self):
        """初始化工具栏 - 精简版"""
        toolbar = self.addToolBar('主工具栏')
        toolbar.setMovable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        # 项目操作
        new_action = QAction('新建', self)
        new_action.setToolTip('新建项目 (Ctrl+N)')
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        open_action = QAction('打开', self)
        open_action.setToolTip('打开项目 (Ctrl+O)')
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        save_action = QAction('保存', self)
        save_action.setToolTip('保存项目 (Ctrl+S)')
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 仿真控制
        self.run_action = QAction('运行', self)
        self.run_action.setToolTip('运行仿真 (F5)')
        self.run_action.triggered.connect(self.run_simulation)
        toolbar.addAction(self.run_action)
        
        self.stop_action = QAction('停止', self)
        self.stop_action.setToolTip('停止仿真 (F6)')
        self.stop_action.triggered.connect(self.stop_simulation)
        self.stop_action.setEnabled(False)
        toolbar.addAction(self.stop_action)
    
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
        
        # 项目信息
        self.project_info_label = QLabel("无项目")
        self.status_bar.addPermanentWidget(self.project_info_label)
    
    def init_dock_widgets(self):
        """初始化停靠窗口"""
        # 项目资源管理器
        self.project_dock = ProjectExplorer(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.project_dock)
        
        # 连接停靠窗口的显示/隐藏到菜单
        self.project_dock_action.toggled.connect(self.project_dock.setVisible)
        self.project_dock.visibilityChanged.connect(self.project_dock_action.setChecked)
    
    def restore_layout(self):
        """恢复窗口布局"""
        self.restoreGeometry(self.settings.value("geometry", b""))
        self.restoreState(self.settings.value("windowState", b""))
    
    def save_layout(self):
        """保存窗口布局"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
    def connect_signals(self):
        """连接信号"""
        self.project_dock.project_selected.connect(self.load_project)
        self.project_dock.run_simulation_btn.clicked.connect(self.run_simulation)
        self.project_dock.view_results_btn.clicked.connect(lambda: self.central_tabs.setCurrentIndex(1))
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
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
            QDockWidget {
                titlebar-close-icon: none;
                titlebar-normal-icon: none;
            }
            QDockWidget::title {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #c0c0c0;
            }
        """)
    
    # 项目管理方法
    def new_project(self):
        """新建项目"""
        # TODO: 实现新建项目逻辑
        QMessageBox.information(self, "信息", "新建项目功能")
    
    def open_project(self):
        """打开项目"""
        # TODO: 实现打开项目逻辑
        QMessageBox.information(self, "信息", "打开项目功能")
    
    def save_project(self):
        """保存项目"""
        # TODO: 实现保存项目逻辑
        QMessageBox.information(self, "信息", "保存项目功能")
    
    def load_project(self, project_name):
        """加载项目"""
        self.project_info_label.setText(f"项目: {project_name}")
        self.status_label.setText(f"已加载项目: {project_name}")
    
    # 仿真控制方法
    def run_simulation(self):
        """运行仿真"""
        self.run_action.setEnabled(False)
        self.stop_action.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.status_label.setText("仿真运行中...")
        
        # 模拟仿真过程
        QTimer.singleShot(3000, self.simulation_finished)
    
    def stop_simulation(self):
        """停止仿真"""
        self.simulation_finished()
        self.status_label.setText("仿真已停止")
    
    def simulation_finished(self):
        """仿真完成"""
        self.run_action.setEnabled(True)
        self.stop_action.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("仿真完成")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
                         "激光毁伤仿真系统 v2.0\n\n"
                         "基于工业GUI设计原则优化的版本")
    
    def closeEvent(self, event):
        """关闭事件"""
        self.save_layout()
        event.accept()


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("激光毁伤仿真系统")
    app.setApplicationVersion("2.0")
    
    # 创建主窗口
    window = OptimizedMainWindow()
    window.show()
    
    # 运行应用
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

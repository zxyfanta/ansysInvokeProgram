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
    QFileDialog, QProgressBar, QLabel, QSplitter
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont

from .simulation_panel import SimulationPanel
from .analysis_panel import AnalysisPanel
from .report_panel import ReportPanel
from .assessment_panel import AssessmentPanel
from ..core.data_models import SimulationStatus


class LaserSimulationMainWindow(QMainWindow):
    """激光毁伤仿真系统主窗口"""
    
    # 信号定义
    simulation_started = pyqtSignal(str)  # 仿真开始信号
    simulation_finished = pyqtSignal(str, object)  # 仿真完成信号
    
    def __init__(self):
        super().__init__()
        self.current_project_path: Optional[str] = None
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
    
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("激光毁伤仿真系统 v1.0")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建左侧面板（项目树和参数设置）
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 创建右侧主工作区（标签页）
        self.tab_widget = QTabWidget()
        self.init_tabs()
        splitter.addWidget(self.tab_widget)
        
        # 设置分割器比例
        splitter.setSizes([300, 1100])
        
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
    
    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 项目信息标签
        project_label = QLabel("项目信息")
        project_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(project_label)
        
        # 项目路径显示
        self.project_path_label = QLabel("未加载项目")
        self.project_path_label.setWordWrap(True)
        self.project_path_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        left_layout.addWidget(self.project_path_label)
        
        # 快速操作按钮区域
        from PyQt5.QtWidgets import QPushButton
        
        quick_actions_label = QLabel("快速操作")
        quick_actions_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_layout.addWidget(quick_actions_label)
        
        # 新建项目按钮
        new_project_btn = QPushButton("新建项目")
        new_project_btn.clicked.connect(self.new_project)
        left_layout.addWidget(new_project_btn)
        
        # 打开项目按钮
        open_project_btn = QPushButton("打开项目")
        open_project_btn.clicked.connect(self.open_project)
        left_layout.addWidget(open_project_btn)
        
        # 保存项目按钮
        self.save_project_btn = QPushButton("保存项目")
        self.save_project_btn.clicked.connect(self.save_project)
        self.save_project_btn.setEnabled(False)
        left_layout.addWidget(self.save_project_btn)
        
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
        
        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        
        # 新建项目
        new_action = QAction('新建项目(&N)', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        # 打开项目
        open_action = QAction('打开项目(&O)', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # 保存项目
        save_action = QAction('保存项目(&S)', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        # 另存为
        save_as_action = QAction('另存为(&A)', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 仿真菜单
        simulation_menu = menubar.addMenu('仿真(&S)')
        
        # 开始仿真
        start_sim_action = QAction('开始仿真(&S)', self)
        start_sim_action.setShortcut('F5')
        start_sim_action.triggered.connect(self.start_simulation)
        simulation_menu.addAction(start_sim_action)
        
        # 停止仿真
        stop_sim_action = QAction('停止仿真(&T)', self)
        stop_sim_action.setShortcut('F6')
        stop_sim_action.triggered.connect(self.stop_simulation)
        simulation_menu.addAction(stop_sim_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        
        # 用户手册
        manual_action = QAction('用户手册(&M)', self)
        manual_action.triggered.connect(self.show_manual)
        help_menu.addAction(manual_action)
        
        # 关于
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def init_tool_bar(self):
        """初始化工具栏"""
        toolbar = self.addToolBar('主工具栏')
        toolbar.setMovable(False)
        
        # 新建项目
        new_action = QAction('新建', self)
        new_action.setToolTip('新建项目 (Ctrl+N)')
        new_action.triggered.connect(self.new_project)
        toolbar.addAction(new_action)
        
        # 打开项目
        open_action = QAction('打开', self)
        open_action.setToolTip('打开项目 (Ctrl+O)')
        open_action.triggered.connect(self.open_project)
        toolbar.addAction(open_action)
        
        # 保存项目
        save_action = QAction('保存', self)
        save_action.setToolTip('保存项目 (Ctrl+S)')
        save_action.triggered.connect(self.save_project)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()
        
        # 开始仿真
        self.start_sim_action = QAction('开始仿真', self)
        self.start_sim_action.setToolTip('开始仿真 (F5)')
        self.start_sim_action.triggered.connect(self.start_simulation)
        toolbar.addAction(self.start_sim_action)
        
        # 停止仿真
        self.stop_sim_action = QAction('停止仿真', self)
        self.stop_sim_action.setToolTip('停止仿真 (F6)')
        self.stop_sim_action.triggered.connect(self.stop_simulation)
        self.stop_sim_action.setEnabled(False)
        toolbar.addAction(self.stop_sim_action)
    
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
        # 如果当前有未保存的项目，询问是否保存
        if self.current_project_path and self.is_project_modified():
            reply = QMessageBox.question(
                self, '新建项目', 
                '当前项目有未保存的更改，是否保存？',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                if not self.save_project():
                    return
            elif reply == QMessageBox.Cancel:
                return
        
        # 重置界面
        self.reset_interface()
        self.current_project_path = None
        self.project_path_label.setText("新项目")
        self.save_project_btn.setEnabled(True)
        self.status_label.setText("新项目已创建")
    
    def open_project(self):
        """打开项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, '打开项目', '', 
            'Laser Simulation Project (*.lsp);;All Files (*)'
        )
        
        if file_path:
            try:
                self.load_project(file_path)
                self.current_project_path = file_path
                self.project_path_label.setText(f"项目: {Path(file_path).name}")
                self.save_project_btn.setEnabled(True)
                self.status_label.setText(f"项目已打开: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.critical(self, '错误', f'打开项目失败：{str(e)}')
    
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

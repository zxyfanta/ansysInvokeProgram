"""
项目选择界面

提供项目选择、创建和管理功能。
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QDialog, QLineEdit, QTextEdit, QFormLayout, QDialogButtonBox,
    QGroupBox, QGridLayout, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon


class ProjectInfo:
    """项目信息类"""
    
    def __init__(self, name: str = "", path: str = "", description: str = ""):
        self.name = name
        self.path = path
        self.description = description
        self.created_time = datetime.now()
        self.modified_time = datetime.now()
        self.version = "1.0"
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "created_time": self.created_time.isoformat(),
            "modified_time": self.modified_time.isoformat(),
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProjectInfo':
        """从字典创建"""
        project = cls(data.get("name", ""), data.get("path", ""), data.get("description", ""))
        project.created_time = datetime.fromisoformat(data.get("created_time", datetime.now().isoformat()))
        project.modified_time = datetime.fromisoformat(data.get("modified_time", datetime.now().isoformat()))
        project.version = data.get("version", "1.0")
        return project


class NewProjectDialog(QDialog):
    """新建项目对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("新建项目")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 项目信息表单
        form_layout = QFormLayout()
        
        # 项目名称
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入项目名称")
        form_layout.addRow("项目名称*:", self.name_edit)
        
        # 项目路径
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("选择项目保存路径")
        self.browse_btn = QPushButton("浏览...")
        self.browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.browse_btn)
        form_layout.addRow("保存路径*:", path_layout)
        
        # 项目描述
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("请输入项目描述（可选）")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("项目描述:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 设置默认路径
        default_path = str(Path.home() / "LaserSimulationProjects")
        self.path_edit.setText(default_path)
    
    def browse_path(self):
        """浏览路径"""
        path = QFileDialog.getExistingDirectory(self, "选择项目保存路径", self.path_edit.text())
        if path:
            self.path_edit.setText(path)
    
    def get_project_info(self) -> Optional[ProjectInfo]:
        """获取项目信息"""
        name = self.name_edit.text().strip()
        path = self.path_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not name or not path:
            QMessageBox.warning(self, "警告", "项目名称和保存路径不能为空！")
            return None
        
        # 创建完整的项目路径
        full_path = Path(path) / name
        
        return ProjectInfo(name, str(full_path), description)


class ProjectCard(QFrame):
    """项目卡片组件"""
    
    clicked = pyqtSignal(str)  # 项目路径
    
    def __init__(self, project_info: ProjectInfo, parent=None):
        super().__init__(parent)
        self.project_info = project_info
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: white;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #0078d4;
                background-color: #f8f9fa;
            }
        """)
        self.setFixedSize(280, 120)
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 项目名称
        name_label = QLabel(self.project_info.name)
        name_label.setFont(QFont("Arial", 12, QFont.Bold))
        name_label.setStyleSheet("color: #333; margin-bottom: 5px;")
        layout.addWidget(name_label)
        
        # 项目描述
        desc_text = self.project_info.description[:50] + "..." if len(self.project_info.description) > 50 else self.project_info.description
        desc_label = QLabel(desc_text or "无描述")
        desc_label.setFont(QFont("Arial", 9))
        desc_label.setStyleSheet("color: #666;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 修改时间
        time_label = QLabel(f"修改时间: {self.project_info.modified_time.strftime('%Y-%m-%d %H:%M')}")
        time_label.setFont(QFont("Arial", 8))
        time_label.setStyleSheet("color: #999;")
        layout.addWidget(time_label)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.project_info.path)
        super().mousePressEvent(event)


class ProjectSelector(QWidget):
    """项目选择界面"""
    
    # 信号定义
    project_selected = pyqtSignal(str)  # 项目路径
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_projects: List[ProjectInfo] = []
        self.init_ui()
        self.load_recent_projects()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 30, 50, 30)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # 应用标题
        title_label = QLabel("激光毁伤仿真系统")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #0078d4; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("选择或创建一个项目开始工作")
        subtitle_label.setFont(QFont("Arial", 12))
        subtitle_label.setStyleSheet("color: #666; margin-bottom: 30px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle_label)
        
        layout.addLayout(title_layout)
        
        # 操作按钮区域
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        # 新建项目按钮
        self.new_project_btn = QPushButton("新建项目")
        self.new_project_btn.setFixedSize(120, 40)
        self.new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.new_project_btn.clicked.connect(self.new_project)
        button_layout.addWidget(self.new_project_btn)
        
        # 打开项目按钮
        self.open_project_btn = QPushButton("打开项目")
        self.open_project_btn.setFixedSize(120, 40)
        self.open_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f2f1;
                color: #323130;
                border: 1px solid #8a8886;
                border-radius: 6px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #edebe9;
            }
        """)
        self.open_project_btn.clicked.connect(self.open_project)
        button_layout.addWidget(self.open_project_btn)
        
        layout.addLayout(button_layout)
        
        # 最近项目区域
        recent_group = QGroupBox("最近的项目")
        recent_group.setFont(QFont("Arial", 11, QFont.Bold))
        recent_layout = QVBoxLayout(recent_group)
        
        # 项目卡片滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setMaximumHeight(300)
        
        self.projects_widget = QWidget()
        self.projects_layout = QGridLayout(self.projects_widget)
        self.projects_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.projects_widget)
        recent_layout.addWidget(scroll_area)
        
        layout.addWidget(recent_group)
        
        # 添加弹性空间
        layout.addStretch()
    
    def new_project(self):
        """新建项目"""
        dialog = NewProjectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            project_info = dialog.get_project_info()
            if project_info:
                self.create_project(project_info)
    
    def open_project(self):
        """打开项目"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开项目", "", "项目文件 (*.lsp);;所有文件 (*)"
        )
        if file_path:
            self.project_selected.emit(file_path)
    
    def create_project(self, project_info: ProjectInfo):
        """创建项目"""
        try:
            # 创建项目目录
            project_path = Path(project_info.path)
            project_path.mkdir(parents=True, exist_ok=True)
            
            # 创建项目文件
            project_file = project_path / f"{project_info.name}.lsp"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_info.to_dict(), f, indent=2, ensure_ascii=False)
            
            # 添加到最近项目
            self.add_recent_project(project_info)
            
            # 发射项目选择信号
            self.project_selected.emit(str(project_file))
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建项目失败：{str(e)}")
    
    def load_recent_projects(self):
        """加载最近项目"""
        try:
            config_path = Path.home() / ".laser_simulation" / "recent_projects.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recent_projects = [ProjectInfo.from_dict(item) for item in data]
            
            self.update_recent_projects_display()
            
        except Exception as e:
            print(f"加载最近项目失败: {e}")
    
    def save_recent_projects(self):
        """保存最近项目"""
        try:
            config_path = Path.home() / ".laser_simulation"
            config_path.mkdir(exist_ok=True)
            
            config_file = config_path / "recent_projects.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                data = [project.to_dict() for project in self.recent_projects]
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"保存最近项目失败: {e}")
    
    def add_recent_project(self, project_info: ProjectInfo):
        """添加最近项目"""
        # 移除重复项目
        self.recent_projects = [p for p in self.recent_projects if p.path != project_info.path]
        
        # 添加到开头
        self.recent_projects.insert(0, project_info)
        
        # 限制数量
        self.recent_projects = self.recent_projects[:10]
        
        # 保存并更新显示
        self.save_recent_projects()
        self.update_recent_projects_display()
    
    def update_recent_projects_display(self):
        """更新最近项目显示"""
        # 清除现有卡片
        for i in reversed(range(self.projects_layout.count())):
            child = self.projects_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # 添加项目卡片
        row, col = 0, 0
        for project in self.recent_projects:
            # 检查项目文件是否存在
            if Path(project.path).exists() or Path(project.path + f"/{project.name}.lsp").exists():
                card = ProjectCard(project)
                card.clicked.connect(self.on_project_card_clicked)
                self.projects_layout.addWidget(card, row, col)
                
                col += 1
                if col >= 3:  # 每行3个卡片
                    col = 0
                    row += 1
    
    def on_project_card_clicked(self, project_path: str):
        """项目卡片点击事件"""
        # 查找项目文件
        path = Path(project_path)
        if path.is_dir():
            # 如果是目录，查找.lsp文件
            lsp_files = list(path.glob("*.lsp"))
            if lsp_files:
                self.project_selected.emit(str(lsp_files[0]))
            else:
                QMessageBox.warning(self, "警告", "项目目录中未找到项目文件！")
        elif path.suffix == '.lsp':
            self.project_selected.emit(project_path)
        else:
            QMessageBox.warning(self, "警告", "无效的项目文件！")

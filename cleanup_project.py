#!/usr/bin/env python3
"""
项目清理脚本

移除冗余文件和内容，优化项目结构。
"""

import os
import shutil
from pathlib import Path


def cleanup_redundant_files():
    """清理冗余文件"""
    
    # 要删除的冗余文件
    redundant_files = [
        "abc.txt",
        "check_gui_status.py", 
        "simple_check.py",
        "test_gui.py",
        "test_project_management.py",
        "GUI使用说明.md",
        "GUI开发完成报告.md", 
        "README.md",  # 保留README_NEW.md
        "开发方案设计文档.md",
        "开发流程与规范.md",
        "测试策略设计.md",
        "环境搭建指南.md",
        "环境设置完成报告.md",
        "环境配置指南.md",
        "部署与运维方案.md",
        "项目总结报告.md",
        "项目文件总结.md",
        "项目管理功能完成报告.md"
    ]
    
    print("🗑️  清理冗余文件...")
    for file_name in redundant_files:
        file_path = Path(file_name)
        if file_path.exists():
            try:
                file_path.unlink()
                print(f"   ✓ 删除: {file_name}")
            except Exception as e:
                print(f"   ✗ 删除失败: {file_name} - {e}")
    
    # 重命名README_NEW.md为README.md
    if Path("README_NEW.md").exists():
        Path("README_NEW.md").rename("README.md")
        print("   ✓ 重命名: README_NEW.md -> README.md")


def cleanup_empty_directories():
    """清理空目录"""
    
    empty_dirs = [
        "docs/api",
        "docs/developer_guide", 
        "docs/examples",
        "docs/user_guide",
        "data/materials",
        "data/models", 
        "data/results",
        "data/templates",
        "tests/unit",
        "tests/integration",
        "tests/system",
        "deployment/docker",
        "deployment/ansible", 
        "deployment/kubernetes",
        "scripts"
    ]
    
    print("\n📁 清理空目录...")
    for dir_name in empty_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            try:
                # 检查目录是否为空
                if not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    print(f"   ✓ 删除空目录: {dir_name}")
                else:
                    print(f"   - 保留非空目录: {dir_name}")
            except Exception as e:
                print(f"   ✗ 删除失败: {dir_name} - {e}")


def optimize_project_structure():
    """优化项目结构"""
    
    print("\n🏗️  优化项目结构...")
    
    # 创建优化后的目录结构
    new_dirs = [
        "assets/icons",
        "assets/images", 
        "assets/styles",
        "examples",
        "tools"
    ]
    
    for dir_name in new_dirs:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✓ 创建目录: {dir_name}")
    
    # 移动工具脚本到tools目录
    tool_files = [
        "setup_environment.sh"
    ]
    
    for tool_file in tool_files:
        src_path = Path(tool_file)
        dst_path = Path("tools") / tool_file
        if src_path.exists() and not dst_path.exists():
            try:
                shutil.move(str(src_path), str(dst_path))
                print(f"   ✓ 移动: {tool_file} -> tools/")
            except Exception as e:
                print(f"   ✗ 移动失败: {tool_file} - {e}")


def create_optimized_readme():
    """创建优化后的README"""
    
    readme_content = """# 激光毁伤仿真系统

基于PyQt5的工业级激光毁伤仿真分析系统。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- PyQt5
- matplotlib, numpy, pandas

### 安装和运行
```bash
# 1. 创建虚拟环境
python -m venv laser_simulation_env
source laser_simulation_env/bin/activate  # Linux/macOS
# laser_simulation_env\\Scripts\\activate  # Windows

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
python run_gui.py
```

## 📋 主要功能

- **仿真设置**: 激光参数、材料属性、环境条件配置
- **结果分析**: 2D/3D可视化、数据分析、统计报告
- **报告生成**: 自动化报告生成，支持多种格式
- **效果评估**: 毁伤效果评估和对比分析

## 🏗️ 项目结构

```
laser-damage-simulation/
├── src/laser_damage/          # 源代码
│   ├── gui/                   # GUI界面
│   ├── core/                  # 核心功能
│   ├── laser_damage/          # 激光毁伤模块
│   └── utils/                 # 工具模块
├── assets/                    # 资源文件
├── examples/                  # 示例文件
├── tools/                     # 工具脚本
├── requirements.txt           # 依赖列表
└── run_gui.py                # 启动脚本
```

## 📖 使用说明

1. **启动应用**: 运行 `python run_gui.py`
2. **项目管理**: 通过左侧项目资源管理器管理项目
3. **仿真设置**: 在"仿真设置"标签页配置参数
4. **运行仿真**: 点击工具栏"运行"按钮或按F5
5. **查看结果**: 在"结果分析"标签页查看仿真结果
6. **生成报告**: 在"报告生成"标签页创建分析报告

## 🔧 开发

### 代码规范
- 使用Black进行代码格式化
- 遵循PEP 8编码规范
- 添加类型注解

### 测试
```bash
pytest tests/
```

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request。
"""
    
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("\n📝 创建优化后的README.md")


def create_gitignore():
    """创建优化后的.gitignore"""
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
laser_simulation_env/
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
data/results/
*.log
*.tmp
config/local_settings.py

# ANSYS files
*.db
*.rst
*.rth
"""
    
    with open(".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    
    print("📝 创建优化后的.gitignore")


def main():
    """主函数"""
    print("🧹 开始项目清理和优化...")
    print("=" * 50)
    
    # 执行清理步骤
    cleanup_redundant_files()
    cleanup_empty_directories() 
    optimize_project_structure()
    create_optimized_readme()
    create_gitignore()
    
    print("\n" + "=" * 50)
    print("✅ 项目清理和优化完成!")
    print("\n📋 优化后的项目结构:")
    print("- 移除了冗余的文档和测试文件")
    print("- 优化了目录结构")
    print("- 创建了新的README和.gitignore")
    print("- 工具脚本移动到tools目录")
    print("\n🚀 现在可以使用优化后的GUI:")
    print("python run_gui.py")


if __name__ == "__main__":
    main()

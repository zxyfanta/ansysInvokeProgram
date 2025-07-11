# 激光毁伤仿真系统

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
# laser_simulation_env\Scripts\activate  # Windows

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

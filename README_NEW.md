# 激光毁伤仿真系统

基于ANSYS的激光毁伤仿真分析系统，提供完整的激光与材料相互作用仿真、分析和评估功能。

## 🎯 主要功能

- **激光毁伤仿真**: 基于ANSYS的高精度激光与材料相互作用仿真
- **热传导分析**: 激光加热过程的瞬态热传导计算
- **应力应变分析**: 热应力和结构响应分析
- **毁伤效果评估**: 多维度毁伤指标评估和可视化
- **可视化结果展示**: 2D/3D结果可视化和交互式分析
- **自动化报告生成**: 专业的仿真分析报告自动生成

## 🖥️ GUI界面

系统提供直观的图形用户界面，包含四大功能模块：

1. **仿真设置** - 激光参数、材料参数、环境参数配置
2. **分析结果** - 2D/3D可视化、数据分析、结果展示  
3. **报告生成** - 报告配置、模板选择、格式输出
4. **效果评估** - 毁伤评估、效应分析、对比分析

## 🛠️ 技术栈

- **仿真引擎**: ANSYS MAPDL (可选)
- **编程语言**: Python 3.8+
- **GUI框架**: PyQt5
- **科学计算**: NumPy, SciPy, Pandas
- **可视化**: Matplotlib, PyVista, VTK
- **报告生成**: ReportLab, Jinja2
- **数据处理**: h5py, netCDF4, openpyxl

## 🚀 快速开始

### 方法一：使用自动化脚本（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd laser-damage-simulation

# 运行自动化设置脚本
./setup_environment.sh

# 启动GUI
./start_gui.sh
```

### 方法二：手动设置

```bash
# 1. 创建虚拟环境
python3 -m venv laser_simulation_env

# 2. 激活虚拟环境
source laser_simulation_env/bin/activate  # macOS/Linux
# laser_simulation_env\Scripts\activate   # Windows

# 3. 升级pip并安装依赖
pip install --upgrade pip
pip install -r requirements.txt

# 4. 启动GUI
python run_gui.py
```

## 📋 环境要求

### 系统要求
- **操作系统**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python版本**: 3.8+ (推荐3.9+)
- **内存**: 8GB+ RAM (推荐16GB+)
- **显卡**: 支持OpenGL 3.3+的显卡

### 可选组件
- **ANSYS**: 2021 R1+ (用于真实仿真计算)
- **Git**: 用于版本控制
- **IDE**: VS Code, PyCharm等 (开发用)

## 📁 项目结构

```
laser-damage-simulation/
├── laser_simulation_env/      # Python虚拟环境 (不纳入Git)
├── src/                       # 源代码
│   └── laser_damage/         # 主要模块
│       ├── gui/              # GUI界面模块
│       ├── core/             # 核心功能模块
│       ├── laser_damage/     # 激光毁伤仿真
│       ├── post_damage/      # 后效分析
│       ├── data_analysis/    # 数据分析
│       ├── damage_assessment/# 毁伤评估
│       └── utils/            # 工具模块
├── tests/                    # 测试文件
├── docs/                     # 文档
├── data/                     # 数据文件
│   ├── models/              # 3D模型文件
│   ├── materials/           # 材料数据
│   ├── templates/           # 模板文件
│   └── results/             # 仿真结果 (不纳入Git)
├── config/                   # 配置文件
├── scripts/                  # 脚本文件
├── requirements.txt          # Python依赖
├── setup_environment.sh      # 环境设置脚本
├── run_gui.py               # GUI启动脚本
├── test_gui.py              # GUI测试脚本
└── .gitignore               # Git忽略文件
```

## 🔧 开发指南

### 环境设置
```bash
# 克隆项目
git clone <repository-url>
cd laser-damage-simulation

# 自动化环境设置
./setup_environment.sh

# 手动激活环境
source laser_simulation_env/bin/activate
```

### 代码规范
- 使用Black进行代码格式化
- 使用Flake8进行代码检查
- 使用MyPy进行类型检查
- 遵循PEP 8编码规范

### 测试
```bash
# 运行GUI测试
python test_gui.py

# 运行单元测试
pytest tests/

# 运行覆盖率测试
pytest --cov=src tests/
```

## 📖 使用说明

### 启动应用
```bash
# 激活虚拟环境
source laser_simulation_env/bin/activate

# 启动GUI
python run_gui.py

# 或使用快捷脚本
./start_gui.sh
```

### 基本操作流程
1. **仿真设置**: 配置激光参数、材料属性、环境条件
2. **运行仿真**: 启动仿真计算（当前为模拟模式）
3. **结果分析**: 查看温度场、应力场等可视化结果
4. **效果评估**: 进行毁伤效果评估和分析
5. **报告生成**: 生成专业的仿真分析报告

### 功能特性
- **参数配置**: 直观的参数设置界面
- **实时预览**: 参数变化的实时反馈
- **多种可视化**: 2D等值线图、3D表面图、雷达图等
- **数据导出**: 支持PNG、CSV、PDF等格式
- **报告定制**: 多种报告模板和样式选择

## 🔍 故障排除

### 常见问题

1. **GUI无法启动**
   ```bash
   # 检查Python版本
   python --version
   
   # 检查虚拟环境
   which python
   
   # 重新安装依赖
   pip install -r requirements.txt
   ```

2. **中文字体显示问题**
   - 图表标签已改为英文避免字体问题
   - 如需中文显示，请安装中文字体

3. **ANSYS集成问题**
   - 当前版本使用模拟模式
   - 真实ANSYS集成需要有效许可证

### 获取帮助
- 查看详细文档: `docs/`
- 运行测试脚本: `python test_gui.py`
- 检查系统状态: `python simple_check.py`

## 📄 许可证

本项目采用 MIT 许可证。详情请参考 [LICENSE](LICENSE) 文件。

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目主页: [Project URL]

---

**最后更新**: 2024-01-01  
**版本**: v1.0.0  
**状态**: 活跃开发中

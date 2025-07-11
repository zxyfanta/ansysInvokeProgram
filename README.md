# 激光毁伤仿真系统

基于ANSYS 2021 R1的激光毁伤仿真系统，提供完整的激光武器毁伤效果仿真、后效分析、数据处理和效果评估功能。

## 🚀 项目特性

- **完整的仿真工作流程**: 从激光毁伤仿真到后效分析的完整链条
- **基于ANSYS 2021 R1**: 利用业界领先的仿真软件进行精确计算
- **模块化架构**: 清晰的模块划分，便于维护和扩展
- **丰富的可视化**: 温度场、应力场、毁伤分布等多种可视化效果
- **自动化报告生成**: 支持PDF、HTML、Word等多种格式的报告输出
- **用户友好界面**: 基于PyQt5的图形用户界面

## 📋 系统要求

### 硬件要求
- **CPU**: Intel i7-12700K 或 AMD Ryzen 7 5800X (推荐)
- **内存**: 32GB DDR4 (推荐，最低16GB)
- **存储**: 1TB NVMe SSD (推荐)
- **GPU**: NVIDIA RTX 3070 或更高 (可选，用于加速)

### 软件要求
- **操作系统**: Windows 10/11 (64位) 或 Linux RHEL/CentOS 8+
- **ANSYS**: ANSYS 2021 R1 (必需)
- **Python**: Python 3.8+ (推荐3.8-3.10)

## 🛠️ 安装指南

### 1. 环境准备

```bash
# 克隆项目
git clone https://github.com/company/laser-damage-simulation.git
cd laser-damage-simulation

# 创建虚拟环境
conda create -n laser_simulation python=3.8
conda activate laser_simulation

# 或使用venv
python -m venv laser_simulation_env
source laser_simulation_env/bin/activate  # Linux
# laser_simulation_env\Scripts\activate  # Windows
```

### 2. 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 开发模式安装
pip install -e .
```

### 3. 配置ANSYS环境

```bash
# 设置环境变量 (Linux)
export ANSYS_ROOT="/opt/ansys_inc/v211"
export ANSYSLMD_LICENSE_FILE="1055@license-server.company.com"

# Windows PowerShell
$env:ANSYS_ROOT="C:\Program Files\ANSYS Inc\v211"
$env:ANSYSLMD_LICENSE_FILE="1055@license-server.company.com"
```

### 4. 验证安装

```bash
# 运行环境验证脚本
python verify_environment.py

# 运行测试
pytest tests/
```

## 🎯 快速开始

### 命令行使用

```python
from laser_damage import LaserDamageSimulator

# 创建仿真器实例
simulator = LaserDamageSimulator()

# 配置仿真参数
config = {
    "model_path": "data/models/sample_plate.step",
    "laser_parameters": {
        "power": 1000.0,        # 激光功率 (W)
        "wavelength": 1064.0,   # 波长 (nm)
        "beam_diameter": 5.0,   # 光斑直径 (mm)
        "pulse_duration": 0.001 # 脉冲持续时间 (s)
    },
    "material_parameters": {
        "name": "aluminum_6061",
        "thermal_conductivity": 167.0,
        "specific_heat": 896.0,
        "density": 2700.0,
        "melting_point": 933.0,
        "absorption_coefficient": 0.1
    }
}

# 运行仿真
result = simulator.run_simulation(config)

# 查看结果
print(f"最高温度: {result.max_temperature} K")
print(f"最大应力: {result.max_stress} Pa")
```

### GUI使用

```bash
# 启动图形界面
laser-gui

# 或直接运行
python src/laser_damage/gui/main_window.py
```

## 📁 项目结构

```
laser_damage_simulation/
├── README.md                    # 项目说明
├── requirements.txt             # 依赖列表
├── setup.py                     # 安装脚本
├── config/                      # 配置文件
│   └── settings.py
├── src/laser_damage/            # 源代码
│   ├── core/                    # 核心模块
│   ├── laser_damage/            # 激光毁伤仿真
│   ├── post_damage/             # 毁伤后效分析
│   ├── data_analysis/           # 数据分析报告
│   ├── damage_assessment/       # 毁伤效果评估
│   ├── gui/                     # 图形界面
│   └── utils/                   # 工具函数
├── tests/                       # 测试代码
├── data/                        # 数据文件
│   ├── models/                  # 3D模型
│   ├── materials/               # 材料数据
│   ├── templates/               # 模板文件
│   └── results/                 # 仿真结果
├── docs/                        # 文档
└── deployment/                  # 部署配置
```

## 🔧 核心模块

### 1. 激光毁伤仿真模块
- 热传导分析
- 热应力计算
- 温度场分布
- 应力场分布

### 2. 毁伤后效分析模块
- 飞行状态仿真
- 气动性能分析
- 结构完整性评估

### 3. 数据分析与报告生成模块
- 结果数据提取
- 统计分析
- 图表生成
- 报告自动生成

### 4. 毁伤效果评估模块
- 毁伤程度量化
- 多维度效果分析
- 综合评估报告

## 📊 使用示例

### 基础仿真示例

```python
# 完整的仿真工作流程示例
from laser_damage import (
    LaserDamageSimulator,
    PostDamageAnalyzer, 
    DataAnalysisReporter,
    DamageEffectAssessor
)

# 1. 激光毁伤仿真
laser_sim = LaserDamageSimulator()
damage_result = laser_sim.run_simulation(laser_config)

# 2. 后效分析
post_analyzer = PostDamageAnalyzer()
post_result = post_analyzer.analyze_post_damage(damage_result)

# 3. 数据分析
data_reporter = DataAnalysisReporter()
analysis_report = data_reporter.generate_analysis_report([damage_result, post_result])

# 4. 效果评估
assessor = DamageEffectAssessor()
assessment = assessor.assess_damage_effect(analysis_report)

print(f"毁伤等级: {assessment.damage_level}")
print(f"报告路径: {assessment.report_file_path}")
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=src/laser_damage --cov-report=html
```

## 📚 文档

- [用户手册](docs/user_guide/README.md)
- [开发者指南](docs/developer_guide/README.md)
- [API文档](docs/api/README.md)
- [环境搭建指南](环境搭建指南.md)
- [开发方案设计](开发方案设计文档.md)

## 🤝 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与联系

- **项目主页**: https://github.com/company/laser-damage-simulation
- **问题反馈**: https://github.com/company/laser-damage-simulation/issues
- **邮箱**: dev-team@company.com
- **文档**: https://laser-damage-simulation.readthedocs.io

## 🙏 致谢

- ANSYS Inc. 提供的优秀仿真软件
- Python科学计算社区的开源贡献
- 所有参与项目开发的团队成员

---

**版本**: v1.0.0  
**最后更新**: 2024-01-01

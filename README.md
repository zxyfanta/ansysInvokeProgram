# 激光毁伤效能分析软件

基于ANSYS 2021 R1的激光毁伤效能分析软件，提供完整的激光毁伤仿真、毁伤后效分析、数据分析和效果评估功能。

## 🎯 项目特点

- **激光毁伤仿真**: 基于PyANSYS的热损伤、热应力计算
- **毁伤后效分析**: 飞行模拟、气动力计算等毁伤后效分析
- **数据分析**: 完整的数据提取、图表生成、报告输出
- **效果评估**: 激光武器毁伤能力评估
- **统一界面**: 专业的军用软件GUI界面

## 🏗️ 项目结构

```
laser_damage_analysis/
├── main.py                    # 主程序入口
├── config/                    # 配置模块
│   ├── settings.py           # 系统配置
│   ├── ansys_config.py       # ANSYS配置
│   └── material_database.py  # 材料数据库
├── src/                      # 源代码
│   ├── core/                 # 核心模块
│   ├── laser_damage/         # 激光毁伤仿真模块
│   ├── post_damage/          # 毁伤后效分析模块
│   ├── data_analysis/        # 数据分析与报告生成模块
│   ├── damage_assessment/    # 激光毁伤效果评估模块
│   ├── gui/                  # 图形用户界面
│   └── utils/                # 工具模块
├── tests/                    # 测试代码
├── docs/                     # 文档
├── examples/                 # 示例文件
├── requirements.txt          # Python依赖
└── environment.yml          # Conda环境配置
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- ANSYS 2021 R1 (已安装在 D:/Program Files/ANSYS Inc/)
- Conda环境管理器

### 安装步骤

1. **激活conda环境**
   ```bash
   conda activate jg
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **验证安装**
   ```bash
   python examples/fluent_test.py
   ```

### 运行示例

```bash
# 启动GUI界面
python main.py --gui

# 运行命令行仿真
python main.py --cli

# 检查环境配置
python main.py --check
```

## 📖 使用指南

### 基础飞机建模

1. **运行aircraft_demo.py**
   - 自动创建飞机几何模型
   - 3D可视化显示
   - 保存STL文件

2. **模型特点**
   - 机身: 椭圆柱体，长15m
   - 机翼: 后掠翼设计，翼展16m
   - 尾翼: 垂直和水平尾翼

### Fluent仿真流程

1. **运行aircraft_fluent_simulation.py**
   - 自动几何创建（支持备用方案）
   - Fluent会话启动
   - 网格导入和处理
   - 基础仿真设置

2. **仿真参数**
   - 求解器: 压力基稳态
   - 湍流模型: k-epsilon标准
   - 流体: 空气（标准大气条件）

## 🔧 技术特点

### PyANSYS集成

- **ansys-fluent-core**: Fluent Python接口
- **PyVista**: 3D可视化和几何处理
- **自动检测**: ANSYS安装路径自动识别
- **错误处理**: 完善的异常处理和备用方案

### 建模能力

- **参数化设计**: 所有几何参数可调整
- **模块化构建**: 各部件独立创建后组装
- **多格式支持**: STL, PLY, VTK等
- **质量检查**: 自动几何验证和清理

## 📊 项目成果

### 成功案例

- ✅ 飞机模型创建: 88个点，164个单元
- ✅ 体积: 69.90 m³，表面积: 265.91 m²
- ✅ Fluent集成: 成功导入和显示
- ✅ 可视化: 完整的3D交互显示

### 测试结果

- ✅ Fluent功能测试: 5/5 通过
- ✅ Workbench测试: 2/3 通过
- ✅ 几何建模: 100% 成功率
- ✅ 文件导出: 支持多种格式

## 🛠️ 开发指南

### 添加新几何

1. 在`aircraft_demo.py`中添加新的几何创建方法
2. 更新`build_complete_aircraft()`方法
3. 测试几何质量和可视化

### 扩展仿真功能

1. 修改`aircraft_fluent_simulation.py`
2. 添加新的仿真参数设置
3. 更新结果处理和可视化

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系信息

- 项目主页: [GitHub Repository](https://github.com/zxyfanta/ansysInvokeProgram)
- 问题反馈: [Issues](https://github.com/zxyfanta/ansysInvokeProgram/issues)

## 🙏 致谢

感谢以下技术的支持：
- [PyANSYS](https://docs.pyansys.com/)
- [PyVista](https://pyvista.org/)
- [ANSYS Fluent](https://www.ansys.com/products/fluids/ansys-fluent)

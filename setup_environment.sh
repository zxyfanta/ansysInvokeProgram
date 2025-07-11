#!/bin/bash

# 激光毁伤仿真系统环境设置脚本
# 使用方法: ./setup_environment.sh

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "找到Python $PYTHON_VERSION"
        
        # 检查版本是否满足要求 (3.8+)
        MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]; then
            print_success "Python版本满足要求 (3.8+)"
        else
            print_error "Python版本过低，需要3.8或更高版本"
            exit 1
        fi
    else
        print_error "未找到Python3，请先安装Python"
        exit 1
    fi
}

# 创建虚拟环境
create_venv() {
    print_info "创建Python虚拟环境..."
    
    if [ -d "laser_simulation_env" ]; then
        print_warning "虚拟环境已存在，是否重新创建? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            print_info "删除现有虚拟环境..."
            rm -rf laser_simulation_env
        else
            print_info "使用现有虚拟环境"
            return 0
        fi
    fi
    
    python3 -m venv laser_simulation_env
    print_success "虚拟环境创建完成"
}

# 激活虚拟环境并安装依赖
install_dependencies() {
    print_info "激活虚拟环境并安装依赖..."
    
    # 激活虚拟环境
    source laser_simulation_env/bin/activate
    
    # 升级pip
    print_info "升级pip..."
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f "requirements.txt" ]; then
        print_info "安装项目依赖..."
        pip install -r requirements.txt
        print_success "依赖安装完成"
    else
        print_error "未找到requirements.txt文件"
        exit 1
    fi
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    source laser_simulation_env/bin/activate
    
    # 检查关键包
    python -c "import PyQt5; print('✓ PyQt5')" || print_error "PyQt5导入失败"
    python -c "import matplotlib; print('✓ matplotlib')" || print_error "matplotlib导入失败"
    python -c "import numpy; print('✓ numpy')" || print_error "numpy导入失败"
    python -c "import pandas; print('✓ pandas')" || print_error "pandas导入失败"
    
    print_success "关键包验证完成"
}

# 创建启动脚本
create_launcher() {
    print_info "创建启动脚本..."
    
    cat > start_gui.sh << 'EOF'
#!/bin/bash
# 激光毁伤仿真系统GUI启动脚本

cd "$(dirname "$0")"
source laser_simulation_env/bin/activate
python run_gui.py
EOF
    
    chmod +x start_gui.sh
    print_success "启动脚本创建完成: start_gui.sh"
}

# 显示使用说明
show_usage() {
    echo ""
    echo "=============================================="
    echo "  激光毁伤仿真系统环境设置完成！"
    echo "=============================================="
    echo ""
    echo "使用方法:"
    echo ""
    echo "1. 激活虚拟环境:"
    echo "   source laser_simulation_env/bin/activate"
    echo ""
    echo "2. 启动GUI:"
    echo "   python run_gui.py"
    echo ""
    echo "3. 或使用快捷启动脚本:"
    echo "   ./start_gui.sh"
    echo ""
    echo "4. 运行测试:"
    echo "   python test_gui.py"
    echo ""
    echo "5. 检查状态:"
    echo "   python simple_check.py"
    echo ""
    echo "6. 停用虚拟环境:"
    echo "   deactivate"
    echo ""
    echo "=============================================="
    echo "环境信息:"
    echo "- 虚拟环境: ./laser_simulation_env/"
    echo "- Python版本: $(python3 --version)"
    echo "- 项目目录: $(pwd)"
    echo "=============================================="
}

# 主函数
main() {
    echo "=============================================="
    echo "  激光毁伤仿真系统环境设置脚本"
    echo "=============================================="
    echo ""
    
    # 检查是否在项目根目录
    if [ ! -f "run_gui.py" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行设置步骤
    check_python
    create_venv
    install_dependencies
    verify_installation
    create_launcher
    show_usage
    
    print_success "环境设置完成！"
}

# 错误处理
trap 'print_error "脚本执行失败，请检查错误信息"' ERR

# 运行主函数
main "$@"

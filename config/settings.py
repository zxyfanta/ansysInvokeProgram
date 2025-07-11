"""
系统配置文件

定义系统的各种配置参数和常量。
"""

import os
from pathlib import Path

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent
SRC_DIR = BASE_DIR / "src"
DATA_DIR = BASE_DIR / "data"
RESULTS_DIR = DATA_DIR / "results"
MODELS_DIR = DATA_DIR / "models"
TEMPLATES_DIR = DATA_DIR / "templates"
MATERIALS_DIR = DATA_DIR / "materials"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"

# 确保目录存在
for directory in [DATA_DIR, RESULTS_DIR, MODELS_DIR, TEMPLATES_DIR, MATERIALS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ANSYS集成配置
ANSYS_CONFIG = {
    'ANSYS_ROOT': os.environ.get('ANSYS_ROOT', '/opt/ansys_inc/v211'),
    'LICENSE_SERVER': os.environ.get('ANSYSLMD_LICENSE_FILE', '1055@localhost'),
    'WORKING_DIRECTORY': str(RESULTS_DIR / "ansys_working"),
    'CLEANUP_TEMP_FILES': True,
    'MAX_SIMULATION_TIME': 3600,  # 最大仿真时间(秒)
    'MEMORY_LIMIT': '16GB',
    'CPU_CORES': 8,
    'SOLVER_PRECISION': 'double',
}

# 数据库配置
DATABASE_CONFIG = {
    'ENGINE': 'sqlite',
    'NAME': str(DATA_DIR / 'simulation_database.db'),
    'BACKUP_ENABLED': True,
    'BACKUP_INTERVAL': 3600,  # 备份间隔(秒)
    'CONNECTION_TIMEOUT': 30,
    'MAX_CONNECTIONS': 10,
}

# 日志配置
LOGGING_CONFIG = {
    'VERSION': 1,
    'DISABLE_EXISTING_LOGGERS': False,
    'FORMATTERS': {
        'STANDARD': {
            'FORMAT': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            'DATEFMT': '%Y-%m-%d %H:%M:%S'
        },
        'DETAILED': {
            'FORMAT': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s',
            'DATEFMT': '%Y-%m-%d %H:%M:%S'
        },
    },
    'HANDLERS': {
        'CONSOLE': {
            'LEVEL': 'INFO',
            'CLASS': 'logging.StreamHandler',
            'FORMATTER': 'STANDARD',
        },
        'FILE': {
            'LEVEL': 'DEBUG',
            'CLASS': 'logging.handlers.RotatingFileHandler',
            'FILENAME': str(LOGS_DIR / 'application.log'),
            'FORMATTER': 'DETAILED',
            'MAX_BYTES': 10485760,  # 10MB
            'BACKUP_COUNT': 5,
        },
        'ERROR_FILE': {
            'LEVEL': 'ERROR',
            'CLASS': 'logging.handlers.RotatingFileHandler',
            'FILENAME': str(LOGS_DIR / 'error.log'),
            'FORMATTER': 'DETAILED',
            'MAX_BYTES': 10485760,  # 10MB
            'BACKUP_COUNT': 3,
        },
    },
    'LOGGERS': {
        '': {
            'HANDLERS': ['CONSOLE', 'FILE', 'ERROR_FILE'],
            'LEVEL': 'DEBUG',
            'PROPAGATE': False
        },
        'laser_damage': {
            'HANDLERS': ['CONSOLE', 'FILE'],
            'LEVEL': 'DEBUG',
            'PROPAGATE': False
        },
        'ansys': {
            'HANDLERS': ['FILE'],
            'LEVEL': 'INFO',
            'PROPAGATE': False
        },
    }
}

# 仿真默认参数
SIMULATION_DEFAULTS = {
    'UNITS': {
        'LENGTH': 'mm',
        'TIME': 's',
        'TEMPERATURE': 'K',
        'FORCE': 'N',
        'PRESSURE': 'Pa',
        'ENERGY': 'J',
    },
    
    'CONVERGENCE_CRITERIA': {
        'THERMAL': {
            'TEMPERATURE_TOLERANCE': 1e-6,
            'HEAT_FLUX_TOLERANCE': 1e-6,
            'MAX_ITERATIONS': 1000,
        },
        'STRUCTURAL': {
            'DISPLACEMENT_TOLERANCE': 1e-6,
            'FORCE_TOLERANCE': 1e-6,
            'MAX_ITERATIONS': 1000,
        },
        'FLUID': {
            'VELOCITY_TOLERANCE': 1e-6,
            'PRESSURE_TOLERANCE': 1e-6,
            'MAX_ITERATIONS': 2000,
        },
    },
    
    'MESH_SETTINGS': {
        'DEFAULT_ELEMENT_SIZE': 1.0,  # mm
        'MIN_ELEMENT_SIZE': 0.1,      # mm
        'MAX_ELEMENT_SIZE': 10.0,     # mm
        'GROWTH_RATE': 1.2,
        'CURVATURE_NORMAL_ANGLE': 18.0,  # degrees
    },
}

# 材料数据库配置
MATERIALS_CONFIG = {
    'DATABASE_FILE': str(MATERIALS_DIR / 'material_database.json'),
    'DEFAULT_MATERIALS': [
        'aluminum_6061',
        'steel_304',
        'titanium_ti6al4v',
        'carbon_fiber',
        'copper',
    ],
}

# 激光参数范围
LASER_PARAMETER_RANGES = {
    'POWER': {
        'MIN': 1.0,      # W
        'MAX': 100000.0, # W
        'DEFAULT': 1000.0,
    },
    'WAVELENGTH': {
        'MIN': 200.0,    # nm
        'MAX': 12000.0,  # nm
        'DEFAULT': 1064.0,
    },
    'BEAM_DIAMETER': {
        'MIN': 0.1,      # mm
        'MAX': 100.0,    # mm
        'DEFAULT': 5.0,
    },
    'PULSE_DURATION': {
        'MIN': 1e-12,    # s (飞秒)
        'MAX': 1.0,      # s
        'DEFAULT': 0.001,
    },
}

# GUI配置
GUI_CONFIG = {
    'WINDOW_SIZE': (1200, 800),
    'MIN_WINDOW_SIZE': (800, 600),
    'THEME': 'default',
    'FONT_SIZE': 10,
    'CHART_DPI': 100,
    'AUTO_SAVE_INTERVAL': 300,  # 秒
}

# 报告生成配置
REPORT_CONFIG = {
    'TEMPLATE_DIR': str(TEMPLATES_DIR / 'report_templates'),
    'OUTPUT_FORMATS': ['pdf', 'html', 'docx'],
    'DEFAULT_FORMAT': 'pdf',
    'CHART_FORMAT': 'png',
    'CHART_DPI': 300,
    'PAGE_SIZE': 'A4',
    'MARGINS': {
        'TOP': 25,    # mm
        'BOTTOM': 25, # mm
        'LEFT': 25,   # mm
        'RIGHT': 25,  # mm
    },
}

# 性能监控配置
PERFORMANCE_CONFIG = {
    'ENABLE_PROFILING': False,
    'MEMORY_LIMIT_GB': 16,
    'CPU_USAGE_THRESHOLD': 90,  # %
    'DISK_USAGE_THRESHOLD': 85, # %
    'MONITORING_INTERVAL': 60,  # 秒
}

# 安全配置
SECURITY_CONFIG = {
    'ENABLE_FILE_VALIDATION': True,
    'ALLOWED_MODEL_EXTENSIONS': ['.step', '.stp', '.iges', '.igs', '.sat', '.x_t'],
    'MAX_FILE_SIZE_MB': 1000,
    'TEMP_FILE_CLEANUP': True,
    'BACKUP_ENCRYPTION': False,
}

# 网络配置
NETWORK_CONFIG = {
    'LICENSE_SERVER_TIMEOUT': 30,  # 秒
    'RETRY_ATTEMPTS': 3,
    'RETRY_DELAY': 5,  # 秒
    'PROXY_ENABLED': False,
    'PROXY_HOST': '',
    'PROXY_PORT': 8080,
}

# 开发配置
DEVELOPMENT_CONFIG = {
    'DEBUG_MODE': os.environ.get('DEBUG', 'False').lower() == 'true',
    'ENABLE_TESTING': True,
    'MOCK_ANSYS': os.environ.get('MOCK_ANSYS', 'False').lower() == 'true',
    'PROFILE_PERFORMANCE': False,
    'VERBOSE_LOGGING': False,
}

# 导出配置字典
CONFIG = {
    'BASE_DIR': BASE_DIR,
    'DATA_DIR': DATA_DIR,
    'ANSYS': ANSYS_CONFIG,
    'DATABASE': DATABASE_CONFIG,
    'LOGGING': LOGGING_CONFIG,
    'SIMULATION': SIMULATION_DEFAULTS,
    'MATERIALS': MATERIALS_CONFIG,
    'LASER_RANGES': LASER_PARAMETER_RANGES,
    'GUI': GUI_CONFIG,
    'REPORT': REPORT_CONFIG,
    'PERFORMANCE': PERFORMANCE_CONFIG,
    'SECURITY': SECURITY_CONFIG,
    'NETWORK': NETWORK_CONFIG,
    'DEVELOPMENT': DEVELOPMENT_CONFIG,
}

def get_config(key: str, default=None):
    """
    获取配置值
    
    Args:
        key: 配置键，支持点号分隔的嵌套键
        default: 默认值
        
    Returns:
        配置值
    """
    keys = key.split('.')
    value = CONFIG
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value

def update_config(key: str, value):
    """
    更新配置值
    
    Args:
        key: 配置键
        value: 新值
    """
    keys = key.split('.')
    config = CONFIG
    
    for k in keys[:-1]:
        if k not in config:
            config[k] = {}
        config = config[k]
    
    config[keys[-1]] = value

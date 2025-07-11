#!/usr/bin/env python3
"""
激光毁伤仿真系统安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="laser-damage-simulation",
    version="1.0.0",
    author="激光毁伤仿真系统开发团队",
    author_email="dev-team@company.com",
    description="基于ANSYS 2021 R1的激光毁伤仿真系统",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/company/laser-damage-simulation",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "laser-simulation=laser_damage.cli:main",
            "laser-gui=laser_damage.gui.main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "laser_damage": [
            "data/templates/*.json",
            "data/materials/*.json",
            "config/*.yaml",
        ],
    },
    zip_safe=False,
)

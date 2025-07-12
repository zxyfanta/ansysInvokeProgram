"""
数据分析 - 图表生成器

生成各种类型的分析图表。
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import seaborn as sns
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import warnings

# 设置matplotlib中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 忽略matplotlib警告
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

class ChartGenerator:
    """图表生成器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 设置图表样式
        self.style_config = {
            'figure_size': (12, 8),
            'dpi': 300,
            'color_palette': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'],
            'grid_alpha': 0.3,
            'line_width': 2,
            'marker_size': 6
        }
        
        # 设置seaborn样式
        sns.set_style("whitegrid")
        sns.set_palette(self.style_config['color_palette'])
    
    def generate_damage_analysis_charts(self, damage_data: Dict, output_dir: str) -> List[str]:
        """生成毁伤分析图表"""
        chart_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. 温度分布图
            if 'temperature_distribution' in damage_data:
                temp_chart = self._create_temperature_distribution_chart(
                    damage_data['temperature_distribution'],
                    str(output_path / "temperature_distribution.png")
                )
                if temp_chart:
                    chart_files.append(temp_chart)
            
            # 2. 应力分布图
            if 'stress_distribution' in damage_data:
                stress_chart = self._create_stress_distribution_chart(
                    damage_data['stress_distribution'],
                    str(output_path / "stress_distribution.png")
                )
                if stress_chart:
                    chart_files.append(stress_chart)
            
            # 3. 毁伤指标雷达图
            if 'damage_metrics' in damage_data:
                radar_chart = self._create_damage_metrics_radar(
                    damage_data['damage_metrics'],
                    str(output_path / "damage_metrics_radar.png")
                )
                if radar_chart:
                    chart_files.append(radar_chart)
            
            # 4. 毁伤区域分析饼图
            if 'damage_analysis' in damage_data:
                pie_chart = self._create_damage_region_pie(
                    damage_data['damage_analysis'],
                    str(output_path / "damage_region_pie.png")
                )
                if pie_chart:
                    chart_files.append(pie_chart)
            
            self.logger.info(f"生成了 {len(chart_files)} 个毁伤分析图表")
            return chart_files
            
        except Exception as e:
            self.logger.error(f"毁伤分析图表生成失败: {e}")
            return []
    
    def generate_trajectory_charts(self, trajectory_data: Dict, output_dir: str) -> List[str]:
        """生成轨迹分析图表"""
        chart_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. 3D轨迹图
            if 'time_series' in trajectory_data:
                trajectory_3d = self._create_3d_trajectory_chart(
                    trajectory_data['time_series'],
                    str(output_path / "trajectory_3d.png")
                )
                if trajectory_3d:
                    chart_files.append(trajectory_3d)
            
            # 2. 高度-时间图
            if 'time_series' in trajectory_data:
                altitude_chart = self._create_altitude_time_chart(
                    trajectory_data['time_series'],
                    str(output_path / "altitude_time.png")
                )
                if altitude_chart:
                    chart_files.append(altitude_chart)
            
            # 3. 速度-时间图
            if 'time_series' in trajectory_data:
                velocity_chart = self._create_velocity_time_chart(
                    trajectory_data['time_series'],
                    str(output_path / "velocity_time.png")
                )
                if velocity_chart:
                    chart_files.append(velocity_chart)
            
            # 4. 姿态角变化图
            if 'time_series' in trajectory_data:
                attitude_chart = self._create_attitude_chart(
                    trajectory_data['time_series'],
                    str(output_path / "attitude_angles.png")
                )
                if attitude_chart:
                    chart_files.append(attitude_chart)
            
            # 5. 飞行性能对比图
            if 'flight_performance' in trajectory_data:
                performance_chart = self._create_performance_bar_chart(
                    trajectory_data['flight_performance'],
                    str(output_path / "flight_performance.png")
                )
                if performance_chart:
                    chart_files.append(performance_chart)
            
            self.logger.info(f"生成了 {len(chart_files)} 个轨迹分析图表")
            return chart_files
            
        except Exception as e:
            self.logger.error(f"轨迹分析图表生成失败: {e}")
            return []
    
    def generate_comparison_charts(self, comparison_data: Dict, output_dir: str) -> List[str]:
        """生成对比分析图表"""
        chart_files = []
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            # 1. 气动力系数对比
            if 'aerodynamic_comparison' in comparison_data:
                aero_chart = self._create_aerodynamic_comparison_chart(
                    comparison_data['aerodynamic_comparison'],
                    str(output_path / "aerodynamic_comparison.png")
                )
                if aero_chart:
                    chart_files.append(aero_chart)
            
            # 2. 性能退化分析
            if 'performance_comparison' in comparison_data:
                degradation_chart = self._create_performance_degradation_chart(
                    comparison_data['performance_comparison'],
                    str(output_path / "performance_degradation.png")
                )
                if degradation_chart:
                    chart_files.append(degradation_chart)
            
            # 3. 轨迹偏差分析
            if 'trajectory_comparison' in comparison_data:
                deviation_chart = self._create_trajectory_deviation_chart(
                    comparison_data['trajectory_comparison'],
                    str(output_path / "trajectory_deviation.png")
                )
                if deviation_chart:
                    chart_files.append(deviation_chart)
            
            self.logger.info(f"生成了 {len(chart_files)} 个对比分析图表")
            return chart_files
            
        except Exception as e:
            self.logger.error(f"对比分析图表生成失败: {e}")
            return []
    
    def _create_temperature_distribution_chart(self, temp_data: Dict, output_file: str) -> Optional[str]:
        """创建温度分布图"""
        try:
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            histogram = temp_data['histogram']
            bins = temp_data['bins']
            
            # 绘制直方图
            ax.bar(bins[:-1], histogram, width=np.diff(bins), alpha=0.7, 
                   color=self.style_config['color_palette'][0], edgecolor='black')
            
            ax.set_xlabel('温度 (K)')
            ax.set_ylabel('频次')
            ax.set_title('温度场分布直方图')
            ax.grid(True, alpha=self.style_config['grid_alpha'])
            
            # 添加统计信息
            mean_temp = np.average(bins[:-1], weights=histogram)
            ax.axvline(mean_temp, color='red', linestyle='--', linewidth=2, label=f'平均温度: {mean_temp:.1f} K')
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"温度分布图创建失败: {e}")
            return None
    
    def _create_stress_distribution_chart(self, stress_data: Dict, output_file: str) -> Optional[str]:
        """创建应力分布图"""
        try:
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            histogram = stress_data['histogram']
            bins = stress_data['bins']
            
            # 绘制直方图
            ax.bar(bins[:-1], histogram, width=np.diff(bins), alpha=0.7,
                   color=self.style_config['color_palette'][1], edgecolor='black')
            
            ax.set_xlabel('应力 (Pa)')
            ax.set_ylabel('频次')
            ax.set_title('应力场分布直方图')
            ax.grid(True, alpha=self.style_config['grid_alpha'])
            
            # 添加统计信息
            mean_stress = np.average(bins[:-1], weights=histogram)
            ax.axvline(mean_stress, color='red', linestyle='--', linewidth=2, label=f'平均应力: {mean_stress:.0f} Pa')
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"应力分布图创建失败: {e}")
            return None
    
    def _create_damage_metrics_radar(self, metrics: Dict, output_file: str) -> Optional[str]:
        """创建毁伤指标雷达图"""
        try:
            # 准备数据
            labels = []
            values = []
            
            # 归一化指标值
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and value > 0:
                    labels.append(key.replace('_', ' ').title())
                    # 简单归一化到0-100范围
                    if 'temperature' in key.lower():
                        normalized_value = min(100, value / 1000 * 100)  # 假设1000K为满分
                    elif 'stress' in key.lower():
                        normalized_value = min(100, value / 1e9 * 100)   # 假设1GPa为满分
                    elif 'volume' in key.lower():
                        normalized_value = min(100, value / 0.001 * 100) # 假设0.001m³为满分
                    else:
                        normalized_value = min(100, value)
                    values.append(normalized_value)
            
            if not labels:
                return None
            
            # 创建雷达图
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            values += values[:1]  # 闭合图形
            angles += angles[:1]
            
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            ax.plot(angles, values, 'o-', linewidth=self.style_config['line_width'],
                    color=self.style_config['color_palette'][2])
            ax.fill(angles, values, alpha=0.25, color=self.style_config['color_palette'][2])
            
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels)
            ax.set_ylim(0, 100)
            ax.set_title('毁伤指标雷达图', size=16, pad=20)
            ax.grid(True)
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"毁伤指标雷达图创建失败: {e}")
            return None
    
    def _create_damage_region_pie(self, damage_analysis: Dict, output_file: str) -> Optional[str]:
        """创建毁伤区域饼图"""
        try:
            damaged_ratio = damage_analysis.get('damage_ratio', 0.0)
            undamaged_ratio = damage_analysis.get('undamaged_ratio', 1.0)
            
            labels = ['毁伤区域', '完好区域']
            sizes = [damaged_ratio * 100, undamaged_ratio * 100]
            colors = [self.style_config['color_palette'][3], self.style_config['color_palette'][4]]
            explode = (0.1, 0)  # 突出显示毁伤区域
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                             autopct='%1.1f%%', shadow=True, startangle=90)
            
            ax.set_title('毁伤区域分布', size=16)
            
            # 添加图例
            ax.legend(wedges, [f'{label}: {size:.1f}%' for label, size in zip(labels, sizes)],
                     title="区域分布", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"毁伤区域饼图创建失败: {e}")
            return None
    
    def _create_3d_trajectory_chart(self, time_series: Dict, output_file: str) -> Optional[str]:
        """创建3D轨迹图"""
        try:
            if 'time' not in time_series:
                return None
            
            time_data = time_series['time']
            
            # 构造3D轨迹数据（简化）
            x_data = np.array(time_data) * 100  # 假设X方向位移
            y_data = np.sin(np.array(time_data) * 0.1) * 50  # 假设Y方向位移
            z_data = time_series.get('altitude', np.array(time_data) * -10 + 10000)  # 高度数据
            
            fig = plt.figure(figsize=self.style_config['figure_size'])
            ax = fig.add_subplot(111, projection='3d')
            
            ax.plot(x_data, y_data, z_data, linewidth=self.style_config['line_width'],
                    color=self.style_config['color_palette'][0])
            
            ax.set_xlabel('X 位置 (m)')
            ax.set_ylabel('Y 位置 (m)')
            ax.set_zlabel('高度 (m)')
            ax.set_title('飞行轨迹 (3D)')
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"3D轨迹图创建失败: {e}")
            return None
    
    def _create_altitude_time_chart(self, time_series: Dict, output_file: str) -> Optional[str]:
        """创建高度-时间图"""
        try:
            time_data = time_series.get('time', [])
            altitude_data = time_series.get('altitude', [])
            
            if not time_data or not altitude_data:
                return None
            
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            ax.plot(time_data, altitude_data, linewidth=self.style_config['line_width'],
                    color=self.style_config['color_palette'][0], marker='o',
                    markersize=self.style_config['marker_size'], markevery=10)
            
            ax.set_xlabel('时间 (s)')
            ax.set_ylabel('高度 (m)')
            ax.set_title('高度随时间变化')
            ax.grid(True, alpha=self.style_config['grid_alpha'])
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"高度-时间图创建失败: {e}")
            return None
    
    def _create_velocity_time_chart(self, time_series: Dict, output_file: str) -> Optional[str]:
        """创建速度-时间图"""
        try:
            time_data = time_series.get('time', [])
            velocity_data = time_series.get('velocity', [])
            
            if not time_data or not velocity_data:
                return None
            
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            ax.plot(time_data, velocity_data, linewidth=self.style_config['line_width'],
                    color=self.style_config['color_palette'][1], marker='s',
                    markersize=self.style_config['marker_size'], markevery=10)
            
            ax.set_xlabel('时间 (s)')
            ax.set_ylabel('速度 (m/s)')
            ax.set_title('速度随时间变化')
            ax.grid(True, alpha=self.style_config['grid_alpha'])
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"速度-时间图创建失败: {e}")
            return None
    
    def _create_attitude_chart(self, time_series: Dict, output_file: str) -> Optional[str]:
        """创建姿态角变化图"""
        try:
            time_data = time_series.get('time', [])
            attitude_data = time_series.get('attitude', {})
            
            if not time_data or not attitude_data:
                return None
            
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            colors = self.style_config['color_palette'][:3]
            labels = ['俯仰角', '滚转角', '偏航角']
            
            for i, (angle_name, angle_data) in enumerate(attitude_data.items()):
                if angle_data:
                    ax.plot(time_data, angle_data, linewidth=self.style_config['line_width'],
                            color=colors[i], label=labels[i], marker='o',
                            markersize=self.style_config['marker_size'], markevery=20)
            
            ax.set_xlabel('时间 (s)')
            ax.set_ylabel('角度 (度)')
            ax.set_title('姿态角随时间变化')
            ax.grid(True, alpha=self.style_config['grid_alpha'])
            ax.legend()
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"姿态角图创建失败: {e}")
            return None
    
    def _create_performance_bar_chart(self, performance: Dict, output_file: str) -> Optional[str]:
        """创建飞行性能柱状图"""
        try:
            metrics = []
            values = []
            
            for key, value in performance.items():
                if isinstance(value, (int, float)):
                    metrics.append(key.replace('_', ' ').title())
                    values.append(value)
            
            if not metrics:
                return None
            
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            bars = ax.bar(metrics, values, color=self.style_config['color_palette'][:len(metrics)])
            
            ax.set_ylabel('数值')
            ax.set_title('飞行性能指标')
            ax.grid(True, alpha=self.style_config['grid_alpha'], axis='y')
            
            # 添加数值标签
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{value:.2f}', ha='center', va='bottom')
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"性能柱状图创建失败: {e}")
            return None
    
    def _create_aerodynamic_comparison_chart(self, comparison: Dict, output_file: str) -> Optional[str]:
        """创建气动力系数对比图"""
        try:
            original = comparison.get('original', {})
            damaged = comparison.get('damaged', {})
            
            if not original or not damaged:
                return None
            
            coefficients = list(original.keys())
            original_values = [original[coeff] for coeff in coefficients]
            damaged_values = [damaged[coeff] for coeff in coefficients]
            
            x = np.arange(len(coefficients))
            width = 0.35
            
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            bars1 = ax.bar(x - width/2, original_values, width, label='原始状态',
                          color=self.style_config['color_palette'][0])
            bars2 = ax.bar(x + width/2, damaged_values, width, label='毁伤后',
                          color=self.style_config['color_palette'][1])
            
            ax.set_xlabel('气动力系数')
            ax.set_ylabel('系数值')
            ax.set_title('气动力系数对比')
            ax.set_xticks(x)
            ax.set_xticklabels(coefficients)
            ax.legend()
            ax.grid(True, alpha=self.style_config['grid_alpha'], axis='y')
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"气动力对比图创建失败: {e}")
            return None
    
    def _create_performance_degradation_chart(self, comparison: Dict, output_file: str) -> Optional[str]:
        """创建性能退化图"""
        try:
            change_percentages = comparison.get('change_percentages', {})
            
            if not change_percentages:
                return None
            
            metrics = list(change_percentages.keys())
            changes = [change_percentages[metric] for metric in metrics]
            
            # 创建颜色映射（负值为红色，正值为绿色）
            colors = ['red' if change < 0 else 'green' for change in changes]
            
            fig, ax = plt.subplots(figsize=self.style_config['figure_size'])
            
            bars = ax.barh(metrics, changes, color=colors, alpha=0.7)
            
            ax.set_xlabel('变化百分比 (%)')
            ax.set_title('性能变化分析')
            ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
            ax.grid(True, alpha=self.style_config['grid_alpha'], axis='x')
            
            # 添加数值标签
            for bar, change in zip(bars, changes):
                width = bar.get_width()
                ax.text(width + (1 if width >= 0 else -1), bar.get_y() + bar.get_height()/2,
                       f'{change:.1f}%', ha='left' if width >= 0 else 'right', va='center')
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file
            
        except Exception as e:
            self.logger.error(f"性能退化图创建失败: {e}")
            return None
    
    def _create_trajectory_deviation_chart(self, comparison: Dict, output_file: str) -> Optional[str]:
        """创建轨迹偏差图"""
        try:
            altitude_dev = comparison.get('altitude_deviation', {})
            velocity_dev = comparison.get('velocity_deviation', {})
            
            if not altitude_dev and not velocity_dev:
                return None
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.style_config['figure_size'])
            
            # 高度偏差
            if altitude_dev:
                metrics = ['平均偏差', '最大偏差', 'RMS偏差']
                values = [
                    altitude_dev.get('mean_deviation', 0),
                    altitude_dev.get('max_deviation', 0),
                    altitude_dev.get('rms_deviation', 0)
                ]
                
                ax1.bar(metrics, values, color=self.style_config['color_palette'][0])
                ax1.set_ylabel('高度偏差 (m)')
                ax1.set_title('高度轨迹偏差')
                ax1.grid(True, alpha=self.style_config['grid_alpha'], axis='y')
            
            # 速度偏差
            if velocity_dev:
                metrics = ['平均偏差', '最大偏差', 'RMS偏差']
                values = [
                    velocity_dev.get('mean_deviation', 0),
                    velocity_dev.get('max_deviation', 0),
                    velocity_dev.get('rms_deviation', 0)
                ]
                
                ax2.bar(metrics, values, color=self.style_config['color_palette'][1])
                ax2.set_ylabel('速度偏差 (m/s)')
                ax2.set_title('速度轨迹偏差')
                ax2.grid(True, alpha=self.style_config['grid_alpha'], axis='y')
            
            plt.tight_layout()
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()
            
            return output_file

        except Exception as e:
            self.logger.error(f"轨迹偏差图创建失败: {e}")
            return None

    def create_comprehensive_dashboard(self, all_data: Dict, output_file: str) -> Optional[str]:
        """创建综合仪表板"""
        try:
            fig = plt.figure(figsize=(20, 16))

            # 创建子图布局
            gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)

            # 1. 毁伤指标概览
            ax1 = fig.add_subplot(gs[0, :2])
            if 'damage_metrics' in all_data:
                metrics = all_data['damage_metrics']
                metric_names = list(metrics.keys())[:4]  # 取前4个指标
                metric_values = [metrics[name] for name in metric_names]

                bars = ax1.bar(metric_names, metric_values, color=self.style_config['color_palette'][:4])
                ax1.set_title('毁伤指标概览')
                ax1.tick_params(axis='x', rotation=45)

            # 2. 气动力系数雷达图
            ax2 = fig.add_subplot(gs[0, 2:], projection='polar')
            if 'aerodynamic_coefficients' in all_data:
                aero_coeffs = all_data['aerodynamic_coefficients']
                labels = list(aero_coeffs.keys())
                values = list(aero_coeffs.values())

                angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
                values += values[:1]
                angles += angles[:1]

                ax2.plot(angles, values, 'o-', linewidth=2)
                ax2.fill(angles, values, alpha=0.25)
                ax2.set_xticks(angles[:-1])
                ax2.set_xticklabels(labels)
                ax2.set_title('气动力系数')

            # 3. 轨迹图
            ax3 = fig.add_subplot(gs[1, :2])
            if 'time_series' in all_data:
                time_series = all_data['time_series']
                time_data = time_series.get('time', [])
                altitude_data = time_series.get('altitude', [])

                if time_data and altitude_data:
                    ax3.plot(time_data, altitude_data, linewidth=2)
                    ax3.set_xlabel('时间 (s)')
                    ax3.set_ylabel('高度 (m)')
                    ax3.set_title('飞行轨迹')
                    ax3.grid(True, alpha=0.3)

            # 4. 性能对比
            ax4 = fig.add_subplot(gs[1, 2:])
            if 'performance_comparison' in all_data:
                comparison = all_data['performance_comparison']
                change_percentages = comparison.get('change_percentages', {})

                if change_percentages:
                    metrics = list(change_percentages.keys())[:5]  # 取前5个指标
                    changes = [change_percentages[metric] for metric in metrics]
                    colors = ['red' if change < 0 else 'green' for change in changes]

                    ax4.barh(metrics, changes, color=colors, alpha=0.7)
                    ax4.set_xlabel('变化百分比 (%)')
                    ax4.set_title('性能变化')
                    ax4.axvline(x=0, color='black', linestyle='-', linewidth=1)

            # 5. 毁伤区域分布
            ax5 = fig.add_subplot(gs[2, :2])
            if 'damage_analysis' in all_data:
                damage_analysis = all_data['damage_analysis']
                damaged_ratio = damage_analysis.get('damage_ratio', 0.0)
                undamaged_ratio = damage_analysis.get('undamaged_ratio', 1.0)

                labels = ['毁伤区域', '完好区域']
                sizes = [damaged_ratio * 100, undamaged_ratio * 100]
                colors = [self.style_config['color_palette'][3], self.style_config['color_palette'][4]]

                ax5.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax5.set_title('毁伤区域分布')

            # 6. 综合评估
            ax6 = fig.add_subplot(gs[2, 2:])
            if 'comprehensive_assessment' in all_data:
                assessment = all_data['comprehensive_assessment']
                categories = ['飞行能力', '任务效能', '生存能力', '总体影响']
                values = [
                    assessment.get('flight_capability', 0),
                    assessment.get('mission_effectiveness', 0),
                    assessment.get('survivability', 0),
                    assessment.get('overall_impact', 0)
                ]

                bars = ax6.bar(categories, values, color=self.style_config['color_palette'][:4])
                ax6.set_ylabel('评估分数')
                ax6.set_title('综合评估')
                ax6.set_ylim(0, 100)

                # 添加数值标签
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax6.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{value:.1f}', ha='center', va='bottom')

            plt.suptitle('激光毁伤效能分析综合仪表板', fontsize=20, y=0.98)
            plt.savefig(output_file, dpi=self.style_config['dpi'], bbox_inches='tight')
            plt.close()

            return output_file

        except Exception as e:
            self.logger.error(f"综合仪表板创建失败: {e}")
            return None

"""
数据分析 - 数据提取器

从仿真结果中提取和处理数据。
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json
import pickle

class DataExtractor:
    """数据提取器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.extracted_data = {}
        
    def extract_laser_damage_data(self, simulation_results: Dict) -> Dict[str, Any]:
        """提取激光毁伤数据"""
        try:
            laser_data = {}
            
            if 'laser_damage_results' in simulation_results:
                results = simulation_results['laser_damage_results']
                
                # 基本毁伤指标
                laser_data['damage_metrics'] = {
                    'max_temperature': results.get('max_temperature', 0.0),
                    'max_stress': results.get('max_stress', 0.0),
                    'damage_volume': results.get('damage_volume', 0.0),
                    'damage_depth': results.get('damage_depth', 0.0),
                    'computation_time': results.get('computation_time', 0.0)
                }
                
                # 温度场数据
                if 'temperature_field' in results:
                    temp_field = results['temperature_field']
                    if temp_field is not None:
                        laser_data['temperature_statistics'] = {
                            'mean_temperature': np.mean(temp_field),
                            'std_temperature': np.std(temp_field),
                            'min_temperature': np.min(temp_field),
                            'max_temperature': np.max(temp_field),
                            'temperature_range': np.max(temp_field) - np.min(temp_field)
                        }
                        
                        # 温度分布直方图数据
                        hist, bins = np.histogram(temp_field, bins=50)
                        laser_data['temperature_distribution'] = {
                            'histogram': hist.tolist(),
                            'bins': bins.tolist()
                        }
                
                # 应力场数据
                if 'stress_field' in results:
                    stress_field = results['stress_field']
                    if stress_field is not None:
                        laser_data['stress_statistics'] = {
                            'mean_stress': np.mean(stress_field),
                            'std_stress': np.std(stress_field),
                            'min_stress': np.min(stress_field),
                            'max_stress': np.max(stress_field),
                            'stress_range': np.max(stress_field) - np.min(stress_field)
                        }
                        
                        # 应力分布直方图数据
                        hist, bins = np.histogram(stress_field, bins=50)
                        laser_data['stress_distribution'] = {
                            'histogram': hist.tolist(),
                            'bins': bins.tolist()
                        }
                
                # 毁伤区域分析
                if 'damage_region' in results:
                    damage_region = results['damage_region']
                    if damage_region is not None:
                        total_elements = damage_region.size
                        damaged_elements = np.sum(damage_region)
                        
                        laser_data['damage_analysis'] = {
                            'total_elements': int(total_elements),
                            'damaged_elements': int(damaged_elements),
                            'damage_ratio': float(damaged_elements / total_elements) if total_elements > 0 else 0.0,
                            'undamaged_ratio': float((total_elements - damaged_elements) / total_elements) if total_elements > 0 else 1.0
                        }
            
            self.logger.info("激光毁伤数据提取完成")
            return laser_data
            
        except Exception as e:
            self.logger.error(f"激光毁伤数据提取失败: {e}")
            return {}
    
    def extract_post_damage_data(self, simulation_results: Dict) -> Dict[str, Any]:
        """提取毁伤后效数据"""
        try:
            post_damage_data = {}
            
            if 'post_damage_results' in simulation_results:
                results = simulation_results['post_damage_results']
                
                # 气动力系数
                if 'aerodynamic_coefficients' in results:
                    aero_coeffs = results['aerodynamic_coefficients']
                    post_damage_data['aerodynamic_coefficients'] = aero_coeffs
                
                # 飞行轨迹数据
                if 'flight_trajectory' in results:
                    trajectory = results['flight_trajectory']
                    if trajectory is not None:
                        post_damage_data['trajectory_statistics'] = {
                            'trajectory_length': len(trajectory),
                            'max_altitude': np.max(trajectory[:, 2]) if trajectory.shape[1] > 2 else 0.0,
                            'max_range': np.max(np.sqrt(trajectory[:, 0]**2 + trajectory[:, 1]**2)) if trajectory.shape[1] > 1 else 0.0,
                            'final_position': trajectory[-1].tolist() if len(trajectory) > 0 else [0, 0, 0]
                        }
                
                # 稳定性分析数据
                if 'stability_analysis' in results:
                    stability = results['stability_analysis']
                    post_damage_data['stability_metrics'] = stability
                
                # 性能退化数据
                if 'performance_degradation' in results:
                    degradation = results['performance_degradation']
                    post_damage_data['performance_degradation'] = degradation
            
            # 从详细结果中提取轨迹分析数据
            if 'trajectory_analysis_results' in simulation_results:
                traj_results = simulation_results['trajectory_analysis_results']
                
                if 'trajectory_data' in traj_results:
                    traj_data = traj_results['trajectory_data']
                    
                    # 提取时间序列数据
                    post_damage_data['time_series'] = {
                        'time': traj_data.get('time', []),
                        'altitude': traj_data.get('flight_path', {}).get('altitude', []),
                        'velocity': traj_data.get('velocity', {}).get('total', []),
                        'attitude': {
                            'pitch': traj_data.get('attitude', {}).get('theta', []),
                            'roll': traj_data.get('attitude', {}).get('phi', []),
                            'yaw': traj_data.get('attitude', {}).get('psi', [])
                        }
                    }
                
                # 飞行性能指标
                if 'flight_performance' in traj_results:
                    performance = traj_results['flight_performance']
                    post_damage_data['flight_performance'] = performance
            
            self.logger.info("毁伤后效数据提取完成")
            return post_damage_data
            
        except Exception as e:
            self.logger.error(f"毁伤后效数据提取失败: {e}")
            return {}
    
    def extract_comparison_data(self, original_results: Dict, damaged_results: Dict) -> Dict[str, Any]:
        """提取对比数据"""
        try:
            comparison_data = {}
            
            # 提取原始和毁伤后的数据
            original_laser = self.extract_laser_damage_data(original_results)
            damaged_laser = self.extract_laser_damage_data(damaged_results)
            
            original_post = self.extract_post_damage_data(original_results)
            damaged_post = self.extract_post_damage_data(damaged_results)
            
            # 毁伤指标对比
            if 'damage_metrics' in original_laser and 'damage_metrics' in damaged_laser:
                comparison_data['damage_comparison'] = self._compare_metrics(
                    original_laser['damage_metrics'],
                    damaged_laser['damage_metrics']
                )
            
            # 气动力系数对比
            if 'aerodynamic_coefficients' in original_post and 'aerodynamic_coefficients' in damaged_post:
                comparison_data['aerodynamic_comparison'] = self._compare_metrics(
                    original_post['aerodynamic_coefficients'],
                    damaged_post['aerodynamic_coefficients']
                )
            
            # 飞行性能对比
            if 'flight_performance' in original_post and 'flight_performance' in damaged_post:
                comparison_data['performance_comparison'] = self._compare_metrics(
                    original_post['flight_performance'],
                    damaged_post['flight_performance']
                )
            
            # 轨迹对比
            if 'time_series' in original_post and 'time_series' in damaged_post:
                comparison_data['trajectory_comparison'] = self._compare_trajectories(
                    original_post['time_series'],
                    damaged_post['time_series']
                )
            
            self.logger.info("对比数据提取完成")
            return comparison_data
            
        except Exception as e:
            self.logger.error(f"对比数据提取失败: {e}")
            return {}
    
    def _compare_metrics(self, original: Dict, damaged: Dict) -> Dict[str, Any]:
        """比较指标数据"""
        comparison = {
            'original': original,
            'damaged': damaged,
            'changes': {},
            'change_percentages': {}
        }
        
        for key in original:
            if key in damaged:
                original_val = original[key]
                damaged_val = damaged[key]
                
                if isinstance(original_val, (int, float)) and isinstance(damaged_val, (int, float)):
                    change = damaged_val - original_val
                    change_percent = (change / original_val * 100) if original_val != 0 else 0.0
                    
                    comparison['changes'][key] = change
                    comparison['change_percentages'][key] = change_percent
        
        return comparison
    
    def _compare_trajectories(self, original: Dict, damaged: Dict) -> Dict[str, Any]:
        """比较轨迹数据"""
        comparison = {}
        
        try:
            # 比较高度轨迹
            if 'altitude' in original and 'altitude' in damaged:
                orig_alt = np.array(original['altitude'])
                dam_alt = np.array(damaged['altitude'])
                
                min_len = min(len(orig_alt), len(dam_alt))
                if min_len > 0:
                    altitude_diff = dam_alt[:min_len] - orig_alt[:min_len]
                    comparison['altitude_deviation'] = {
                        'mean_deviation': np.mean(altitude_diff),
                        'max_deviation': np.max(np.abs(altitude_diff)),
                        'rms_deviation': np.sqrt(np.mean(altitude_diff**2))
                    }
            
            # 比较速度轨迹
            if 'velocity' in original and 'velocity' in damaged:
                orig_vel = np.array(original['velocity'])
                dam_vel = np.array(damaged['velocity'])
                
                min_len = min(len(orig_vel), len(dam_vel))
                if min_len > 0:
                    velocity_diff = dam_vel[:min_len] - orig_vel[:min_len]
                    comparison['velocity_deviation'] = {
                        'mean_deviation': np.mean(velocity_diff),
                        'max_deviation': np.max(np.abs(velocity_diff)),
                        'rms_deviation': np.sqrt(np.mean(velocity_diff**2))
                    }
            
        except Exception as e:
            self.logger.warning(f"轨迹比较部分失败: {e}")
        
        return comparison
    
    def create_summary_statistics(self, data: Dict) -> Dict[str, Any]:
        """创建汇总统计"""
        try:
            summary = {
                'data_overview': {},
                'key_metrics': {},
                'statistical_summary': {}
            }
            
            # 数据概览
            summary['data_overview'] = {
                'total_datasets': len(data),
                'data_types': list(data.keys()),
                'extraction_timestamp': pd.Timestamp.now().isoformat()
            }
            
            # 关键指标提取
            if 'damage_metrics' in data:
                metrics = data['damage_metrics']
                summary['key_metrics']['damage'] = {
                    'max_temperature': metrics.get('max_temperature', 0),
                    'max_stress': metrics.get('max_stress', 0),
                    'damage_volume': metrics.get('damage_volume', 0)
                }
            
            if 'flight_performance' in data:
                performance = data['flight_performance']
                summary['key_metrics']['performance'] = {
                    'average_speed': performance.get('average_speed', 0),
                    'max_speed': performance.get('max_speed', 0),
                    'flight_time': performance.get('flight_time', 0)
                }
            
            # 统计汇总
            for key, value in data.items():
                if isinstance(value, dict):
                    numeric_values = [v for v in value.values() if isinstance(v, (int, float))]
                    if numeric_values:
                        summary['statistical_summary'][key] = {
                            'count': len(numeric_values),
                            'mean': np.mean(numeric_values),
                            'std': np.std(numeric_values),
                            'min': np.min(numeric_values),
                            'max': np.max(numeric_values)
                        }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"汇总统计创建失败: {e}")
            return {}
    
    def export_data(self, data: Dict, output_path: str, format: str = 'json') -> bool:
        """导出数据"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == 'json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            
            elif format.lower() == 'pickle':
                with open(output_file, 'wb') as f:
                    pickle.dump(data, f)
            
            elif format.lower() == 'csv':
                # 将嵌套字典展平为DataFrame
                flattened_data = self._flatten_dict(data)
                df = pd.DataFrame([flattened_data])
                df.to_csv(output_file, index=False, encoding='utf-8-sig')
            
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            self.logger.info(f"数据已导出到: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"数据导出失败: {e}")
            return False
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """展平嵌套字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, (list, np.ndarray)):
                # 对于列表和数组，只保存基本统计信息
                if len(v) > 0 and isinstance(v[0], (int, float)):
                    items.append((f"{new_key}_mean", np.mean(v)))
                    items.append((f"{new_key}_max", np.max(v)))
                    items.append((f"{new_key}_min", np.min(v)))
                else:
                    items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def load_data(self, input_path: str, format: str = 'json') -> Dict:
        """加载数据"""
        try:
            input_file = Path(input_path)
            
            if not input_file.exists():
                raise FileNotFoundError(f"文件不存在: {input_path}")
            
            if format.lower() == 'json':
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            elif format.lower() == 'pickle':
                with open(input_file, 'rb') as f:
                    data = pickle.load(f)
            
            elif format.lower() == 'csv':
                df = pd.read_csv(input_file, encoding='utf-8-sig')
                data = df.to_dict('records')[0] if len(df) > 0 else {}
            
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            self.logger.info(f"数据已从 {input_path} 加载")
            return data
            
        except Exception as e:
            self.logger.error(f"数据加载失败: {e}")
            return {}

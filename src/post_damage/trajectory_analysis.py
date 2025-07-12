"""
毁伤后效分析 - 轨迹分析

分析毁伤后的飞行轨迹和性能变化。
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import matplotlib.pyplot as plt
from dataclasses import dataclass

from .flight_simulator import FlightState, FlightSimulator

@dataclass
class TrajectoryMetrics:
    """轨迹指标"""
    max_altitude: float = 0.0           # 最大高度 (m)
    max_range: float = 0.0              # 最大航程 (m)
    flight_time: float = 0.0            # 飞行时间 (s)
    impact_velocity: float = 0.0        # 撞击速度 (m/s)
    impact_angle: float = 0.0           # 撞击角度 (度)
    stability_margin: float = 0.0       # 稳定裕度
    controllability_index: float = 0.0  # 可控性指数

class TrajectoryAnalyzer:
    """轨迹分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.flight_simulator = FlightSimulator()
        
        # 分析结果存储
        self.analysis_results = {}
        self.trajectory_data = {}
        
    def analyze_trajectory(self, simulation_results: Dict) -> Dict[str, any]:
        """分析飞行轨迹"""
        try:
            if not simulation_results.get('success', False):
                raise ValueError("仿真结果无效")
            
            time_data = simulation_results['time']
            states_data = simulation_results['states']
            forces_data = simulation_results['forces']
            
            if not time_data or not states_data:
                raise ValueError("仿真数据为空")
            
            self.logger.info("开始轨迹分析...")
            
            # 提取轨迹数据
            trajectory = self._extract_trajectory_data(time_data, states_data)
            
            # 计算轨迹指标
            metrics = self._calculate_trajectory_metrics(trajectory)
            
            # 分析飞行性能
            performance = self._analyze_flight_performance(trajectory, forces_data)
            
            # 分析稳定性
            stability = self._analyze_flight_stability(trajectory)
            
            # 分析可控性
            controllability = self._analyze_controllability(trajectory)
            
            # 综合分析结果
            analysis_results = {
                'trajectory_metrics': metrics,
                'flight_performance': performance,
                'stability_analysis': stability,
                'controllability_analysis': controllability,
                'trajectory_data': trajectory
            }
            
            self.analysis_results = analysis_results
            self.trajectory_data = trajectory
            
            self.logger.info("轨迹分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"轨迹分析失败: {e}")
            return {'error': str(e)}
    
    def _extract_trajectory_data(self, time_data: np.ndarray, states_data: List[FlightState]) -> Dict:
        """提取轨迹数据"""
        trajectory = {
            'time': time_data,
            'position': {'x': [], 'y': [], 'z': []},
            'velocity': {'u': [], 'v': [], 'w': [], 'total': []},
            'attitude': {'phi': [], 'theta': [], 'psi': []},
            'angular_velocity': {'p': [], 'q': [], 'r': []},
            'flight_path': {'altitude': [], 'range': [], 'flight_path_angle': []}
        }
        
        for state in states_data:
            # 位置
            trajectory['position']['x'].append(state.x)
            trajectory['position']['y'].append(state.y)
            trajectory['position']['z'].append(-state.z)  # 转换为高度（正值向上）
            
            # 速度
            trajectory['velocity']['u'].append(state.u)
            trajectory['velocity']['v'].append(state.v)
            trajectory['velocity']['w'].append(state.w)
            
            total_velocity = np.sqrt(state.u**2 + state.v**2 + state.w**2)
            trajectory['velocity']['total'].append(total_velocity)
            
            # 姿态
            trajectory['attitude']['phi'].append(np.degrees(state.phi))
            trajectory['attitude']['theta'].append(np.degrees(state.theta))
            trajectory['attitude']['psi'].append(np.degrees(state.psi))
            
            # 角速度
            trajectory['angular_velocity']['p'].append(np.degrees(state.p))
            trajectory['angular_velocity']['q'].append(np.degrees(state.q))
            trajectory['angular_velocity']['r'].append(np.degrees(state.r))
            
            # 飞行路径参数
            altitude = -state.z
            range_val = np.sqrt(state.x**2 + state.y**2)
            
            # 飞行路径角
            if total_velocity > 0.1:
                flight_path_angle = np.degrees(np.arcsin(-state.w / total_velocity))
            else:
                flight_path_angle = 0.0
            
            trajectory['flight_path']['altitude'].append(altitude)
            trajectory['flight_path']['range'].append(range_val)
            trajectory['flight_path']['flight_path_angle'].append(flight_path_angle)
        
        # 转换为numpy数组
        for category in trajectory:
            if category != 'time':
                for key in trajectory[category]:
                    trajectory[category][key] = np.array(trajectory[category][key])
        
        return trajectory
    
    def _calculate_trajectory_metrics(self, trajectory: Dict) -> TrajectoryMetrics:
        """计算轨迹指标"""
        metrics = TrajectoryMetrics()
        
        try:
            # 最大高度
            metrics.max_altitude = np.max(trajectory['flight_path']['altitude'])
            
            # 最大航程
            metrics.max_range = np.max(trajectory['flight_path']['range'])
            
            # 飞行时间
            metrics.flight_time = trajectory['time'][-1] if len(trajectory['time']) > 0 else 0.0
            
            # 撞击速度（最终速度）
            if len(trajectory['velocity']['total']) > 0:
                metrics.impact_velocity = trajectory['velocity']['total'][-1]
            
            # 撞击角度（最终飞行路径角）
            if len(trajectory['flight_path']['flight_path_angle']) > 0:
                metrics.impact_angle = trajectory['flight_path']['flight_path_angle'][-1]
            
            # 稳定裕度（基于俯仰角变化）
            theta_data = trajectory['attitude']['theta']
            if len(theta_data) > 1:
                theta_std = np.std(theta_data)
                metrics.stability_margin = max(0, 10 - theta_std)  # 简化计算
            
            # 可控性指数（基于角速度变化）
            p_data = trajectory['angular_velocity']['p']
            q_data = trajectory['angular_velocity']['q']
            r_data = trajectory['angular_velocity']['r']
            
            if len(p_data) > 1:
                angular_vel_rms = np.sqrt(np.mean(np.array(p_data)**2 + 
                                                np.array(q_data)**2 + 
                                                np.array(r_data)**2))
                metrics.controllability_index = max(0, 100 - angular_vel_rms)  # 简化计算
            
        except Exception as e:
            self.logger.warning(f"轨迹指标计算部分失败: {e}")
        
        return metrics
    
    def _analyze_flight_performance(self, trajectory: Dict, forces_data: List) -> Dict:
        """分析飞行性能"""
        performance = {
            'average_speed': 0.0,
            'max_speed': 0.0,
            'climb_rate': 0.0,
            'turn_rate': 0.0,
            'load_factor': 0.0,
            'energy_loss': 0.0
        }
        
        try:
            velocity_data = trajectory['velocity']['total']
            altitude_data = trajectory['flight_path']['altitude']
            time_data = trajectory['time']
            
            if len(velocity_data) > 0:
                performance['average_speed'] = np.mean(velocity_data)
                performance['max_speed'] = np.max(velocity_data)
            
            # 爬升率
            if len(altitude_data) > 1 and len(time_data) > 1:
                dt = time_data[1] - time_data[0]
                climb_rates = np.diff(altitude_data) / dt
                performance['climb_rate'] = np.mean(climb_rates[climb_rates > 0]) if np.any(climb_rates > 0) else 0.0
            
            # 转弯率
            psi_data = trajectory['attitude']['psi']
            if len(psi_data) > 1:
                turn_rates = np.abs(np.diff(psi_data))
                performance['turn_rate'] = np.mean(turn_rates)
            
            # 载荷因子（基于法向加速度）
            if forces_data and len(forces_data) > 0:
                # 简化计算，假设forces_data包含总力
                normal_forces = [f[2] for f in forces_data if len(f) >= 3]  # Z方向力
                if normal_forces:
                    # 载荷因子 = 法向力 / 重力
                    mass = 1000.0  # 假设质量，实际应从飞行器参数获取
                    g = 9.81
                    load_factors = [abs(f) / (mass * g) for f in normal_forces]
                    performance['load_factor'] = np.mean(load_factors)
            
            # 能量损失
            if len(velocity_data) > 1 and len(altitude_data) > 1:
                initial_energy = 0.5 * velocity_data[0]**2 + 9.81 * altitude_data[0]
                final_energy = 0.5 * velocity_data[-1]**2 + 9.81 * altitude_data[-1]
                performance['energy_loss'] = initial_energy - final_energy
            
        except Exception as e:
            self.logger.warning(f"飞行性能分析部分失败: {e}")
        
        return performance
    
    def _analyze_flight_stability(self, trajectory: Dict) -> Dict:
        """分析飞行稳定性"""
        stability = {
            'longitudinal_stability': 0.0,
            'lateral_stability': 0.0,
            'directional_stability': 0.0,
            'overall_stability': 0.0,
            'oscillation_frequency': 0.0,
            'damping_ratio': 0.0
        }
        
        try:
            # 纵向稳定性（基于俯仰角变化）
            theta_data = trajectory['attitude']['theta']
            if len(theta_data) > 10:
                theta_var = np.var(theta_data)
                stability['longitudinal_stability'] = max(0, 100 - theta_var * 10)
            
            # 横向稳定性（基于滚转角变化）
            phi_data = trajectory['attitude']['phi']
            if len(phi_data) > 10:
                phi_var = np.var(phi_data)
                stability['lateral_stability'] = max(0, 100 - phi_var * 10)
            
            # 航向稳定性（基于偏航角变化）
            psi_data = trajectory['attitude']['psi']
            if len(psi_data) > 10:
                psi_var = np.var(psi_data)
                stability['directional_stability'] = max(0, 100 - psi_var * 10)
            
            # 总体稳定性
            stability['overall_stability'] = np.mean([
                stability['longitudinal_stability'],
                stability['lateral_stability'],
                stability['directional_stability']
            ])
            
            # 振荡频率分析（简化）
            if len(theta_data) > 20:
                # 使用FFT分析主要频率
                fft_result = np.fft.fft(theta_data - np.mean(theta_data))
                freqs = np.fft.fftfreq(len(theta_data), d=0.01)  # 假设采样间隔0.01s
                
                # 找到主要频率
                power_spectrum = np.abs(fft_result)**2
                main_freq_idx = np.argmax(power_spectrum[1:len(power_spectrum)//2]) + 1
                stability['oscillation_frequency'] = abs(freqs[main_freq_idx])
                
                # 简化的阻尼比估算
                if stability['oscillation_frequency'] > 0:
                    amplitude_decay = np.std(theta_data[:len(theta_data)//2]) / np.std(theta_data[len(theta_data)//2:])
                    stability['damping_ratio'] = min(1.0, amplitude_decay / 2.0)
            
        except Exception as e:
            self.logger.warning(f"稳定性分析部分失败: {e}")
        
        return stability
    
    def _analyze_controllability(self, trajectory: Dict) -> Dict:
        """分析可控性"""
        controllability = {
            'pitch_control_effectiveness': 0.0,
            'roll_control_effectiveness': 0.0,
            'yaw_control_effectiveness': 0.0,
            'overall_controllability': 0.0,
            'response_time': 0.0,
            'control_authority': 0.0
        }
        
        try:
            # 基于角速度响应分析控制效果
            p_data = trajectory['angular_velocity']['p']
            q_data = trajectory['angular_velocity']['q']
            r_data = trajectory['angular_velocity']['r']
            
            if len(p_data) > 10:
                # 滚转控制效果
                p_range = np.max(p_data) - np.min(p_data)
                controllability['roll_control_effectiveness'] = min(100, p_range * 5)
                
                # 俯仰控制效果
                q_range = np.max(q_data) - np.min(q_data)
                controllability['pitch_control_effectiveness'] = min(100, q_range * 5)
                
                # 偏航控制效果
                r_range = np.max(r_data) - np.min(r_data)
                controllability['yaw_control_effectiveness'] = min(100, r_range * 5)
            
            # 总体可控性
            controllability['overall_controllability'] = np.mean([
                controllability['pitch_control_effectiveness'],
                controllability['roll_control_effectiveness'],
                controllability['yaw_control_effectiveness']
            ])
            
            # 响应时间（简化估算）
            if len(q_data) > 5:
                # 寻找第一个显著的角速度变化
                q_diff = np.abs(np.diff(q_data))
                significant_change_idx = np.where(q_diff > np.std(q_diff))[0]
                if len(significant_change_idx) > 0:
                    controllability['response_time'] = significant_change_idx[0] * 0.01  # 假设采样间隔0.01s
            
            # 控制权限（基于最大角速度）
            max_angular_vel = max(np.max(np.abs(p_data)), np.max(np.abs(q_data)), np.max(np.abs(r_data)))
            controllability['control_authority'] = min(100, max_angular_vel * 2)
            
        except Exception as e:
            self.logger.warning(f"可控性分析部分失败: {e}")
        
        return controllability
    
    def compare_trajectories(self, original_results: Dict, damaged_results: Dict) -> Dict:
        """比较原始和毁伤后的轨迹"""
        try:
            comparison = {
                'performance_degradation': {},
                'stability_degradation': {},
                'controllability_degradation': {},
                'trajectory_deviation': {}
            }
            
            # 分析两个轨迹
            original_analysis = self.analyze_trajectory(original_results)
            damaged_analysis = self.analyze_trajectory(damaged_results)
            
            if 'error' in original_analysis or 'error' in damaged_analysis:
                return {'error': '轨迹分析失败'}
            
            # 性能退化
            orig_perf = original_analysis['flight_performance']
            dam_perf = damaged_analysis['flight_performance']
            
            for key in orig_perf:
                if orig_perf[key] != 0:
                    degradation = (orig_perf[key] - dam_perf[key]) / orig_perf[key] * 100
                else:
                    degradation = 0.0
                comparison['performance_degradation'][key] = degradation
            
            # 稳定性退化
            orig_stab = original_analysis['stability_analysis']
            dam_stab = damaged_analysis['stability_analysis']
            
            for key in orig_stab:
                if orig_stab[key] != 0:
                    degradation = (orig_stab[key] - dam_stab[key]) / orig_stab[key] * 100
                else:
                    degradation = 0.0
                comparison['stability_degradation'][key] = degradation
            
            # 可控性退化
            orig_ctrl = original_analysis['controllability_analysis']
            dam_ctrl = damaged_analysis['controllability_analysis']
            
            for key in orig_ctrl:
                if orig_ctrl[key] != 0:
                    degradation = (orig_ctrl[key] - dam_ctrl[key]) / orig_ctrl[key] * 100
                else:
                    degradation = 0.0
                comparison['controllability_degradation'][key] = degradation
            
            # 轨迹偏差
            orig_traj = original_analysis['trajectory_data']
            dam_traj = damaged_analysis['trajectory_data']
            
            if 'flight_path' in orig_traj and 'flight_path' in dam_traj:
                # 计算轨迹偏差
                orig_alt = orig_traj['flight_path']['altitude']
                dam_alt = dam_traj['flight_path']['altitude']
                
                min_len = min(len(orig_alt), len(dam_alt))
                if min_len > 0:
                    altitude_deviation = np.mean(np.abs(orig_alt[:min_len] - dam_alt[:min_len]))
                    comparison['trajectory_deviation']['altitude_deviation'] = altitude_deviation
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"轨迹比较失败: {e}")
            return {'error': str(e)}
    
    def generate_trajectory_report(self) -> str:
        """生成轨迹分析报告"""
        if not self.analysis_results:
            return "无分析结果可用"
        
        report = []
        report.append("=" * 60)
        report.append("飞行轨迹分析报告")
        report.append("=" * 60)
        
        # 轨迹指标
        if 'trajectory_metrics' in self.analysis_results:
            metrics = self.analysis_results['trajectory_metrics']
            report.append("\n轨迹指标:")
            report.append(f"  最大高度: {metrics.max_altitude:.1f} m")
            report.append(f"  最大航程: {metrics.max_range:.1f} m")
            report.append(f"  飞行时间: {metrics.flight_time:.1f} s")
            report.append(f"  撞击速度: {metrics.impact_velocity:.1f} m/s")
            report.append(f"  撞击角度: {metrics.impact_angle:.1f} °")
            report.append(f"  稳定裕度: {metrics.stability_margin:.1f}")
            report.append(f"  可控性指数: {metrics.controllability_index:.1f}")
        
        # 飞行性能
        if 'flight_performance' in self.analysis_results:
            perf = self.analysis_results['flight_performance']
            report.append("\n飞行性能:")
            report.append(f"  平均速度: {perf['average_speed']:.1f} m/s")
            report.append(f"  最大速度: {perf['max_speed']:.1f} m/s")
            report.append(f"  爬升率: {perf['climb_rate']:.1f} m/s")
            report.append(f"  转弯率: {perf['turn_rate']:.1f} °/s")
            report.append(f"  载荷因子: {perf['load_factor']:.2f}")
        
        # 稳定性分析
        if 'stability_analysis' in self.analysis_results:
            stab = self.analysis_results['stability_analysis']
            report.append("\n稳定性分析:")
            report.append(f"  纵向稳定性: {stab['longitudinal_stability']:.1f}%")
            report.append(f"  横向稳定性: {stab['lateral_stability']:.1f}%")
            report.append(f"  航向稳定性: {stab['directional_stability']:.1f}%")
            report.append(f"  总体稳定性: {stab['overall_stability']:.1f}%")
        
        # 可控性分析
        if 'controllability_analysis' in self.analysis_results:
            ctrl = self.analysis_results['controllability_analysis']
            report.append("\n可控性分析:")
            report.append(f"  俯仰控制效果: {ctrl['pitch_control_effectiveness']:.1f}%")
            report.append(f"  滚转控制效果: {ctrl['roll_control_effectiveness']:.1f}%")
            report.append(f"  偏航控制效果: {ctrl['yaw_control_effectiveness']:.1f}%")
            report.append(f"  总体可控性: {ctrl['overall_controllability']:.1f}%")
        
        report.append("=" * 60)
        
        return "\n".join(report)

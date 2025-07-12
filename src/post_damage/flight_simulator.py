"""
毁伤后效分析 - 飞行模拟器

实现6自由度飞行动力学仿真。
"""

import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy.integrate import solve_ivp

@dataclass
class FlightState:
    """飞行状态"""
    # 位置 (m)
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    
    # 速度 (m/s)
    u: float = 0.0  # 机体坐标系X轴速度
    v: float = 0.0  # 机体坐标系Y轴速度
    w: float = 0.0  # 机体坐标系Z轴速度
    
    # 姿态角 (rad)
    phi: float = 0.0    # 滚转角
    theta: float = 0.0  # 俯仰角
    psi: float = 0.0    # 偏航角
    
    # 角速度 (rad/s)
    p: float = 0.0  # 滚转角速度
    q: float = 0.0  # 俯仰角速度
    r: float = 0.0  # 偏航角速度
    
    def to_array(self) -> np.ndarray:
        """转换为状态向量"""
        return np.array([
            self.x, self.y, self.z,
            self.u, self.v, self.w,
            self.phi, self.theta, self.psi,
            self.p, self.q, self.r
        ])
    
    @classmethod
    def from_array(cls, state_vector: np.ndarray):
        """从状态向量创建"""
        return cls(
            x=state_vector[0], y=state_vector[1], z=state_vector[2],
            u=state_vector[3], v=state_vector[4], w=state_vector[5],
            phi=state_vector[6], theta=state_vector[7], psi=state_vector[8],
            p=state_vector[9], q=state_vector[10], r=state_vector[11]
        )

@dataclass
class AircraftParameters:
    """飞行器参数"""
    mass: float = 1000.0        # 质量 (kg)
    Ixx: float = 1000.0         # 转动惯量 (kg·m²)
    Iyy: float = 2000.0
    Izz: float = 3000.0
    Ixz: float = 0.0
    
    # 几何参数
    wing_area: float = 20.0     # 机翼面积 (m²)
    wing_span: float = 10.0     # 翼展 (m)
    chord: float = 2.0          # 平均气动弦长 (m)

class FlightSimulator:
    """飞行模拟器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 飞行器参数
        self.aircraft_params = AircraftParameters()
        
        # 当前飞行状态
        self.current_state = FlightState()
        
        # 气动力系数
        self.aero_coefficients = {
            'CL': 0.5, 'CD': 0.05, 'CM': 0.0,
            'CY': 0.0, 'Cl': 0.0, 'Cn': 0.0
        }
        
        # 稳定性导数
        self.stability_derivatives = {
            'CL_alpha': 5.0, 'CD_alpha': 0.5, 'CM_alpha': -1.0,
            'CL_q': 8.0, 'CM_q': -20.0,
            'CY_beta': -0.5, 'Cl_beta': -0.1, 'Cn_beta': 0.1,
            'Cl_p': -0.5, 'Cn_r': -0.3
        }
        
        # 环境参数
        self.environment = {
            'rho': 1.225,      # 空气密度 (kg/m³)
            'g': 9.81,         # 重力加速度 (m/s²)
            'wind_velocity': np.array([0.0, 0.0, 0.0])  # 风速 (m/s)
        }
        
        # 仿真历史
        self.simulation_history = {
            'time': [],
            'states': [],
            'forces': [],
            'moments': []
        }
    
    def set_aircraft_parameters(self, params: Dict[str, float]):
        """设置飞行器参数"""
        for key, value in params.items():
            if hasattr(self.aircraft_params, key):
                setattr(self.aircraft_params, key, value)
    
    def set_aerodynamic_coefficients(self, coefficients: Dict[str, float]):
        """设置气动力系数"""
        self.aero_coefficients.update(coefficients)
        self.logger.info(f"气动力系数已更新: CL={coefficients.get('CL', 'N/A')}, "
                        f"CD={coefficients.get('CD', 'N/A')}")
    
    def set_initial_conditions(self, initial_state: FlightState, 
                              environment: Optional[Dict] = None):
        """设置初始条件"""
        self.current_state = initial_state
        
        if environment:
            self.environment.update(environment)
        
        # 清空历史记录
        self.simulation_history = {
            'time': [],
            'states': [],
            'forces': [],
            'moments': []
        }
        
        self.logger.info("初始条件设置完成")
    
    def calculate_aerodynamic_forces_moments(self, state: FlightState) -> Tuple[np.ndarray, np.ndarray]:
        """计算气动力和气动力矩"""
        # 计算空速和气流角
        V = np.sqrt(state.u**2 + state.v**2 + state.w**2)
        
        if V < 0.1:  # 避免除零
            return np.zeros(3), np.zeros(3)
        
        # 攻角和侧滑角
        alpha = np.arctan2(state.w, state.u)
        beta = np.arcsin(state.v / V) if V > 0 else 0.0
        
        # 动压
        q_dyn = 0.5 * self.environment['rho'] * V**2
        
        # 无量纲角速度
        p_hat = state.p * self.aircraft_params.wing_span / (2 * V) if V > 0 else 0.0
        q_hat = state.q * self.aircraft_params.chord / (2 * V) if V > 0 else 0.0
        r_hat = state.r * self.aircraft_params.wing_span / (2 * V) if V > 0 else 0.0
        
        # 计算气动力系数
        CL = (self.aero_coefficients['CL'] + 
              self.stability_derivatives['CL_alpha'] * alpha +
              self.stability_derivatives['CL_q'] * q_hat)
        
        CD = (self.aero_coefficients['CD'] + 
              self.stability_derivatives['CD_alpha'] * alpha)
        
        CY = (self.aero_coefficients['CY'] + 
              self.stability_derivatives['CY_beta'] * beta)
        
        # 计算气动力矩系数
        Cl = (self.aero_coefficients['Cl'] + 
              self.stability_derivatives['Cl_beta'] * beta +
              self.stability_derivatives['Cl_p'] * p_hat)
        
        CM = (self.aero_coefficients['CM'] + 
              self.stability_derivatives['CM_alpha'] * alpha +
              self.stability_derivatives['CM_q'] * q_hat)
        
        Cn = (self.aero_coefficients['Cn'] + 
              self.stability_derivatives['Cn_beta'] * beta +
              self.stability_derivatives['Cn_r'] * r_hat)
        
        # 转换到机体坐标系
        # 气动力 (机体坐标系)
        L = q_dyn * self.aircraft_params.wing_area * CL  # 升力
        D = q_dyn * self.aircraft_params.wing_area * CD  # 阻力
        Y = q_dyn * self.aircraft_params.wing_area * CY  # 侧力
        
        # 从风轴转换到机体轴
        cos_alpha = np.cos(alpha)
        sin_alpha = np.sin(alpha)
        
        F_aero = np.array([
            -D * cos_alpha + L * sin_alpha,  # X方向力
            Y,                               # Y方向力
            -D * sin_alpha - L * cos_alpha   # Z方向力
        ])
        
        # 气动力矩 (机体坐标系)
        M_aero = np.array([
            q_dyn * self.aircraft_params.wing_area * self.aircraft_params.wing_span * Cl,  # 滚转力矩
            q_dyn * self.aircraft_params.wing_area * self.aircraft_params.chord * CM,      # 俯仰力矩
            q_dyn * self.aircraft_params.wing_area * self.aircraft_params.wing_span * Cn   # 偏航力矩
        ])
        
        return F_aero, M_aero
    
    def calculate_gravity_force(self, state: FlightState) -> np.ndarray:
        """计算重力"""
        # 重力在地面坐标系中为 [0, 0, mg]
        # 转换到机体坐标系
        cos_theta = np.cos(state.theta)
        sin_theta = np.sin(state.theta)
        cos_phi = np.cos(state.phi)
        sin_phi = np.sin(state.phi)
        
        mg = self.aircraft_params.mass * self.environment['g']
        
        F_gravity = mg * np.array([
            -sin_theta,
            cos_theta * sin_phi,
            cos_theta * cos_phi
        ])
        
        return F_gravity
    
    def flight_dynamics(self, t: float, state_vector: np.ndarray) -> np.ndarray:
        """飞行动力学方程"""
        state = FlightState.from_array(state_vector)
        
        # 计算气动力和气动力矩
        F_aero, M_aero = self.calculate_aerodynamic_forces_moments(state)
        
        # 计算重力
        F_gravity = self.calculate_gravity_force(state)
        
        # 总力
        F_total = F_aero + F_gravity
        
        # 运动学方程
        # 位置导数 (地面坐标系)
        cos_theta = np.cos(state.theta)
        sin_theta = np.sin(state.theta)
        cos_phi = np.cos(state.phi)
        sin_phi = np.sin(state.phi)
        cos_psi = np.cos(state.psi)
        sin_psi = np.sin(state.psi)
        
        # 机体坐标系到地面坐标系的转换矩阵
        T_bg = np.array([
            [cos_theta * cos_psi, 
             sin_phi * sin_theta * cos_psi - cos_phi * sin_psi,
             cos_phi * sin_theta * cos_psi + sin_phi * sin_psi],
            [cos_theta * sin_psi,
             sin_phi * sin_theta * sin_psi + cos_phi * cos_psi,
             cos_phi * sin_theta * sin_psi - sin_phi * cos_psi],
            [-sin_theta,
             sin_phi * cos_theta,
             cos_phi * cos_theta]
        ])
        
        # 位置导数
        pos_dot = T_bg @ np.array([state.u, state.v, state.w])
        
        # 速度导数 (机体坐标系)
        vel_dot = F_total / self.aircraft_params.mass - np.array([
            state.q * state.w - state.r * state.v,
            state.r * state.u - state.p * state.w,
            state.p * state.v - state.q * state.u
        ])
        
        # 姿态角导数
        tan_theta = np.tan(state.theta)
        sec_theta = 1.0 / np.cos(state.theta) if abs(np.cos(state.theta)) > 1e-6 else 1e6
        
        attitude_dot = np.array([
            state.p + (state.q * sin_phi + state.r * cos_phi) * tan_theta,
            state.q * cos_phi - state.r * sin_phi,
            (state.q * sin_phi + state.r * cos_phi) * sec_theta
        ])
        
        # 角速度导数
        I = np.array([
            [self.aircraft_params.Ixx, 0, -self.aircraft_params.Ixz],
            [0, self.aircraft_params.Iyy, 0],
            [-self.aircraft_params.Ixz, 0, self.aircraft_params.Izz]
        ])
        
        omega = np.array([state.p, state.q, state.r])
        omega_cross = np.array([
            [0, -state.r, state.q],
            [state.r, 0, -state.p],
            [-state.q, state.p, 0]
        ])
        
        omega_dot = np.linalg.solve(I, M_aero - omega_cross @ I @ omega)
        
        # 组合状态导数
        state_dot = np.concatenate([pos_dot, vel_dot, attitude_dot, omega_dot])
        
        return state_dot
    
    def simulate_flight(self, duration: float, dt: float = 0.01) -> Dict:
        """执行飞行仿真"""
        try:
            self.logger.info(f"开始飞行仿真，持续时间: {duration}s")
            
            # 时间向量
            t_span = (0, duration)
            t_eval = np.arange(0, duration + dt, dt)
            
            # 初始状态
            y0 = self.current_state.to_array()
            
            # 求解微分方程
            sol = solve_ivp(
                self.flight_dynamics,
                t_span,
                y0,
                t_eval=t_eval,
                method='RK45',
                rtol=1e-6,
                atol=1e-8
            )
            
            if not sol.success:
                raise RuntimeError(f"飞行仿真失败: {sol.message}")
            
            # 处理结果
            results = {
                'time': sol.t,
                'states': [FlightState.from_array(state) for state in sol.y.T],
                'success': True,
                'message': '仿真完成'
            }
            
            # 计算每个时刻的力和力矩
            forces_history = []
            moments_history = []
            
            for state_vec in sol.y.T:
                state = FlightState.from_array(state_vec)
                F_aero, M_aero = self.calculate_aerodynamic_forces_moments(state)
                F_gravity = self.calculate_gravity_force(state)
                
                forces_history.append(F_aero + F_gravity)
                moments_history.append(M_aero)
            
            results['forces'] = forces_history
            results['moments'] = moments_history
            
            # 更新仿真历史
            self.simulation_history = {
                'time': sol.t.tolist(),
                'states': results['states'],
                'forces': forces_history,
                'moments': moments_history
            }
            
            self.logger.info("飞行仿真完成")
            return results
            
        except Exception as e:
            self.logger.error(f"飞行仿真失败: {e}")
            return {
                'success': False,
                'message': str(e),
                'time': [],
                'states': [],
                'forces': [],
                'moments': []
            }
    
    def analyze_stability(self) -> Dict[str, float]:
        """分析飞行稳定性"""
        try:
            # 简化的稳定性分析
            stability_analysis = {}
            
            # 纵向稳定性
            CM_alpha = self.stability_derivatives['CM_alpha']
            stability_analysis['longitudinal_stable'] = CM_alpha < 0
            stability_analysis['static_margin'] = -CM_alpha / self.stability_derivatives['CL_alpha']
            
            # 横航向稳定性
            Cn_beta = self.stability_derivatives['Cn_beta']
            Cl_beta = self.stability_derivatives['Cl_beta']
            
            stability_analysis['directional_stable'] = Cn_beta > 0
            stability_analysis['lateral_stable'] = Cl_beta < 0
            
            # 阻尼特性
            stability_analysis['pitch_damping'] = self.stability_derivatives['CM_q']
            stability_analysis['roll_damping'] = self.stability_derivatives['Cl_p']
            stability_analysis['yaw_damping'] = self.stability_derivatives['Cn_r']
            
            return stability_analysis
            
        except Exception as e:
            self.logger.error(f"稳定性分析失败: {e}")
            return {}
    
    def get_flight_envelope(self) -> Dict[str, Tuple[float, float]]:
        """获取飞行包线"""
        # 简化的飞行包线估算
        envelope = {
            'altitude_range': (0.0, 15000.0),      # 高度范围 (m)
            'speed_range': (50.0, 300.0),          # 速度范围 (m/s)
            'load_factor_range': (-2.0, 6.0),      # 载荷因子范围
            'angle_of_attack_range': (-10.0, 25.0) # 攻角范围 (度)
        }
        
        return envelope

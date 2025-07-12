"""
飞行器激光毁伤仿真器

基于完整飞行器模型的激光毁伤效能分析仿真器。
"""

import sys
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

from core.base_simulator import BaseSimulator, SimulationStatus
from core.data_models import LaserParameters, MaterialData, GeometryData
from aircraft_modeling.aircraft_types import AircraftParameters, AircraftType
from aircraft_modeling.mesh_generator import MeshGenerator, MeshParameters
from aircraft_modeling.fluid_domain_setup import FluidDomainSetup, FlightConditions

@dataclass
class LaserTargetingParameters:
    """激光瞄准参数"""
    target_component: str = "fuselage"      # 目标部件
    impact_point: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # 撞击点坐标
    beam_direction: Tuple[float, float, float] = (1.0, 0.0, 0.0)  # 光束方向
    incident_angle: float = 0.0             # 入射角 (度)
    spot_size: float = 0.01                 # 光斑尺寸 (m)
    irradiation_time: float = 1.0           # 照射时间 (s)

@dataclass
class DamageAssessmentCriteria:
    """毁伤评估准则"""
    melting_temperature: float = 933.0      # 熔化温度 (K)
    vaporization_temperature: float = 2740.0  # 汽化温度 (K)
    critical_stress: float = 500e6          # 临界应力 (Pa)
    structural_failure_strain: float = 0.02 # 结构失效应变
    thermal_shock_threshold: float = 100.0  # 热冲击阈值 (K/s)

class AircraftLaserDamageSimulator(BaseSimulator):
    """飞行器激光毁伤仿真器"""
    
    def __init__(self):
        super().__init__("AircraftLaserDamageSimulator")
        
        # 子模块
        self.mesh_generator = MeshGenerator()
        self.fluid_setup = FluidDomainSetup()
        
        # 仿真数据
        self.aircraft_model: Optional[Dict[str, Any]] = None
        self.laser_params: Optional[LaserParameters] = None
        self.targeting_params: Optional[LaserTargetingParameters] = None
        self.flight_conditions: Optional[FlightConditions] = None
        
        # 网格数据
        self.aircraft_mesh: Optional[Dict[str, Any]] = None
        self.fluid_domain: Optional[Dict[str, Any]] = None
        
        # 仿真结果
        self.damage_results: Dict[str, Any] = {}
        
    def setup_aircraft_model(self, aircraft_model: Dict[str, Any]) -> bool:
        """设置飞行器模型"""
        try:
            self.log_info(f"设置飞行器模型: {aircraft_model.get('metadata', {}).get('name', 'Unknown')}")
            
            # 验证模型数据
            if not self._validate_aircraft_model(aircraft_model):
                raise ValueError("飞行器模型数据无效")
            
            self.aircraft_model = aircraft_model
            
            # 生成飞行器网格
            mesh_params = MeshParameters(
                max_element_size=0.05,
                min_element_size=0.001,
                boundary_layer_count=5,
                boundary_layer_thickness=0.001
            )
            
            self.aircraft_mesh = self.mesh_generator.generate_adaptive_mesh(
                aircraft_model, mesh_params
            )
            
            self.log_info("飞行器模型设置完成")
            return True
            
        except Exception as e:
            self.log_error(f"飞行器模型设置失败: {e}")
            return False
    
    def setup_laser_parameters(self, laser_params: LaserParameters,
                              targeting_params: LaserTargetingParameters) -> bool:
        """设置激光参数"""
        try:
            self.log_info("设置激光参数...")
            
            self.laser_params = laser_params
            self.targeting_params = targeting_params
            
            # 验证激光参数
            if not self._validate_laser_parameters():
                raise ValueError("激光参数无效")
            
            # 计算激光功率密度
            spot_area = np.pi * (targeting_params.spot_size / 2) ** 2
            power_density = laser_params.power / spot_area
            
            self.log_info(f"激光功率密度: {power_density:.2e} W/m²")
            
            if power_density > 1e9:  # 超过1 GW/m²
                self.log_warning("激光功率密度极高，可能导致瞬间汽化")
            
            return True
            
        except Exception as e:
            self.log_error(f"激光参数设置失败: {e}")
            return False
    
    def setup_flight_conditions(self, flight_conditions: FlightConditions) -> bool:
        """设置飞行条件"""
        try:
            self.log_info("设置飞行条件...")
            
            self.flight_conditions = flight_conditions
            
            # 创建流体域
            if self.aircraft_model:
                from aircraft_modeling.fluid_domain_setup import DomainParameters
                
                domain_params = DomainParameters(
                    upstream_distance=5.0,
                    downstream_distance=10.0,
                    lateral_distance=5.0,
                    vertical_distance=5.0
                )
                
                self.fluid_domain = self.fluid_setup.create_external_flow_domain(
                    self.aircraft_model, flight_conditions, domain_params
                )
            
            self.log_info("飞行条件设置完成")
            return True
            
        except Exception as e:
            self.log_error(f"飞行条件设置失败: {e}")
            return False
    
    def run_thermal_analysis(self) -> Dict[str, Any]:
        """运行热分析"""
        try:
            self.log_info("开始热分析...")
            
            # 确定激光照射区域
            irradiation_zone = self._identify_irradiation_zone()
            
            # 计算激光热源
            heat_source = self._calculate_laser_heat_source(irradiation_zone)
            
            # 设置热边界条件
            thermal_bc = self._setup_thermal_boundary_conditions()
            
            # 求解热传导方程
            thermal_results = self._solve_heat_transfer(heat_source, thermal_bc)
            
            # 分析温度分布
            temperature_analysis = self._analyze_temperature_distribution(thermal_results)
            
            # 识别毁伤区域
            damage_zones = self._identify_thermal_damage_zones(thermal_results)
            
            results = {
                'status': 'success',
                'irradiation_zone': irradiation_zone,
                'heat_source': heat_source,
                'thermal_results': thermal_results,
                'temperature_analysis': temperature_analysis,
                'damage_zones': damage_zones,
                'computation_time': 0.0  # 实际计算时间
            }
            
            self.damage_results['thermal_analysis'] = results
            self.log_info("热分析完成")
            return results
            
        except Exception as e:
            self.log_error(f"热分析失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_structural_analysis(self) -> Dict[str, Any]:
        """运行结构分析"""
        try:
            self.log_info("开始结构分析...")
            
            # 获取热分析结果
            thermal_results = self.damage_results.get('thermal_analysis', {})
            if not thermal_results or thermal_results.get('status') != 'success':
                raise ValueError("需要先完成热分析")
            
            # 计算热应力
            thermal_stress = self._calculate_thermal_stress(thermal_results)
            
            # 计算气动载荷
            aerodynamic_loads = self._calculate_aerodynamic_loads()
            
            # 组合载荷
            combined_loads = self._combine_loads(thermal_stress, aerodynamic_loads)
            
            # 求解结构响应
            structural_response = self._solve_structural_response(combined_loads)
            
            # 分析应力分布
            stress_analysis = self._analyze_stress_distribution(structural_response)
            
            # 评估结构完整性
            structural_integrity = self._assess_structural_integrity(structural_response)
            
            results = {
                'status': 'success',
                'thermal_stress': thermal_stress,
                'aerodynamic_loads': aerodynamic_loads,
                'combined_loads': combined_loads,
                'structural_response': structural_response,
                'stress_analysis': stress_analysis,
                'structural_integrity': structural_integrity,
                'computation_time': 0.0
            }
            
            self.damage_results['structural_analysis'] = results
            self.log_info("结构分析完成")
            return results
            
        except Exception as e:
            self.log_error(f"结构分析失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_aerodynamic_impact_analysis(self) -> Dict[str, Any]:
        """运行气动影响分析"""
        try:
            self.log_info("开始气动影响分析...")
            
            # 获取结构分析结果
            structural_results = self.damage_results.get('structural_analysis', {})
            if not structural_results or structural_results.get('status') != 'success':
                raise ValueError("需要先完成结构分析")
            
            # 分析几何变形对气动性能的影响
            geometry_changes = self._analyze_geometry_changes(structural_results)
            
            # 计算气动系数变化
            aerodynamic_changes = self._calculate_aerodynamic_changes(geometry_changes)
            
            # 评估飞行性能影响
            flight_performance_impact = self._assess_flight_performance_impact(aerodynamic_changes)
            
            # 分析稳定性变化
            stability_changes = self._analyze_stability_changes(aerodynamic_changes)
            
            results = {
                'status': 'success',
                'geometry_changes': geometry_changes,
                'aerodynamic_changes': aerodynamic_changes,
                'flight_performance_impact': flight_performance_impact,
                'stability_changes': stability_changes,
                'computation_time': 0.0
            }
            
            self.damage_results['aerodynamic_impact'] = results
            self.log_info("气动影响分析完成")
            return results
            
        except Exception as e:
            self.log_error(f"气动影响分析失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_comprehensive_damage_assessment(self) -> Dict[str, Any]:
        """运行综合毁伤评估"""
        try:
            self.log_info("开始综合毁伤评估...")
            
            # 收集所有分析结果
            thermal_results = self.damage_results.get('thermal_analysis', {})
            structural_results = self.damage_results.get('structural_analysis', {})
            aerodynamic_results = self.damage_results.get('aerodynamic_impact', {})
            
            # 综合毁伤等级评估
            damage_level = self._assess_overall_damage_level(
                thermal_results, structural_results, aerodynamic_results
            )
            
            # 关键部件影响分析
            critical_component_impact = self._analyze_critical_component_impact()
            
            # 任务能力评估
            mission_capability = self._assess_mission_capability(damage_level)
            
            # 生存能力评估
            survivability = self._assess_survivability(damage_level)
            
            # 对抗建议
            countermeasures = self._generate_countermeasure_recommendations(damage_level)
            
            results = {
                'status': 'success',
                'overall_damage_level': damage_level,
                'critical_component_impact': critical_component_impact,
                'mission_capability': mission_capability,
                'survivability': survivability,
                'countermeasures': countermeasures,
                'assessment_time': self.get_current_time()
            }
            
            self.damage_results['comprehensive_assessment'] = results
            self.log_info("综合毁伤评估完成")
            return results
            
        except Exception as e:
            self.log_error(f"综合毁伤评估失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def run_complete_simulation(self) -> Dict[str, Any]:
        """运行完整仿真"""
        try:
            self.log_info("开始完整激光毁伤仿真...")
            
            # 验证设置
            if not self._validate_simulation_setup():
                raise ValueError("仿真设置不完整")
            
            # 按顺序执行各个分析
            thermal_results = self.run_thermal_analysis()
            if thermal_results.get('status') != 'success':
                raise RuntimeError("热分析失败")
            
            structural_results = self.run_structural_analysis()
            if structural_results.get('status') != 'success':
                raise RuntimeError("结构分析失败")
            
            aerodynamic_results = self.run_aerodynamic_impact_analysis()
            if aerodynamic_results.get('status') != 'success':
                raise RuntimeError("气动影响分析失败")
            
            assessment_results = self.run_comprehensive_damage_assessment()
            if assessment_results.get('status') != 'success':
                raise RuntimeError("综合毁伤评估失败")
            
            # 生成仿真摘要
            simulation_summary = self._generate_simulation_summary()
            
            complete_results = {
                'status': 'success',
                'simulation_summary': simulation_summary,
                'thermal_analysis': thermal_results,
                'structural_analysis': structural_results,
                'aerodynamic_impact': aerodynamic_results,
                'comprehensive_assessment': assessment_results,
                'total_computation_time': 0.0,
                'completion_time': self.get_current_time()
            }
            
            self.log_info("完整激光毁伤仿真完成")
            return complete_results
            
        except Exception as e:
            self.log_error(f"完整仿真失败: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def get_simulation_results(self) -> Dict[str, Any]:
        """获取仿真结果"""
        return self.damage_results.copy()
    
    def export_results(self, output_dir: str, formats: List[str] = None) -> bool:
        """导出结果"""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            formats = formats or ['json', 'vtk', 'csv']
            
            for format_type in formats:
                if format_type == 'json':
                    self._export_json_results(output_path)
                elif format_type == 'vtk':
                    self._export_vtk_results(output_path)
                elif format_type == 'csv':
                    self._export_csv_results(output_path)
            
            self.log_info(f"结果已导出到: {output_path}")
            return True
            
        except Exception as e:
            self.log_error(f"结果导出失败: {e}")
            return False

    # 验证方法
    def _validate_aircraft_model(self, aircraft_model: Dict[str, Any]) -> bool:
        """验证飞行器模型"""
        required_fields = ['type', 'metadata']
        return all(field in aircraft_model for field in required_fields)

    def _validate_laser_parameters(self) -> bool:
        """验证激光参数"""
        if not self.laser_params or not self.targeting_params:
            return False

        # 检查功率范围
        if self.laser_params.power <= 0 or self.laser_params.power > 1e6:
            return False

        # 检查波长范围
        if self.laser_params.wavelength <= 0 or self.laser_params.wavelength > 10000:
            return False

        return True

    def _validate_simulation_setup(self) -> bool:
        """验证仿真设置"""
        return all([
            self.aircraft_model is not None,
            self.laser_params is not None,
            self.targeting_params is not None,
            self.aircraft_mesh is not None
        ])

    # 热分析相关方法
    def _identify_irradiation_zone(self) -> Dict[str, Any]:
        """识别激光照射区域"""
        impact_point = self.targeting_params.impact_point
        spot_size = self.targeting_params.spot_size

        return {
            'center': impact_point,
            'radius': spot_size / 2,
            'area': np.pi * (spot_size / 2) ** 2,
            'target_component': self.targeting_params.target_component
        }

    def _calculate_laser_heat_source(self, irradiation_zone: Dict[str, Any]) -> Dict[str, Any]:
        """计算激光热源"""
        power = self.laser_params.power
        area = irradiation_zone['area']

        # 考虑材料吸收率
        absorptivity = 0.15  # 铝合金典型值，实际应从材料数据获取

        absorbed_power = power * absorptivity
        heat_flux = absorbed_power / area

        return {
            'total_power': power,
            'absorbed_power': absorbed_power,
            'heat_flux': heat_flux,
            'absorptivity': absorptivity,
            'distribution': 'gaussian'  # 高斯分布
        }

    def _setup_thermal_boundary_conditions(self) -> Dict[str, Any]:
        """设置热边界条件"""
        # 基于飞行条件设置边界条件
        if self.flight_conditions:
            ambient_temp = self.flight_conditions.temperature
            convection_coeff = self._calculate_convection_coefficient()
        else:
            ambient_temp = 288.15  # 标准大气温度
            convection_coeff = 25.0  # 典型对流换热系数

        return {
            'ambient_temperature': ambient_temp,
            'convection_coefficient': convection_coeff,
            'radiation_emissivity': 0.8,
            'initial_temperature': ambient_temp
        }

    def _calculate_convection_coefficient(self) -> float:
        """计算对流换热系数"""
        if not self.flight_conditions:
            return 25.0

        # 基于飞行速度和高度的简化计算
        velocity = self.flight_conditions.velocity
        altitude = self.flight_conditions.altitude

        # 简化的对流换热系数计算
        h = 10.0 + 0.1 * velocity - 0.001 * altitude
        return max(h, 5.0)  # 最小值5 W/m²K

    def _solve_heat_transfer(self, heat_source: Dict[str, Any],
                            thermal_bc: Dict[str, Any]) -> Dict[str, Any]:
        """求解传热方程"""
        # 简化的传热求解
        max_temperature = thermal_bc['ambient_temperature'] + heat_source['heat_flux'] / 1000

        return {
            'max_temperature': max_temperature,
            'temperature_field': self._generate_temperature_field(max_temperature),
            'heat_flux_field': self._generate_heat_flux_field(heat_source),
            'time_to_steady_state': 10.0  # 秒
        }

    def _analyze_temperature_distribution(self, thermal_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析温度分布"""
        max_temp = thermal_results['max_temperature']

        # 温度分析
        analysis = {
            'max_temperature': max_temp,
            'temperature_gradient': max_temp / 0.01,  # 简化梯度
            'thermal_penetration_depth': 0.005,  # 5mm
            'affected_volume': 0.001  # 1 cm³
        }

        return analysis

    def _identify_thermal_damage_zones(self, thermal_results: Dict[str, Any]) -> Dict[str, Any]:
        """识别热毁伤区域"""
        max_temp = thermal_results['max_temperature']

        damage_zones = {
            'no_damage': {'temperature_range': (0, 373), 'volume': 0.0},
            'heating': {'temperature_range': (373, 933), 'volume': 0.0},
            'melting': {'temperature_range': (933, 2740), 'volume': 0.0},
            'vaporization': {'temperature_range': (2740, float('inf')), 'volume': 0.0}
        }

        # 简化的毁伤区域计算
        if max_temp > 2740:
            damage_zones['vaporization']['volume'] = 0.0001
        elif max_temp > 933:
            damage_zones['melting']['volume'] = 0.0005
        elif max_temp > 373:
            damage_zones['heating']['volume'] = 0.001

        return damage_zones

    # 结构分析相关方法
    def _calculate_thermal_stress(self, thermal_results: Dict[str, Any]) -> Dict[str, Any]:
        """计算热应力"""
        thermal_data = thermal_results.get('thermal_results', {})
        max_temp = thermal_data.get('max_temperature', 288.15)

        # 从温度分析中获取梯度
        temp_analysis = thermal_results.get('temperature_analysis', {})
        temp_gradient = temp_analysis.get('temperature_gradient', 0)

        # 材料属性（铝合金）
        thermal_expansion = 22.3e-6  # 1/K
        youngs_modulus = 73.1e9     # Pa

        # 热应力计算
        thermal_strain = thermal_expansion * (max_temp - 288.15)
        thermal_stress = youngs_modulus * thermal_strain

        return {
            'max_thermal_stress': thermal_stress,
            'thermal_strain': thermal_strain,
            'stress_distribution': 'concentrated',
            'affected_area': 0.01  # m²
        }

    def _calculate_aerodynamic_loads(self) -> Dict[str, Any]:
        """计算气动载荷"""
        if not self.flight_conditions:
            return {'pressure_loads': {}, 'shear_loads': {}}

        # 简化的气动载荷计算
        dynamic_pressure = 0.5 * self.flight_conditions.density * self.flight_conditions.velocity**2

        return {
            'dynamic_pressure': dynamic_pressure,
            'pressure_loads': {
                'fuselage': dynamic_pressure * 0.5,
                'wings': dynamic_pressure * 1.0,
                'tail': dynamic_pressure * 0.3
            },
            'shear_loads': {
                'fuselage': dynamic_pressure * 0.1,
                'wings': dynamic_pressure * 0.2
            }
        }

    def _combine_loads(self, thermal_stress: Dict[str, Any],
                      aerodynamic_loads: Dict[str, Any]) -> Dict[str, Any]:
        """组合载荷"""
        return {
            'thermal_contribution': thermal_stress,
            'aerodynamic_contribution': aerodynamic_loads,
            'combined_stress': thermal_stress.get('max_thermal_stress', 0) +
                             aerodynamic_loads.get('dynamic_pressure', 0) * 1000,
            'load_combination_method': 'linear_superposition'
        }

    def _solve_structural_response(self, combined_loads: Dict[str, Any]) -> Dict[str, Any]:
        """求解结构响应"""
        combined_stress = combined_loads.get('combined_stress', 0)

        # 材料属性
        youngs_modulus = 73.1e9
        yield_strength = 324e6

        # 应变计算
        strain = combined_stress / youngs_modulus

        return {
            'max_stress': combined_stress,
            'max_strain': strain,
            'displacement_field': self._generate_displacement_field(strain),
            'plastic_deformation': strain > (yield_strength / youngs_modulus)
        }

    def _analyze_stress_distribution(self, structural_response: Dict[str, Any]) -> Dict[str, Any]:
        """分析应力分布"""
        max_stress = structural_response.get('max_stress', 0)

        return {
            'stress_concentration_factor': 2.5,
            'critical_stress_locations': ['impact_point', 'structural_joints'],
            'stress_intensity': 'high' if max_stress > 300e6 else 'moderate',
            'failure_probability': min(max_stress / 500e6, 1.0)
        }

    def _assess_structural_integrity(self, structural_response: Dict[str, Any]) -> Dict[str, Any]:
        """评估结构完整性"""
        max_stress = structural_response.get('max_stress', 0)
        plastic_deformation = structural_response.get('plastic_deformation', False)

        if plastic_deformation:
            integrity_level = 'compromised'
        elif max_stress > 200e6:
            integrity_level = 'degraded'
        else:
            integrity_level = 'intact'

        return {
            'integrity_level': integrity_level,
            'structural_damage': plastic_deformation,
            'load_carrying_capacity': max(0, 1 - max_stress / 500e6),
            'repair_requirements': 'major' if plastic_deformation else 'minor'
        }

    # 气动影响分析相关方法
    def _analyze_geometry_changes(self, structural_results: Dict[str, Any]) -> Dict[str, Any]:
        """分析几何变形"""
        plastic_deformation = structural_results.get('plastic_deformation', False)
        max_strain = structural_results.get('max_strain', 0)

        return {
            'surface_deformation': plastic_deformation,
            'deformation_magnitude': max_strain * 0.1,  # 简化计算
            'affected_surface_area': 0.01 if plastic_deformation else 0.0,
            'shape_change_type': 'local_depression' if plastic_deformation else 'none'
        }

    def _calculate_aerodynamic_changes(self, geometry_changes: Dict[str, Any]) -> Dict[str, Any]:
        """计算气动系数变化"""
        surface_deformation = geometry_changes.get('surface_deformation', False)

        if not surface_deformation:
            return {
                'lift_coefficient_change': 0.0,
                'drag_coefficient_change': 0.0,
                'moment_coefficient_change': 0.0
            }

        # 简化的气动系数变化计算
        deformation_magnitude = geometry_changes.get('deformation_magnitude', 0)

        return {
            'lift_coefficient_change': -deformation_magnitude * 0.1,
            'drag_coefficient_change': deformation_magnitude * 0.2,
            'moment_coefficient_change': deformation_magnitude * 0.05,
            'flow_separation': deformation_magnitude > 0.001
        }

    def _assess_flight_performance_impact(self, aerodynamic_changes: Dict[str, Any]) -> Dict[str, Any]:
        """评估飞行性能影响"""
        drag_change = aerodynamic_changes.get('drag_coefficient_change', 0)
        lift_change = aerodynamic_changes.get('lift_coefficient_change', 0)

        return {
            'range_reduction': abs(drag_change) * 100,  # 百分比
            'fuel_consumption_increase': abs(drag_change) * 50,  # 百分比
            'maneuverability_impact': abs(lift_change) * 80,  # 百分比
            'performance_degradation_level': 'severe' if abs(drag_change) > 0.1 else 'moderate'
        }

    def _analyze_stability_changes(self, aerodynamic_changes: Dict[str, Any]) -> Dict[str, Any]:
        """分析稳定性变化"""
        moment_change = aerodynamic_changes.get('moment_coefficient_change', 0)

        return {
            'longitudinal_stability_change': moment_change,
            'lateral_stability_impact': abs(moment_change) * 0.5,
            'control_authority_reduction': abs(moment_change) * 100,  # 百分比
            'stability_margin_reduction': abs(moment_change) * 200  # 百分比
        }

    # 综合评估相关方法
    def _assess_overall_damage_level(self, thermal_results: Dict[str, Any],
                                   structural_results: Dict[str, Any],
                                   aerodynamic_results: Dict[str, Any]) -> Dict[str, Any]:
        """评估总体毁伤等级"""
        # 热毁伤评分
        thermal_score = self._calculate_thermal_damage_score(thermal_results)

        # 结构毁伤评分
        structural_score = self._calculate_structural_damage_score(structural_results)

        # 气动影响评分
        aerodynamic_score = self._calculate_aerodynamic_impact_score(aerodynamic_results)

        # 综合评分
        overall_score = max(thermal_score, structural_score, aerodynamic_score)

        # 毁伤等级
        if overall_score >= 0.8:
            damage_level = "致命"
        elif overall_score >= 0.6:
            damage_level = "严重"
        elif overall_score >= 0.4:
            damage_level = "中等"
        elif overall_score >= 0.2:
            damage_level = "轻微"
        else:
            damage_level = "无毁伤"

        return {
            'overall_damage_level': damage_level,
            'overall_score': overall_score,
            'thermal_score': thermal_score,
            'structural_score': structural_score,
            'aerodynamic_score': aerodynamic_score,
            'dominant_damage_mode': self._identify_dominant_damage_mode(
                thermal_score, structural_score, aerodynamic_score
            )
        }

    def _analyze_critical_component_impact(self) -> Dict[str, Any]:
        """分析关键部件影响"""
        target_component = self.targeting_params.target_component

        component_criticality = {
            'fuselage': 0.8,
            'wings': 0.9,
            'tail': 0.7,
            'engine': 1.0,
            'cockpit': 1.0,
            'fuel_tank': 0.9
        }

        criticality = component_criticality.get(target_component, 0.5)

        return {
            'target_component': target_component,
            'component_criticality': criticality,
            'mission_impact_factor': criticality,
            'repair_complexity': 'high' if criticality > 0.8 else 'medium',
            'replacement_required': criticality > 0.9
        }

    def _assess_mission_capability(self, damage_level: Dict[str, Any]) -> Dict[str, Any]:
        """评估任务能力"""
        overall_score = damage_level.get('overall_score', 0)

        mission_capability = max(0, 1 - overall_score)

        return {
            'mission_capability_remaining': mission_capability,
            'mission_abort_required': overall_score > 0.7,
            'emergency_landing_required': overall_score > 0.5,
            'continued_operation_possible': overall_score < 0.3,
            'mission_success_probability': mission_capability
        }

    def _assess_survivability(self, damage_level: Dict[str, Any]) -> Dict[str, Any]:
        """评估生存能力"""
        overall_score = damage_level.get('overall_score', 0)

        return {
            'structural_survivability': max(0, 1 - overall_score * 1.2),
            'flight_survivability': max(0, 1 - overall_score),
            'crew_survivability': max(0, 1 - overall_score * 0.8),
            'recovery_probability': max(0, 1 - overall_score * 1.5),
            'time_to_critical_failure': max(0, 3600 * (1 - overall_score))  # 秒
        }

    def _generate_countermeasure_recommendations(self, damage_level: Dict[str, Any]) -> List[str]:
        """生成对抗措施建议"""
        overall_score = damage_level.get('overall_score', 0)
        recommendations = []

        if overall_score > 0.8:
            recommendations.extend([
                "立即执行紧急程序",
                "寻找最近机场紧急降落",
                "启动应急通信系统"
            ])
        elif overall_score > 0.6:
            recommendations.extend([
                "评估飞行控制能力",
                "准备应急降落程序",
                "监控结构完整性"
            ])
        elif overall_score > 0.4:
            recommendations.extend([
                "调整飞行参数",
                "避免高机动动作",
                "监控系统状态"
            ])
        elif overall_score > 0.2:
            recommendations.extend([
                "继续监控",
                "记录损伤情况",
                "准备维修计划"
            ])

        return recommendations

    def _generate_simulation_summary(self) -> Dict[str, Any]:
        """生成仿真摘要"""
        return {
            'aircraft_model': self.aircraft_model.get('metadata', {}).get('name', 'Unknown'),
            'laser_power': self.laser_params.power if self.laser_params else 0,
            'target_component': self.targeting_params.target_component if self.targeting_params else 'Unknown',
            'simulation_modules': list(self.damage_results.keys()),
            'overall_status': 'success' if all(
                result.get('status') == 'success'
                for result in self.damage_results.values()
            ) else 'partial_success'
        }

    # 辅助计算方法
    def _calculate_thermal_damage_score(self, thermal_results: Dict[str, Any]) -> float:
        """计算热毁伤评分"""
        if thermal_results.get('status') != 'success':
            return 0.0

        max_temp = thermal_results.get('thermal_results', {}).get('max_temperature', 288.15)

        if max_temp > 2740:  # 汽化
            return 1.0
        elif max_temp > 933:  # 熔化
            return 0.8
        elif max_temp > 373:  # 加热
            return 0.3
        else:
            return 0.0

    def _calculate_structural_damage_score(self, structural_results: Dict[str, Any]) -> float:
        """计算结构毁伤评分"""
        if structural_results.get('status') != 'success':
            return 0.0

        plastic_deformation = structural_results.get('structural_response', {}).get('plastic_deformation', False)
        max_stress = structural_results.get('structural_response', {}).get('max_stress', 0)

        if plastic_deformation:
            return 0.8
        elif max_stress > 300e6:
            return 0.6
        elif max_stress > 200e6:
            return 0.4
        else:
            return 0.0

    def _calculate_aerodynamic_impact_score(self, aerodynamic_results: Dict[str, Any]) -> float:
        """计算气动影响评分"""
        if aerodynamic_results.get('status') != 'success':
            return 0.0

        performance_impact = aerodynamic_results.get('flight_performance_impact', {})
        degradation_level = performance_impact.get('performance_degradation_level', 'none')

        if degradation_level == 'severe':
            return 0.7
        elif degradation_level == 'moderate':
            return 0.4
        else:
            return 0.1

    def _identify_dominant_damage_mode(self, thermal_score: float,
                                     structural_score: float,
                                     aerodynamic_score: float) -> str:
        """识别主导毁伤模式"""
        scores = {
            'thermal': thermal_score,
            'structural': structural_score,
            'aerodynamic': aerodynamic_score
        }

        return max(scores, key=scores.get)

    # 数据生成方法（简化实现）
    def _generate_temperature_field(self, max_temperature: float) -> List[float]:
        """生成温度场数据"""
        # 简化的温度场生成
        return [max_temperature * np.exp(-i*0.1) for i in range(100)]

    def _generate_heat_flux_field(self, heat_source: Dict[str, Any]) -> List[float]:
        """生成热流场数据"""
        max_flux = heat_source.get('heat_flux', 0)
        return [max_flux * np.exp(-i*0.1) for i in range(100)]

    def _generate_displacement_field(self, max_strain: float) -> List[float]:
        """生成位移场数据"""
        max_displacement = max_strain * 0.1  # 简化计算
        return [max_displacement * np.exp(-i*0.1) for i in range(100)]

    # 导出方法
    def _export_json_results(self, output_path: Path):
        """导出JSON格式结果"""
        import json

        output_file = output_path / "laser_damage_results.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.damage_results, f, indent=2, ensure_ascii=False, default=str)

    def _export_vtk_results(self, output_path: Path):
        """导出VTK格式结果"""
        # VTK导出实现（简化）
        self.log_info("VTK导出功能需要进一步实现")

    def _export_csv_results(self, output_path: Path):
        """导出CSV格式结果"""
        import csv

        output_file = output_path / "laser_damage_summary.csv"

        # 提取关键数据
        summary_data = []
        for module, results in self.damage_results.items():
            if results.get('status') == 'success':
                summary_data.append({
                    'module': module,
                    'status': results['status'],
                    'computation_time': results.get('computation_time', 0)
                })

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if summary_data:
                writer = csv.DictWriter(f, fieldnames=summary_data[0].keys())
                writer.writeheader()
                writer.writerows(summary_data)

    # 实现BaseSimulator的抽象方法
    def setup_simulation(self, **kwargs) -> bool:
        """设置仿真参数"""
        aircraft_model = kwargs.get('aircraft_model')
        laser_params = kwargs.get('laser_params')
        targeting_params = kwargs.get('targeting_params')
        flight_conditions = kwargs.get('flight_conditions')

        success = True
        if aircraft_model:
            success &= self.setup_aircraft_model(aircraft_model)
        if laser_params and targeting_params:
            success &= self.setup_laser_parameters(laser_params, targeting_params)
        if flight_conditions:
            success &= self.setup_flight_conditions(flight_conditions)

        return success

    def run_simulation(self) -> bool:
        """运行仿真"""
        try:
            results = self.run_complete_simulation()
            return results.get('status') == 'success'
        except Exception as e:
            self.log_error(f"仿真运行失败: {e}")
            return False

    def get_results(self) -> Dict[str, Any]:
        """获取仿真结果"""
        return self.damage_results

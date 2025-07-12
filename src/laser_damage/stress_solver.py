"""
激光毁伤仿真 - 应力分析求解器

基于ANSYS MAPDL的热应力分析求解器。
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))
from core.exceptions import SimulationError, ANSYSConnectionError

# PyANSYS导入
try:
    import ansys.mapdl.core as pymapdl
    MAPDL_AVAILABLE = True
except ImportError:
    MAPDL_AVAILABLE = False
    print("PyMAPDL不可用，应力分析功能将受限")

class StressSolver:
    """应力分析求解器"""
    
    def __init__(self):
        self.mapdl = None
        self.is_setup = False
        self.geometry_data = None
        self.material_model = None
        self.boundary_conditions = None
        self.settings = None
        
    def setup(self, geometry, material, boundary_conditions, settings) -> bool:
        """设置应力分析参数"""
        try:
            if not MAPDL_AVAILABLE:
                raise ANSYSConnectionError("PyMAPDL不可用")
            
            # 保存参数
            self.geometry_data = geometry
            self.material_model = material
            self.boundary_conditions = boundary_conditions
            self.settings = settings
            
            # 启动MAPDL
            self._start_mapdl()
            
            # 设置分析类型
            self._setup_analysis_type()
            
            # 创建几何和网格
            self._create_geometry_and_mesh()
            
            # 定义材料属性
            self._define_material_properties()
            
            # 应用边界条件
            self._apply_boundary_conditions()
            
            self.is_setup = True
            return True
            
        except Exception as e:
            print(f"应力分析设置失败: {e}")
            return False
    
    def _start_mapdl(self):
        """启动MAPDL会话"""
        try:
            self.mapdl = pymapdl.launch_mapdl(
                run_location="./ansys_work",
                nproc=self.settings.parallel_cores if self.settings else 4,
                override=True,
                additional_switches="-smp"
            )
            
            # 设置单位制
            self.mapdl.prep7()  # 进入前处理器
            self.mapdl.units("SI")  # 设置SI单位制
            
        except Exception as e:
            raise ANSYSConnectionError(f"MAPDL启动失败: {e}")
    
    def _setup_analysis_type(self):
        """设置分析类型"""
        # 设置为静态结构分析
        self.mapdl.antype("STATIC")
    
    def _create_geometry_and_mesh(self):
        """创建几何和网格"""
        try:
            # 简化几何创建 - 创建一个长方体
            if self.geometry_data:
                length, width, height = self.geometry_data.dimensions
                
                # 创建关键点
                self.mapdl.k(1, 0, 0, 0)
                self.mapdl.k(2, length, 0, 0)
                self.mapdl.k(3, length, width, 0)
                self.mapdl.k(4, 0, width, 0)
                self.mapdl.k(5, 0, 0, height)
                self.mapdl.k(6, length, 0, height)
                self.mapdl.k(7, length, width, height)
                self.mapdl.k(8, 0, width, height)
                
                # 创建体
                self.mapdl.v(1, 2, 3, 4, 5, 6, 7, 8)
                
                # 设置单元类型 - 结构分析单元
                self.mapdl.et(1, "SOLID185")  # 3D结构单元
                
                # 设置网格尺寸
                mesh_size = self.geometry_data.mesh_size
                self.mapdl.esize(mesh_size)
                
                # 生成网格
                self.mapdl.vmesh("ALL")
                
        except Exception as e:
            raise SimulationError(f"几何和网格创建失败: {e}")
    
    def _define_material_properties(self):
        """定义材料属性"""
        try:
            if self.material_model:
                # 材料1 - 结构属性
                self.mapdl.mp("EX", 1, self.material_model.youngs_modulus)      # 杨氏模量
                self.mapdl.mp("PRXY", 1, self.material_model.poissons_ratio)   # 泊松比
                self.mapdl.mp("DENS", 1, self.material_model.density)          # 密度
                self.mapdl.mp("ALPX", 1, self.material_model.thermal_expansion) # 热膨胀系数
                
                # 分配材料到所有单元
                self.mapdl.mat(1)
                self.mapdl.emodif("ALL")
                
        except Exception as e:
            raise SimulationError(f"材料属性定义失败: {e}")
    
    def _apply_boundary_conditions(self):
        """应用边界条件"""
        try:
            if self.boundary_conditions:
                # 应用固定约束
                for constraint in self.boundary_conditions.fixed_constraints:
                    if constraint == "bottom_fixed":
                        # 固定底面
                        self.mapdl.nsel("S", "LOC", "Z", 0)
                        self.mapdl.d("ALL", "ALL", 0)
                        self.mapdl.allsel()
                
                # 应用压力载荷
                for surface, pressure in self.boundary_conditions.pressure_loads.items():
                    if surface == "top":
                        self.mapdl.asel("S", "LOC", "Z", self.geometry_data.dimensions[2])
                        self.mapdl.sfa("ALL", "", "PRES", pressure)
                        self.mapdl.allsel()
                
        except Exception as e:
            raise SimulationError(f"边界条件应用失败: {e}")
    
    def solve(self, thermal_results: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """执行应力分析求解"""
        if not self.is_setup:
            raise SimulationError("应力分析未设置")
        
        try:
            start_time = time.time()
            
            # 如果有热分析结果，应用热载荷
            if thermal_results:
                self._apply_thermal_load(thermal_results)
            
            # 进入求解器
            self.mapdl.slashsolu()
            
            # 设置求解选项
            if self.settings:
                self.mapdl.neqit(self.settings.max_iterations)
                self.mapdl.cnvtol("F", "", self.settings.convergence_tolerance)
            
            # 求解
            self.mapdl.solve()
            self.mapdl.finish()
            
            # 进入后处理器
            self.mapdl.post1()
            
            # 提取结果
            results = self._extract_results()
            
            computation_time = time.time() - start_time
            results['computation_time'] = computation_time
            
            return results
            
        except Exception as e:
            raise SimulationError(f"应力分析求解失败: {e}")
    
    def _apply_thermal_load(self, thermal_results: Dict):
        """应用热载荷"""
        try:
            # 从热分析结果中提取温度场
            temperature_field = thermal_results.get('temperature_field')
            
            if temperature_field is not None:
                # 应用节点温度载荷
                # 这里简化处理，实际应用中需要将温度场映射到结构网格
                
                # 设置参考温度（无应力温度）
                ref_temp = self.boundary_conditions.ambient_temperature if self.boundary_conditions else 293.15
                self.mapdl.tref(ref_temp)
                
                # 应用温度载荷
                # 简化：假设均匀温度分布
                avg_temp = np.mean(temperature_field) if len(temperature_field) > 0 else ref_temp
                self.mapdl.bf("ALL", "TEMP", avg_temp)
                
        except Exception as e:
            print(f"热载荷应用失败: {e}")
    
    def _extract_results(self) -> Dict[str, Any]:
        """提取应力分析结果"""
        try:
            results = {}
            
            # 设置到最后一个载荷步
            self.mapdl.set("LAST")
            
            # 提取节点位移
            displacements = self.mapdl.post_processing.nodal_displacement()
            results['displacement_field'] = displacements
            
            # 提取节点应力
            stresses = self.mapdl.post_processing.nodal_stress()
            results['stress_field'] = stresses
            
            # 计算最大应力
            if len(stresses) > 0:
                # 计算von Mises应力
                von_mises_stress = self._calculate_von_mises_stress(stresses)
                results['von_mises_stress'] = von_mises_stress
                results['max_stress'] = np.max(von_mises_stress)
            else:
                results['max_stress'] = 0.0
            
            # 获取节点坐标
            nodes = self.mapdl.mesh.nodes
            results['node_coordinates'] = nodes
            
            # 获取单元信息
            elements = self.mapdl.mesh.elements
            results['elements'] = elements
            
            return results
            
        except Exception as e:
            print(f"结果提取失败: {e}")
            return {}
    
    def _calculate_von_mises_stress(self, stress_tensor: np.ndarray) -> np.ndarray:
        """计算von Mises应力"""
        try:
            # 假设stress_tensor的格式为 [sx, sy, sz, sxy, syz, sxz]
            if stress_tensor.shape[1] >= 6:
                sx = stress_tensor[:, 0]
                sy = stress_tensor[:, 1]
                sz = stress_tensor[:, 2]
                sxy = stress_tensor[:, 3]
                syz = stress_tensor[:, 4]
                sxz = stress_tensor[:, 5]
                
                # von Mises应力公式
                von_mises = np.sqrt(0.5 * (
                    (sx - sy)**2 + (sy - sz)**2 + (sz - sx)**2 +
                    6 * (sxy**2 + syz**2 + sxz**2)
                ))
                
                return von_mises
            else:
                # 简化处理
                return np.linalg.norm(stress_tensor, axis=1)
                
        except Exception as e:
            print(f"von Mises应力计算失败: {e}")
            return np.zeros(stress_tensor.shape[0])
    
    def cleanup(self):
        """清理资源"""
        try:
            if self.mapdl:
                self.mapdl.exit()
                self.mapdl = None
        except:
            pass
    
    def __del__(self):
        """析构函数"""
        self.cleanup()

"""
激光毁伤仿真 - 热分析求解器

基于ANSYS MAPDL的热传导分析求解器。
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
    print("PyMAPDL不可用，热分析功能将受限")

class ThermalSolver:
    """热分析求解器"""
    
    def __init__(self):
        self.mapdl = None
        self.is_setup = False
        self.geometry_data = None
        self.material_model = None
        self.laser_model = None
        self.boundary_conditions = None
        self.settings = None
        
    def setup(self, geometry, material, laser, boundary_conditions, settings) -> bool:
        """设置热分析参数"""
        try:
            if not MAPDL_AVAILABLE:
                raise ANSYSConnectionError("PyMAPDL不可用")
            
            # 保存参数
            self.geometry_data = geometry
            self.material_model = material
            self.laser_model = laser
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
            
            # 应用激光载荷
            self._apply_laser_load()
            
            self.is_setup = True
            return True
            
        except Exception as e:
            print(f"热分析设置失败: {e}")
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
        # 设置为瞬态热分析
        self.mapdl.antype("TRANS")  # 瞬态分析
        
        # 设置时间步参数
        if self.settings:
            self.mapdl.time(self.settings.total_time)
            self.mapdl.deltim(self.settings.time_step)
            self.mapdl.autots("ON")  # 自动时间步
    
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
                
                # 设置单元类型 - 热分析单元
                self.mapdl.et(1, "SOLID70")  # 3D热传导单元
                
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
                # 材料1
                self.mapdl.mp("KXX", 1, self.material_model.thermal_conductivity)  # 热导率
                self.mapdl.mp("C", 1, self.material_model.specific_heat)          # 比热容
                self.mapdl.mp("DENS", 1, self.material_model.density)             # 密度
                
                # 分配材料到所有单元
                self.mapdl.mat(1)
                self.mapdl.emodif("ALL")
                
        except Exception as e:
            raise SimulationError(f"材料属性定义失败: {e}")
    
    def _apply_boundary_conditions(self):
        """应用边界条件"""
        try:
            if self.boundary_conditions:
                # 初始温度
                self.mapdl.tunif(self.boundary_conditions.ambient_temperature)
                
                # 对流边界条件 - 应用到外表面
                # 这里简化处理，实际应用中需要选择具体的面
                self.mapdl.asel("EXT")  # 选择外表面
                self.mapdl.sfa("ALL", "", "CONV", 
                              self.boundary_conditions.convection_coefficient,
                              self.boundary_conditions.ambient_temperature)
                
                # 辐射边界条件
                self.mapdl.sfa("ALL", "", "RADI", 
                              self.boundary_conditions.radiation_emissivity,
                              self.boundary_conditions.ambient_temperature)
                
                self.mapdl.allsel()  # 选择所有
                
        except Exception as e:
            raise SimulationError(f"边界条件应用失败: {e}")
    
    def _apply_laser_load(self):
        """应用激光载荷"""
        try:
            if self.laser_model:
                # 计算激光功率密度
                power_density = self.laser_model.get_power_density()
                
                # 应用热流载荷到顶面
                # 选择顶面节点（Z = max）
                self.mapdl.nsel("S", "LOC", "Z", self.geometry_data.dimensions[2])
                
                # 应用热流载荷
                self.mapdl.sf("ALL", "HFLUX", power_density)
                
                self.mapdl.allsel()  # 选择所有
                
        except Exception as e:
            raise SimulationError(f"激光载荷应用失败: {e}")
    
    def solve(self) -> Optional[Dict[str, Any]]:
        """执行热分析求解"""
        if not self.is_setup:
            raise SimulationError("热分析未设置")
        
        try:
            start_time = time.time()
            
            # 进入求解器
            self.mapdl.slashsolu()
            
            # 设置求解选项
            if self.settings:
                self.mapdl.neqit(self.settings.max_iterations)
                self.mapdl.cnvtol("TEMP", "", self.settings.convergence_tolerance)
            
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
            raise SimulationError(f"热分析求解失败: {e}")
    
    def _extract_results(self) -> Dict[str, Any]:
        """提取热分析结果"""
        try:
            results = {}
            
            # 获取节点温度
            self.mapdl.set("LAST")  # 设置到最后一个载荷步
            
            # 提取所有节点的温度
            temperatures = self.mapdl.post_processing.nodal_temperature()
            results['temperature_field'] = temperatures
            
            # 计算最高温度
            results['max_temperature'] = np.max(temperatures) if len(temperatures) > 0 else 0.0
            
            # 获取节点坐标
            nodes = self.mapdl.mesh.nodes
            results['node_coordinates'] = nodes
            
            # 获取单元信息
            elements = self.mapdl.mesh.elements
            results['elements'] = elements
            
            # 计算温度梯度（简化）
            if len(temperatures) > 0:
                temp_gradient = np.gradient(temperatures)
                results['temperature_gradient'] = temp_gradient
            
            return results
            
        except Exception as e:
            print(f"结果提取失败: {e}")
            return {}
    
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

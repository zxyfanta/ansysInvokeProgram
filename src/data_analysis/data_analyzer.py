"""
数据分析 - 数据分析器

集成数据提取、图表生成和报告生成的完整数据分析功能。
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np

# 添加路径
sys.path.append(str(Path(__file__).parent.parent))

from .data_extractor import DataExtractor
from .chart_generator import ChartGenerator
from .report_generator import ReportGenerator

class DataAnalyzer:
    """数据分析器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # 子分析器
        self.data_extractor = DataExtractor()
        self.chart_generator = ChartGenerator()
        self.report_generator = ReportGenerator()
        
        # 分析结果存储
        self.extracted_data: Optional[Dict] = None
        self.generated_charts: List[str] = []
        self.analysis_summary: Optional[Dict] = None
    
    def analyze_simulation_results(self, simulation_results: Dict, output_dir: str = "analysis_output") -> Dict[str, Any]:
        """分析仿真结果"""
        try:
            self.logger.info("开始数据分析...")
            
            # 创建输出目录
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 第一步：数据提取
            self.logger.info("提取仿真数据...")
            extracted_data = self._extract_all_data(simulation_results)
            
            if not extracted_data:
                raise ValueError("数据提取失败")
            
            self.extracted_data = extracted_data
            
            # 第二步：生成图表
            self.logger.info("生成分析图表...")
            chart_files = self._generate_all_charts(extracted_data, str(output_path / "charts"))
            self.generated_charts = chart_files
            
            # 第三步：创建分析摘要
            self.logger.info("创建分析摘要...")
            analysis_summary = self._create_analysis_summary(extracted_data)
            self.analysis_summary = analysis_summary
            
            # 第四步：生成报告
            self.logger.info("生成分析报告...")
            report_files = self._generate_reports(extracted_data, chart_files, str(output_path / "reports"))
            
            # 综合结果
            analysis_results = {
                'status': 'success',
                'extracted_data': extracted_data,
                'chart_files': chart_files,
                'report_files': report_files,
                'analysis_summary': analysis_summary,
                'output_directory': str(output_path)
            }
            
            self.logger.info("数据分析完成")
            return analysis_results
            
        except Exception as e:
            self.logger.error(f"数据分析失败: {e}")
            return {
                'status': 'error',
                'error_message': str(e),
                'extracted_data': {},
                'chart_files': [],
                'report_files': [],
                'analysis_summary': {}
            }
    
    def _extract_all_data(self, simulation_results: Dict) -> Dict[str, Any]:
        """提取所有数据"""
        try:
            all_data = {}
            
            # 提取激光毁伤数据
            laser_damage_data = self.data_extractor.extract_laser_damage_data(simulation_results)
            if laser_damage_data:
                all_data['laser_damage'] = laser_damage_data
            
            # 提取毁伤后效数据
            post_damage_data = self.data_extractor.extract_post_damage_data(simulation_results)
            if post_damage_data:
                all_data['post_damage'] = post_damage_data
            
            # 如果有对比数据，提取对比分析
            if 'original_results' in simulation_results and 'damaged_results' in simulation_results:
                comparison_data = self.data_extractor.extract_comparison_data(
                    simulation_results['original_results'],
                    simulation_results['damaged_results']
                )
                if comparison_data:
                    all_data['comparison'] = comparison_data
            
            # 创建汇总统计
            summary_stats = self.data_extractor.create_summary_statistics(all_data)
            if summary_stats:
                all_data['summary_statistics'] = summary_stats
            
            return all_data
            
        except Exception as e:
            self.logger.error(f"数据提取失败: {e}")
            return {}
    
    def _generate_all_charts(self, extracted_data: Dict, charts_dir: str) -> List[str]:
        """生成所有图表"""
        try:
            all_chart_files = []
            
            # 创建图表目录
            charts_path = Path(charts_dir)
            charts_path.mkdir(parents=True, exist_ok=True)
            
            # 生成毁伤分析图表
            if 'laser_damage' in extracted_data:
                damage_charts = self.chart_generator.generate_damage_analysis_charts(
                    extracted_data['laser_damage'], 
                    str(charts_path / "damage")
                )
                all_chart_files.extend(damage_charts)
            
            # 生成轨迹分析图表
            if 'post_damage' in extracted_data:
                trajectory_charts = self.chart_generator.generate_trajectory_charts(
                    extracted_data['post_damage'],
                    str(charts_path / "trajectory")
                )
                all_chart_files.extend(trajectory_charts)
            
            # 生成对比分析图表
            if 'comparison' in extracted_data:
                comparison_charts = self.chart_generator.generate_comparison_charts(
                    extracted_data['comparison'],
                    str(charts_path / "comparison")
                )
                all_chart_files.extend(comparison_charts)
            
            # 生成综合仪表板
            dashboard_file = self.chart_generator.create_comprehensive_dashboard(
                extracted_data,
                str(charts_path / "comprehensive_dashboard.png")
            )
            if dashboard_file:
                all_chart_files.append(dashboard_file)
            
            return all_chart_files
            
        except Exception as e:
            self.logger.error(f"图表生成失败: {e}")
            return []
    
    def _create_analysis_summary(self, extracted_data: Dict) -> Dict[str, Any]:
        """创建分析摘要"""
        try:
            summary = {
                'analysis_timestamp': np.datetime64('now').astype(str),
                'data_overview': {},
                'key_findings': {},
                'performance_metrics': {},
                'recommendations': []
            }
            
            # 数据概览
            summary['data_overview'] = {
                'total_data_categories': len(extracted_data),
                'available_analyses': list(extracted_data.keys())
            }
            
            # 关键发现
            key_findings = {}
            
            # 激光毁伤关键发现
            if 'laser_damage' in extracted_data:
                laser_data = extracted_data['laser_damage']
                
                if 'damage_metrics' in laser_data:
                    metrics = laser_data['damage_metrics']
                    key_findings['laser_damage'] = {
                        'max_temperature': metrics.get('max_temperature', 0),
                        'max_stress': metrics.get('max_stress', 0),
                        'damage_volume': metrics.get('damage_volume', 0)
                    }
                
                if 'damage_analysis' in laser_data:
                    damage_analysis = laser_data['damage_analysis']
                    key_findings['damage_extent'] = {
                        'damage_ratio': damage_analysis.get('damage_ratio', 0) * 100,
                        'affected_elements': damage_analysis.get('damaged_elements', 0)
                    }
            
            # 毁伤后效关键发现
            if 'post_damage' in extracted_data:
                post_data = extracted_data['post_damage']
                
                if 'flight_performance' in post_data:
                    performance = post_data['flight_performance']
                    key_findings['flight_impact'] = {
                        'average_speed': performance.get('average_speed', 0),
                        'max_speed': performance.get('max_speed', 0),
                        'flight_time': performance.get('flight_time', 0)
                    }
                
                if 'stability_metrics' in post_data:
                    stability = post_data['stability_metrics']
                    key_findings['stability_impact'] = {
                        'overall_stability': stability.get('overall_stability', 0),
                        'longitudinal_stability': stability.get('longitudinal_stability', 0)
                    }
            
            # 对比分析关键发现
            if 'comparison' in extracted_data:
                comparison = extracted_data['comparison']
                
                if 'performance_comparison' in comparison:
                    perf_comp = comparison['performance_comparison']
                    if 'change_percentages' in perf_comp:
                        changes = perf_comp['change_percentages']
                        key_findings['performance_changes'] = {
                            'speed_change': changes.get('average_speed', 0),
                            'efficiency_change': changes.get('energy_loss', 0)
                        }
            
            summary['key_findings'] = key_findings
            
            # 性能指标
            performance_metrics = self._calculate_performance_metrics(extracted_data)
            summary['performance_metrics'] = performance_metrics
            
            # 建议
            recommendations = self._generate_recommendations(extracted_data)
            summary['recommendations'] = recommendations
            
            return summary
            
        except Exception as e:
            self.logger.error(f"分析摘要创建失败: {e}")
            return {}
    
    def _calculate_performance_metrics(self, extracted_data: Dict) -> Dict[str, float]:
        """计算性能指标"""
        try:
            metrics = {
                'damage_effectiveness': 0.0,
                'flight_capability_retention': 0.0,
                'mission_success_probability': 0.0,
                'overall_impact_score': 0.0
            }
            
            # 毁伤效能评估
            if 'laser_damage' in extracted_data:
                laser_data = extracted_data['laser_damage']
                
                if 'damage_analysis' in laser_data:
                    damage_ratio = laser_data['damage_analysis'].get('damage_ratio', 0)
                    metrics['damage_effectiveness'] = min(100.0, damage_ratio * 100)
            
            # 飞行能力保持率
            if 'post_damage' in extracted_data:
                post_data = extracted_data['post_damage']
                
                if 'flight_performance' in post_data:
                    performance = post_data['flight_performance']
                    avg_speed = performance.get('average_speed', 0)
                    
                    # 假设原始速度为200 m/s
                    original_speed = 200.0
                    retention_rate = (avg_speed / original_speed) * 100 if original_speed > 0 else 0
                    metrics['flight_capability_retention'] = min(100.0, retention_rate)
            
            # 任务成功概率（基于稳定性和性能）
            if 'post_damage' in extracted_data:
                post_data = extracted_data['post_damage']
                
                stability_score = 0.0
                if 'stability_metrics' in post_data:
                    stability = post_data['stability_metrics']
                    stability_score = stability.get('overall_stability', 0)
                
                performance_score = metrics['flight_capability_retention']
                
                # 综合评估任务成功概率
                metrics['mission_success_probability'] = (stability_score + performance_score) / 2.0
            
            # 总体影响评分
            damage_impact = 100 - metrics['damage_effectiveness']  # 毁伤越大，影响越大
            capability_impact = 100 - metrics['flight_capability_retention']  # 能力损失越大，影响越大
            
            metrics['overall_impact_score'] = (damage_impact + capability_impact) / 2.0
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"性能指标计算失败: {e}")
            return {}
    
    def _generate_recommendations(self, extracted_data: Dict) -> List[str]:
        """生成建议"""
        try:
            recommendations = []
            
            # 基于毁伤程度的建议
            if 'laser_damage' in extracted_data:
                laser_data = extracted_data['laser_damage']
                
                if 'damage_analysis' in laser_data:
                    damage_ratio = laser_data['damage_analysis'].get('damage_ratio', 0)
                    
                    if damage_ratio > 0.5:
                        recommendations.append("毁伤程度严重，建议加强防护措施")
                    elif damage_ratio > 0.2:
                        recommendations.append("存在中等程度毁伤，建议优化材料选择")
                    else:
                        recommendations.append("毁伤程度较轻，当前防护措施有效")
            
            # 基于飞行性能的建议
            if 'post_damage' in extracted_data:
                post_data = extracted_data['post_damage']
                
                if 'flight_performance' in post_data:
                    performance = post_data['flight_performance']
                    avg_speed = performance.get('average_speed', 0)
                    
                    if avg_speed < 100:
                        recommendations.append("飞行性能严重下降，建议重新评估飞行任务")
                    elif avg_speed < 150:
                        recommendations.append("飞行性能有所下降，建议调整飞行参数")
                
                if 'stability_metrics' in post_data:
                    stability = post_data['stability_metrics']
                    overall_stability = stability.get('overall_stability', 0)
                    
                    if overall_stability < 50:
                        recommendations.append("飞行稳定性不足，建议增强控制系统")
                    elif overall_stability < 80:
                        recommendations.append("稳定性有待改善，建议优化控制算法")
            
            # 基于对比分析的建议
            if 'comparison' in extracted_data:
                comparison = extracted_data['comparison']
                
                if 'performance_comparison' in comparison:
                    perf_comp = comparison['performance_comparison']
                    if 'change_percentages' in perf_comp:
                        changes = perf_comp['change_percentages']
                        
                        speed_change = changes.get('average_speed', 0)
                        if speed_change < -20:
                            recommendations.append("速度损失显著，建议评估推进系统影响")
            
            # 如果没有具体建议，添加通用建议
            if not recommendations:
                recommendations.extend([
                    "建议持续监控系统性能",
                    "定期进行毁伤效能评估",
                    "优化防护和恢复措施"
                ])
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"建议生成失败: {e}")
            return ["建议进行进一步分析"]
    
    def _generate_reports(self, extracted_data: Dict, chart_files: List[str], reports_dir: str) -> List[str]:
        """生成报告"""
        try:
            report_files = []
            
            # 创建报告目录
            reports_path = Path(reports_dir)
            reports_path.mkdir(parents=True, exist_ok=True)
            
            # 准备报告数据
            report_data = {
                **extracted_data,
                'summary': self.analysis_summary.get('key_findings', {}) if self.analysis_summary else {}
            }
            
            # 生成PDF报告
            pdf_file = str(reports_path / "laser_damage_analysis_report.pdf")
            if self.report_generator.generate_comprehensive_report(report_data, chart_files, pdf_file, 'pdf'):
                report_files.append(pdf_file)
            
            # 生成HTML报告
            html_file = str(reports_path / "laser_damage_analysis_report.html")
            if self.report_generator.generate_comprehensive_report(report_data, chart_files, html_file, 'html'):
                report_files.append(html_file)
            
            # 生成Word报告
            word_file = str(reports_path / "laser_damage_analysis_report.docx")
            if self.report_generator.generate_comprehensive_report(report_data, chart_files, word_file, 'docx'):
                report_files.append(word_file)
            
            return report_files
            
        except Exception as e:
            self.logger.error(f"报告生成失败: {e}")
            return []
    
    def export_analysis_data(self, output_file: str, format: str = 'json') -> bool:
        """导出分析数据"""
        try:
            if not self.extracted_data:
                self.logger.error("无可导出的分析数据")
                return False
            
            return self.data_extractor.export_data(self.extracted_data, output_file, format)
            
        except Exception as e:
            self.logger.error(f"数据导出失败: {e}")
            return False
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """获取分析摘要"""
        return self.analysis_summary or {}
    
    def get_generated_charts(self) -> List[str]:
        """获取生成的图表文件列表"""
        return self.generated_charts.copy()
    
    def get_extracted_data(self) -> Dict[str, Any]:
        """获取提取的数据"""
        return self.extracted_data or {}

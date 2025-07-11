"""
文件处理工具

提供文件读写、格式转换等功能。
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging


class FileUtils:
    """文件处理工具类"""
    
    @staticmethod
    def read_json(file_path: str) -> Optional[Dict[str, Any]]:
        """
        读取JSON文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            JSON数据字典，失败返回None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"读取JSON文件失败: {e}")
            return None
    
    @staticmethod
    def write_json(data: Dict[str, Any], file_path: str) -> bool:
        """
        写入JSON文件
        
        Args:
            data: 要写入的数据
            file_path: 文件路径
            
        Returns:
            是否成功
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logging.error(f"写入JSON文件失败: {e}")
            return False
    
    @staticmethod
    def get_supported_model_formats() -> List[str]:
        """
        获取支持的模型文件格式
        
        Returns:
            支持的文件格式列表
        """
        return ['.step', '.stp', '.iges', '.igs', '.sat', '.x_t', '.x_b']
    
    @staticmethod
    def validate_model_file(file_path: str) -> bool:
        """
        验证模型文件是否有效
        
        Args:
            file_path: 文件路径
            
        Returns:
            是否有效
        """
        if not os.path.exists(file_path):
            return False
        
        file_ext = Path(file_path).suffix.lower()
        return file_ext in FileUtils.get_supported_model_formats()

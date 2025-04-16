import os
from typing import List, Dict, Optional, Any
from app.core.config import get_settings
from app.services.file_manager import FileManager

class StreamService:
    def __init__(self):
        """初始化流媒体服务"""
        self.settings = get_settings()
        self.file_manager = FileManager()
    
    def generate_m3u8_playlist(self, project_id: str, request=None, format_type=None) -> str:
        """
        生成m3u8播放列表
        
        参数:
            project_id: 项目ID
            request: HTTP请求对象(可选)
            format_type: 音频格式类型(可选)
        
        返回:
            m3u8播放列表内容
        """
        files = self.file_manager.get_project_files(project_id)
        
        if not files:
            raise ValueError(f"No files found for project {project_id}")
        
        # 添加错误处理逻辑，避免"order"字段缺失导致的KeyError
        try:
            # 优先尝试按order排序
            sorted_files = sorted(files, key=lambda x: x.get("order", 0))
        except (KeyError, TypeError):
            # 如果获取order字段出错，则退回到按文件名排序
            sorted_files = sorted(files, key=lambda x: x.get("filename", ""))
        
        # 生成m3u8内容
        m3u8_content = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:30\n#EXT-X-MEDIA-SEQUENCE:0\n"
        
        # 获取项目目录基础路径
        base_dir = self.file_manager.get_base_dir()
        
        for file_info in sorted_files:
            # 安全地获取文件路径，使用file_manager来处理路径
            file_path = file_info.get("path", "")
            
            # 创建相对路径：从项目基础目录开始的路径
            if base_dir and file_path.startswith(base_dir):
                relative_path = file_path[len(base_dir):].lstrip(os.sep)
            else:
                # 如果无法确定相对路径，直接使用文件名
                relative_path = os.path.basename(file_path)
            
            # 添加音频持续时间信息
            duration = file_info.get("duration", 10)  # 默认10秒
            
            # 构建完整的流URL
            stream_url = f"{self.settings.STREAM_BASE_URL or ''}/{relative_path}"
            
            m3u8_content += f"#EXTINF:{duration},\n{stream_url}\n"
        
        m3u8_content += "#EXT-X-ENDLIST"
        return m3u8_content
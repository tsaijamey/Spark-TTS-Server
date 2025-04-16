import os
import urllib.parse
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
        
        # 打印找到的文件，帮助调试
        print(f"Found {len(files)} files for project {project_id}")
        
        # 添加错误处理逻辑，避免"order"字段缺失导致的KeyError
        try:
            # 优先尝试按order排序
            sorted_files = sorted(files, key=lambda x: x.get("order", 0))
        except (KeyError, TypeError):
            # 如果获取order字段出错，则退回到按文件名排序
            sorted_files = sorted(files, key=lambda x: x.get("filename", ""))
        
        # 生成m3u8内容
        m3u8_content = "#EXTM3U\n"
        m3u8_content += "#EXT-X-VERSION:3\n"
        m3u8_content += "#EXT-X-TARGETDURATION:60\n"
        m3u8_content += "#EXT-X-MEDIA-SEQUENCE:0\n"
        
        for file_info in sorted_files:
            filename = file_info.get("filename", "")
            
            # 计算一个预估的音频时长（秒）
            duration = file_info.get("duration", 30)
            
            # 构建正确的音频URL路径，使用相对于应用根目录的路径
            # 使用 /spark/audio/{project_id}/{filename} 格式
            audio_url = f"/spark/audio/{project_id}/{urllib.parse.quote(filename)}"
            
            m3u8_content += f"#EXTINF:{duration},\n"
            m3u8_content += f"{audio_url}\n"
        
        m3u8_content += "#EXT-X-ENDLIST"
        return m3u8_content
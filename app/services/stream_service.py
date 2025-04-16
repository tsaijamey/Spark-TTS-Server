from typing import List, Dict, Optional, Any
from app.core.config import get_settings

class StreamService:
    def __init__(self):
        self.settings = get_settings()
    
    def generate_m3u8_playlist(self, project_id: str, files: List[Dict[str, Any]], base_url: Optional[str] = None) -> str:
        """
        生成 M3U8 播放列表内容
        
        参数:
            project_id: 项目ID
            files: 文件信息列表，每个文件包含 order 和 filename
            base_url: 可选的基URL，用于构建绝对路径
            
        返回:
            M3U8 播放列表内容字符串
        """
        # 构建播放列表头部
        m3u8_content = "#EXTM3U\n"
        m3u8_content += "#EXT-X-VERSION:3\n"
        m3u8_content += "#EXT-X-MEDIA-SEQUENCE:0\n"
        m3u8_content += "#EXT-X-ALLOW-CACHE:YES\n"
        m3u8_content += "#EXT-X-TARGETDURATION:10\n"
        m3u8_content += "#EXT-X-PLAYLIST-TYPE:VOD\n\n"
        
        # 添加每个音频文件
        for file_info in sorted(files, key=lambda x: x["order"]):
            if base_url:
                file_url = f"{base_url}/audio/{project_id}/{file_info['filename']}"
            else:
                file_url = f"/audio/{project_id}/{file_info['filename']}"
            
            # 假设每个音频片段时长为10秒（实际应该从文件获取）
            m3u8_content += f"#EXTINF:10.0,\n"
            m3u8_content += f"{file_url}\n"
        
        # 添加播放列表结束标记
        m3u8_content += "#EXT-X-ENDLIST\n"
        
        return m3u8_content
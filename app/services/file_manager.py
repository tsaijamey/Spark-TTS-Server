import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.core.config import get_settings

class FileManager:
    def __init__(self):
        self.settings = get_settings()
    
    def get_base_dir(self) -> str:
        """获取文件存储的基础目录"""
        return self.settings.PROJECT_FILES_DIR
    
    def get_project_path(self, project_id: str) -> str:
        """获取项目目录路径"""
        project_path = os.path.join(self.get_base_dir(), project_id)
        os.makedirs(project_path, exist_ok=True)
        return project_path
        
    def get_next_order_index(self, project_id: str) -> int:
        """获取下一个序号"""
        project_path = Path(self.get_project_path(project_id))
        max_order = 0
        for file in project_path.glob("*.wav"):
            try:
                order = int(file.stem.split("_")[0])
                max_order = max(max_order, order)
            except (ValueError, IndexError):
                continue
        return max_order + 1
        
    def save_audio(self, audio_data: bytes, project_id: str, order: int, format: str = "wav") -> str:
        """保存音频文件"""
        project_path = Path(self.get_project_path(project_id))
        filename = f"{order:03d}_{project_id}.{format}"
        filepath = project_path / filename
        with open(filepath, "wb") as f:
            f.write(audio_data)
        return str(filepath)
        
    def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的所有文件信息"""
        project_path = self.get_project_path(project_id)
        if not os.path.exists(project_path):
            return []
        
        files = []
        print(f"Scanning directory: {project_path}")
        for filename in os.listdir(project_path):
            file_path = os.path.join(project_path, filename)
            if os.path.isfile(file_path) and self._is_audio_file(filename):
                # 调试信息
                print(f"Found audio file: {filename}")
                
                # 从文件名中提取顺序信息
                order = 0
                try:
                    # 尝试从文件名中提取顺序号
                    if "_" in filename:
                        order_str = filename.split("_")[0]
                        if order_str.isdigit():
                            order = int(order_str)
                except:
                    pass
                    
                # 获取文件持续时间，如果可能
                duration = self._get_audio_duration(file_path)
                
                files.append({
                    "filename": filename,
                    "path": file_path,
                    "order": order,
                    "duration": duration
                })
        
        print(f"Total files found: {len(files)}")
        return files

    def _get_audio_duration(self, file_path: str) -> float:
        """获取音频文件的持续时间（秒）"""
        try:
            # 如果有ffprobe或其他音频处理库可用，可以获取精确时长
            # 这里提供一个简单的预估值
            file_size = os.path.getsize(file_path)
            # 粗略估计：假设WAV格式，16位采样，单声道，44.1kHz
            # 每秒约88.2KB
            return file_size / (88200) 
        except:
            return 10  # 默认10秒
            
    def _is_audio_file(self, filename: str) -> bool:
        """检查文件是否为支持的音频格式"""
        extensions = ('.wav', '.mp3', '.ogg', '.aac', '.m4a')
        return any(filename.lower().endswith(ext) for ext in extensions)
        
    def get_audio_path(self, project_id: str, filename: str) -> str:
        """获取音频文件完整路径"""
        project_path = Path(self.get_project_path(project_id))
        filepath = project_path / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Audio file not found: {filename}")
        return str(filepath)
        
    def validate_prompt_size(self, file_size: int, max_size_mb: float = 1.0) -> bool:
        """验证提示文件大小"""
        max_size_bytes = max_size_mb * 1024 * 1024
        return file_size <= max_size_bytes
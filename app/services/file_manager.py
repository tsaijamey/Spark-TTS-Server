import os
from pathlib import Path
from typing import Dict, Any, List
from app.core.config import get_settings

class FileManager:
    def __init__(self):
        self.settings = get_settings()
        self.audio_dir = Path(self.settings.GENERATED_AUDIO_DIR)
        
    def get_project_path(self, project_id: str) -> str:
        """获取项目目录路径"""
        project_path = self.audio_dir / project_id
        project_path.mkdir(parents=True, exist_ok=True)
        return str(project_path)
        
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
        """获取项目文件列表"""
        project_path = Path(self.get_project_path(project_id))
        files = []
        for file in project_path.glob("*.*"):
            files.append({
                "filename": file.name,
                "download_url": f"/audio/{project_id}/{file.name}"
            })
        return sorted(files, key=lambda x: x["filename"])
        
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
from pydub import AudioSegment
from app.core.config import get_settings
import os

class AudioProcessor:
    def __init__(self):
        self.settings = get_settings()
        
    def convert_format(self, input_path: str, output_format: str) -> str:
        """
        转换音频文件格式
        
        参数:
            input_path: 输入文件路径
            output_format: 目标格式 (mp3, wav, ogg等)
            
        返回:
            转换后的文件路径
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        output_path = os.path.splitext(input_path)[0] + f".{output_format}"
        
        try:
            audio = AudioSegment.from_file(input_path)
            audio.export(output_path, format=output_format)
            return output_path
        except Exception as e:
            raise RuntimeError(f"Audio conversion failed: {str(e)}")
            
    def get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频时长(秒)
        
        参数:
            audio_path: 音频文件路径
            
        返回:
            音频时长(秒)
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
        try:
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0  # 毫秒转秒
        except Exception as e:
            raise RuntimeError(f"Failed to get audio duration: {str(e)}")
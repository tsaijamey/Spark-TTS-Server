import re
from typing import List

def split_text_into_sentences(text: str) -> List[str]:
    """
    将文本分割成句子列表，支持中英文混合文本
    
    参数:
        text: 要分割的文本
        
    返回:
        分割后的句子列表
    """
    # 匹配中英文句号、问号、感叹号作为句子分隔符
    pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\。|\？|\！)\s'
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]
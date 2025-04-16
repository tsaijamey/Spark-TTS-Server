from pydantic import BaseModel
from fastapi import UploadFile
from typing import Optional

class SynthesizeRequest(BaseModel):
    text: str
    project_id: Optional[str] = None
    prompt_text: Optional[str] = None
    output_format: str = "wav"
    split_sentences: bool = False

class PromptSpeechFile(BaseModel):
    prompt_speech: UploadFile
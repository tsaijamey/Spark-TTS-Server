from pydantic import BaseModel
from typing import List

class SynthesizeResponse(BaseModel):
    status: str
    project_id: str
    stream_url: str

class AudioFileInfo(BaseModel):
    order: int
    filename: str
    download_url: str

class ProjectFilesResponse(BaseModel):
    project_id: str
    files: List[AudioFileInfo]

class ErrorResponse(BaseModel):
    status: str = "error"
    message: str
from fastapi import FastAPI, UploadFile, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import uuid
import os
from pathlib import Path

# Import core modules
from app.core.config import get_settings
from app.core.security import get_api_key
from app.core.exceptions import (
    TTSError,
    FileProcessingError,
    ValidationError,
    ProjectNotFoundError,
    tts_exception_handler,
    file_processing_handler,
    validation_handler,
    project_not_found_handler
)

# Import models
from app.models.request import SynthesizeRequest, PromptSpeechFile
from app.models.response import (
    SynthesizeResponse,
    ProjectFilesResponse,
    ErrorResponse
)

# Import services
from app.services.tts_service import TTSService
from app.services.audio_processor import AudioProcessor
from app.services.file_manager import FileManager
from app.services.stream_service import StreamService

# Initialize FastAPI app with metadata
app = FastAPI(
    title="Spark-TTS API Server",
    description="API server for Spark-TTS text-to-speech synthesis with project management",
    version="0.1.0",
    contact={
        "name": "Spark-TTS Team",
        "email": "support@spark-tts.example.com"
    },
    license_info={
        "name": "MIT",
    }
)

# Register exception handlers
app.add_exception_handler(TTSError, tts_exception_handler)
app.add_exception_handler(FileProcessingError, file_processing_handler)
app.add_exception_handler(ValidationError, validation_handler)
app.add_exception_handler(ProjectNotFoundError, project_not_found_handler)

# Initialize services
settings = get_settings()
tts_service = TTSService()
audio_processor = AudioProcessor()
file_manager = FileManager()
stream_service = StreamService()

@app.get("/")
async def root():
    return {"message": "Spark-TTS Server is running"}

@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(
    request: SynthesizeRequest = None,
    prompt_speech: UploadFile = None,
    api_key: str = Depends(get_api_key)
):
    """
    接收文本和可选参数，生成语音文件并将其关联到指定或新生成的 project_id
    
    - **text**: 要合成的文本
    - **project_id**: (可选) 项目ID，如果为空则生成新的
    - **prompt_speech**: (可选) 提示语音文件，用于声音克隆
    - **prompt_text**: (可选) 提示文本，与提示语音配合使用
    - **output_format**: (可选) 输出格式，默认为 wav
    - **split_sentences**: (可选) 是否按句分割，默认为 false
    """
    # 验证请求参数
    if not request or not request.text:
        print("Request is :", request)
        print("Request text is :", request.text)
        raise ValidationError("Text is required")
    
    # 处理提示语音文件
    prompt_speech_path = None
    if prompt_speech:
        # 验证提示语音文件大小
        if not file_manager.validate_prompt_size(
            prompt_speech.size,
            settings.MAX_PROMPT_SIZE_MB
        ):
            raise ValidationError(
                f"Prompt speech file too large, max size: {settings.MAX_PROMPT_SIZE_MB}MB"
            )
        
        # 验证提示文本
        if not request.prompt_text:
            raise ValidationError("Prompt text is required when prompt speech is provided")
        
        # 保存提示语音文件到临时位置
        temp_dir = Path(settings.GENERATED_AUDIO_DIR) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        prompt_speech_path = str(temp_dir / f"prompt_{uuid.uuid4()}.wav")
        
        with open(prompt_speech_path, "wb") as f:
            f.write(await prompt_speech.read())
    
    try:
        # 处理文本分割
        if request.split_sentences:
            from app.utils.text_splitter import split_text_into_sentences
            sentences = split_text_into_sentences(request.text)
            
            # 合成多个句子
            project_id, output_files = await tts_service.synthesize_multiple(
                sentences,
                request.project_id,
                prompt_speech_path,
                request.prompt_text,
                request.output_format
            )
        else:
            # 合成单个文本
            project_id, _ = await tts_service.synthesize(
                request.text,
                request.project_id,
                prompt_speech_path,
                request.prompt_text,
                request.output_format,
                request.split_sentences
            )
        
        # 构建响应
        return SynthesizeResponse(
            status="success",
            project_id=project_id,
            stream_url=f"/stream/{project_id}"
        )
    
    finally:
        # 清理临时文件
        if prompt_speech_path and os.path.exists(prompt_speech_path):
            os.remove(prompt_speech_path)

@app.get("/stream/{project_id}")
async def stream_project(project_id: str):
    """
    获取指定项目的 M3U8 播放列表，用于按顺序流式播放该项目下的所有音频
    
    - **project_id**: 项目ID
    """
    try:
        # 获取项目文件列表
        files = file_manager.get_project_files(project_id)
        if not files:
            raise ProjectNotFoundError(project_id)
        
        # 生成 M3U8 播放列表
        m3u8_content = stream_service.generate_m3u8_playlist(
            project_id,
            files,
            settings.AUDIO_BASE_URL
        )
        
        # 返回 M3U8 播放列表
        return StreamingResponse(
            content=iter([m3u8_content.encode()]),
            media_type="application/vnd.apple.mpegurl"
        )
    except FileNotFoundError:
        raise ProjectNotFoundError(project_id)

@app.get("/projects/{project_id}/files", response_model=ProjectFilesResponse)
async def get_project_files(project_id: str):
    """
    获取指定项目下的所有音频文件列表信息
    
    - **project_id**: 项目ID
    """
    try:
        # 获取项目文件列表
        files = file_manager.get_project_files(project_id)
        if not files:
            raise ProjectNotFoundError(project_id)
        
        # 构建响应
        return ProjectFilesResponse(
            project_id=project_id,
            files=files
        )
    except FileNotFoundError:
        raise ProjectNotFoundError(project_id)

@app.get("/audio/{project_id}/{filename}")
async def get_audio_file(project_id: str, filename: str):
    """
    下载指定项目下的特定音频文件
    
    - **project_id**: 项目ID
    - **filename**: 文件名
    """
    try:
        # 获取音频文件路径
        file_path = file_manager.get_audio_path(project_id, filename)
        
        # 确定文件类型
        content_type = "audio/wav"
        if filename.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif filename.endswith(".ogg"):
            content_type = "audio/ogg"
        
        # 返回音频文件
        return StreamingResponse(
            content=open(file_path, "rb"),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audio file not found: {filename}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
from fastapi import FastAPI, UploadFile, HTTPException, status, Depends, Form, File, Request
from fastapi.responses import StreamingResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional
import uuid
import os
from pathlib import Path
import logging

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

# Import routers
from app.routers import audio

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

# 添加logger定义
logger = logging.getLogger(__name__)

# 确保将静态文件挂载在正确的路径
# 应该添加在所有路由定义前
static_files_dir = os.path.join(os.getcwd(), "static")
os.makedirs(static_files_dir, exist_ok=True)

# 直接挂载到根路径/spark, 与应用前缀一致
app.mount("/static", StaticFiles(directory=static_files_dir), name="static")

# 添加根路径重定向到播放器页面
@app.get("/")
async def root():
    """将根路径重定向到播放器页面"""
    return RedirectResponse(url="static/player.html")

@app.post("/synthesize", response_model=SynthesizeResponse)
async def synthesize(
    # Parameters are now expected as Form fields
    text: str = Form(...),
    project_id: Optional[str] = Form(None),
    output_format: str = Form("wav"),
    prompt_text: Optional[str] = Form(None),
    split_sentences: bool = Form(False),
    prompt_speech: Optional[UploadFile] = File(None), # Explicitly use File for clarity
    api_key: str = Depends(get_api_key)
):
    """
    接收文本和可选参数（通过 multipart/form-data），生成语音文件并将其关联到指定或新生成的 project_id

    - **text**: 要合成的文本 (Form field)
    - **project_id**: (可选) 项目ID (Form field)
    - **prompt_speech**: (可选) 提示语音文件 (File upload)
    - **prompt_text**: (可选) 提示文本 (Form field)
    - **output_format**: (可选) 输出格式，默认为 wav (Form field)
    - **split_sentences**: (可选) 是否按句分割，默认为 false (Form field)
    """
    # 验证请求参数 (using the 'text' variable directly)
    if not text:
        # The previous print statements for 'request' are no longer valid
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

        # 验证提示文本 (using the 'prompt_text' variable)
        if not prompt_text:
            raise ValidationError("Prompt text is required when prompt speech is provided")

        # 保存提示语音文件到临时位置
        temp_dir = Path(settings.GENERATED_AUDIO_DIR) / "temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        # Ensure filename is unique and has a standard extension (e.g., .wav)
        # Use prompt_speech.filename if available and sanitize, otherwise generate UUID
        original_filename = prompt_speech.filename if prompt_speech.filename else f"prompt_{uuid.uuid4()}"
        # Basic sanitization (replace spaces, limit length, etc.) - adjust as needed
        safe_filename = "".join(c if c.isalnum() or c in ('-', '_', '.') else '_' for c in original_filename)[:100]
        # Ensure a reasonable extension, default to .wav if unknown
        _, ext = os.path.splitext(safe_filename)
        if not ext:
            safe_filename += ".wav" # Assuming wav is the target format after potential conversion
        prompt_speech_path = str(temp_dir / safe_filename)


        with open(prompt_speech_path, "wb") as f:
            f.write(await prompt_speech.read())

    try:
        # 处理文本分割 (using direct variables)
        if split_sentences:
            from app.utils.text_splitter import split_text_into_sentences
            sentences = split_text_into_sentences(text)

            # 合成多个句子 (using direct variables)
            project_id_res, output_files = await tts_service.synthesize_multiple(
                sentences,
                project_id, # Use project_id variable
                prompt_speech_path,
                prompt_text, # Use prompt_text variable
                output_format # Use output_format variable
            )
            # Ensure project_id is updated if a new one was generated
            if project_id_res:
                 project_id = project_id_res
        else:
            # 合成单个文本 (using direct variables)
            project_id_res, _ = await tts_service.synthesize(
                text, # Use text variable
                project_id, # Use project_id variable
                prompt_speech_path,
                prompt_text, # Use prompt_text variable
                output_format, # Use output_format variable
                split_sentences # Use split_sentences variable
            )
            # Ensure project_id is updated if a new one was generated
            if project_id_res:
                 project_id = project_id_res

        # 构建响应
        return SynthesizeResponse(
            status="success",
            project_id=project_id, # Use the potentially updated project_id
            stream_url=f"/stream/{project_id}"
        )

    finally:
        # 清理临时文件
        if prompt_speech_path and os.path.exists(prompt_speech_path):
            os.remove(prompt_speech_path)

@app.get("/stream/{project_id}")
async def stream_project(
    project_id: str,
    request: Request
):
    """流式获取指定项目的音频"""
    try:
        m3u8_content = stream_service.generate_m3u8_playlist(
            project_id=project_id,
            request=request
        )
        
        return Response(
            content=m3u8_content,
            media_type="application/vnd.apple.mpegurl"
        )
    except Exception as e:
        # 现在logger已定义，可以正常使用
        logger.error(f"Error streaming project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error streaming project: {str(e)}")

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
    """直接获取项目中的音频文件"""
    try:
        # 获取项目路径
        project_path = file_manager.get_project_path(project_id)
        file_path = os.path.join(project_path, filename)
        
        if not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            raise HTTPException(status_code=404, detail=f"Audio file not found: {filename}")
        
        # 确定音频类型
        content_type = "audio/wav"  # 默认为WAV
        if filename.endswith(".mp3"):
            content_type = "audio/mpeg"
        elif filename.endswith(".ogg"):
            content_type = "audio/ogg"
        elif filename.endswith(".m4a"):
            content_type = "audio/mp4"
        
        # 返回音频文件
        return FileResponse(
            path=file_path,
            media_type=content_type,
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error getting audio file {filename} for project {project_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting audio file: {str(e)}")

# Include audio router
app.include_router(audio.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
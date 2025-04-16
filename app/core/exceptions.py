from fastapi import Request, status
from fastapi.responses import JSONResponse

class TTSError(Exception):
    """TTS处理过程中出现的错误"""
    def __init__(self, message: str):
        self.message = message

class FileProcessingError(Exception):
    """文件处理过程中出现的错误"""
    def __init__(self, message: str):
        self.message = message

class ValidationError(Exception):
    """输入验证失败错误"""
    def __init__(self, message: str):
        self.message = message

class ProjectNotFoundError(Exception):
    """请求的项目不存在错误"""
    def __init__(self, project_id: str):
        self.message = f"Project {project_id} not found"

async def tts_exception_handler(request: Request, exc: TTSError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": f"TTS Error: {exc.message}"},
    )

async def file_processing_handler(request: Request, exc: FileProcessingError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": f"File Processing Error: {exc.message}"},
    )

async def validation_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"status": "error", "message": f"Validation Error: {exc.message}"},
    )

async def project_not_found_handler(request: Request, exc: ProjectNotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"status": "error", "message": exc.message},
    )
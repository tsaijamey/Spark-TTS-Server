from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
import logging

router = APIRouter()

# ...existing code...

@router.get("/spark/audio/{project}/{filename}")
async def get_spark_audio_file(project: str, filename: str):
    try:
        audio_path = os.path.join("generated_audio", project, filename)
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail=f"Audio file {filename} not found for project {project}")
        return FileResponse(audio_path)
    except Exception as e:
        logging.error(f"Error getting audio file {filename} for project {project}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving audio file: {str(e)}")

# ...existing code...
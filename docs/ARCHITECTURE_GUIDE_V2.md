# Spark-TTS FastAPI Server - 开发文档 (v2 - Incorporating Project ID)

本文档详细说明了 Spark-TTS FastAPI 服务器的架构设计和开发要点，已包含项目 ID 相关需求。

## 1. 项目目标

构建一个 FastAPI 服务，通过 API 接口接收文本和可选的语音样本，调用 Spark-TTS 命令行工具生成语音文件。支持按项目 (`project_id`) 管理多次请求生成的音频，提供格式转换、按句分割、**按项目流式播放**和**按项目文件列表/下载**的功能。

## 2. 项目结构 (带 Project ID 调整)

```
Spark-TTS-Server/
├── .env                  # 环境变量配置
├── .gitignore
├── LICENSE
├── README.md             # 项目说明 (需要更新)
├── Spark-TTS.md          # Spark-TTS 命令行说明
├── requirements.txt      # Python 依赖
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 应用入口, 定义 API 端点
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py         # 加载和管理配置
│   │   ├── security.py       # API Key 鉴权逻辑
│   │   └── exceptions.py     # 自定义异常处理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py        # API 请求体模型 (Pydantic) - **增加 project_id**
│   │   └── response.py       # API 响应体模型 (Pydantic) - **修改 /synthesize 响应, 增加 /files 响应**
│   ├── services/
│   │   ├── __init__.py
│   │   ├── tts_service.py    # 核心 TTS 逻辑 - **处理 project_id**
│   │   ├── audio_processor.py # 音频处理 (分割, 格式转换)
│   │   ├── file_manager.py   # 文件存储、检索 - **按 project_id 管理, 顺序命名**
│   │   └── stream_service.py # **新增: 处理流播放逻辑 (e.g., M3U8)**
│   └── utils/
│       ├── __init__.py
│       └── text_splitter.py  # 文本按句分割逻辑
└── generated_audio/        # (由 .env 配置) 存放生成的音频文件
    └── {project_id_1}/     # **按项目 ID 创建子目录**
        ├── 001_timestamp_uuid.wav
        ├── 002_timestamp_uuid.mp3
        └── ...
    └── {project_id_2}/
        └── 001_timestamp_uuid.wav
        └── ...
```

## 3. 文件/模块说明 (带 Project ID 调整)

*   **`app/main.py`**:
    *   **调整:** 修改 `/synthesize` 路由逻辑和响应。添加 `/stream/{project_id}` 和 `/projects/{project_id}/files` 路由。修改 `/audio/...` 路由为 `/audio/{project_id}/{filename}`。
*   **`app/core/config.py`**: 无需大改。
*   **`app/core/security.py`**: 无需大改。
*   **`app/core/exceptions.py`**: 无需大改。
*   **`app/models/request.py`**:
    *   **调整:** `/synthesize` 的请求模型增加 `project_id: Optional[str] = None` 字段。
*   **`app/models/response.py`**:
    *   **调整:**
        *   修改 `/synthesize` 的成功响应模型为 `{ status: str, project_id: str, stream_url: str }`。
        *   新增 `/projects/{project_id}/files` 的响应模型，包含 `project_id` 和 `files` 列表，每个文件包含 `order`, `filename`, `download_url`。
*   **`app/services/tts_service.py`**:
    *   **调整:**
        *   接收 `project_id`。如果为空，则生成一个新的 UUID 作为 `project_id`。
        *   调用 `file_manager` 获取项目路径和下一个文件的顺序编号。
        *   调用 `file_manager` 保存文件到项目目录下。
        *   返回 `project_id`。
*   **`app/services/audio_processor.py`**: 无需大改，处理单个文件。
*   **`app/services/file_manager.py`**:
    *   **调整:**
        *   `save_audio`: 需要接收 `project_id` 和 `order`，保存到 `GENERATED_AUDIO_DIR/{project_id}/{order}_{uuid}.{format}`。确保项目目录存在。
        *   `get_project_path`: 根据 `project_id` 返回项目目录路径。
        *   `get_next_order_index`: 根据 `project_id` 查找目录下文件的最大序号，返回下一个序号。
        *   `get_project_files`: 根据 `project_id` 列出目录下所有音频文件，按序号排序。
        *   `get_audio_path`: 根据 `project_id` 和 `filename` 返回完整文件路径。
        *   `validate_prompt_size`: 保持不变。
*   **`app/services/stream_service.py` (新增)**:
    *   **用途:** 生成用于流式播放的内容，推荐 M3U8 格式。
    *   **主要组件:** Function `generate_m3u8_playlist`.
    *   **输入:** `project_id`, list of file paths/URLs within the project.
    *   **输出:** M3U8 播放列表内容的字符串。
*   **`app/utils/text_splitter.py`**: 无需大改。

## 4. API 端点 (带 Project ID 调整)

*   **`POST /synthesize`**
    *   **描述:** 接收文本和可选参数，生成语音文件并将其关联到指定或新生成的 `project_id`。
    *   **鉴权:** 需要 `X-API-Key`。
    *   **请求体:** `multipart/form-data` 包含 `text` (string, required), `project_id` (string, optional), `prompt_speech` (file, optional, <1MB), `prompt_text` (string, required if `prompt_speech` provided), `output_format` (string, optional, default 'wav'), `split_sentences` (boolean, optional, default false).
    *   **成功响应 (200 OK):**
        ```json
        {
          "status": "success",
          "project_id": "the_project_id_used_or_generated",
          "stream_url": "/stream/the_project_id_used_or_generated"
        }
        ```
    *   **失败响应:** 400, 401, 500 等。
*   **`GET /stream/{project_id}` (新增)**
    *   **描述:** 获取指定项目的 M3U8 播放列表，用于按顺序流式播放该项目下的所有音频。
    *   **鉴权:** 无 (或根据需求添加)。
    *   **路径参数:** `project_id` (string, required).
    *   **成功响应 (200 OK):** M3U8 播放列表内容 (`Content-Type: application/vnd.apple.mpegurl` 或 `audio/mpegurl`)。
    *   **失败响应:** 404 Not Found (if project_id doesn't exist or has no files).
*   **`GET /projects/{project_id}/files` (新增)**
    *   **描述:** 获取指定项目下的所有音频文件列表信息（顺序、文件名、下载链接）。
    *   **鉴权:** 无 (或根据需求添加)。
    *   **路径参数:** `project_id` (string, required).
    *   **成功响应 (200 OK):**
        ```json
        {
          "project_id": "the_project_id",
          "files": [
            { "order": 1, "filename": "001_some_id.mp3", "download_url": "/audio/the_project_id/001_some_id.mp3" },
            { "order": 2, "filename": "002_some_id.mp3", "download_url": "/audio/the_project_id/002_some_id.mp3" }
            // ...
          ]
        }
        ```
    *   **失败响应:** 404 Not Found.
*   **`GET /audio/{project_id}/{filename}` (调整)**
    *   **描述:** 下载指定项目下的特定音频文件。
    *   **鉴权:** 无 (或根据需求添加)。
    *   **路径参数:** `project_id` (string, required), `filename` (string, required).
    *   **成功响应 (200 OK):** 音频文件流 (`StreamingResponse`)，带有正确的 `Content-Type`。
    *   **失败响应:** 404 Not Found.

## 5. 核心逻辑流程图 (Mermaid - 简化 Synthesize 流程)

```mermaid
graph TD
    subgraph Synthesize Flow
        A[Client Request: POST /synthesize] --> B{Validate API Key};
        B -- Valid --> C{Parse Request Body (incl. project_id?)};
        B -- Invalid --> Z1[401 Unauthorized];
        C --> C1{Has project_id?};
        C1 -- Yes --> C2[Use provided project_id];
        C1 -- No --> C3[Generate new project_id];
        C2 & C3 --> D{Validate Input (Text, File Size)};
        D -- Invalid --> Z2[400 Bad Request];
        D -- Valid --> D1[Get Project Path & Next Order Index (file_manager)];
        D1 --> E{Check 'split_sentences'};
        E -- True --> F[Split Text into Sentences (text_splitter)];
        E -- False --> G[Process Full Text];
        F --> H[Loop through Sentences];
        H --> I[Call Spark-TTS CLI (tts_service)];
        G --> I[Call Spark-TTS CLI (tts_service)];
        I --> J{Check CLI Execution Status};
        J -- Error --> Z3[500 Internal Server Error];
        J -- Success --> K[Generated WAV file(s)];
        K --> L{Check 'output_format'};
        L -- Needs Conversion --> M[Convert WAV to Target Format (audio_processor)];
        L -- WAV --> N[Store WAV File(s) with Order (file_manager)];
        M --> N[Store Converted File(s) with Order (file_manager)];
        N --> P[Construct Response JSON: {status, project_id, stream_url}];
        P --> Q[Return Simplified Response];
    end

    subgraph Stream Flow
        S[Client Request: GET /stream/{project_id}] --> T{Get Project Files (file_manager)};
        T -- Found --> U[Generate M3U8 Playlist (stream_service)];
        U --> V[Return M3U8 Response];
        T -- Not Found/Empty --> Z4[404 Not Found];
    end

    subgraph List Files Flow
        W[Client Request: GET /projects/{project_id}/files] --> X{Get Project Files (file_manager)};
        X -- Found --> Y[Format File List JSON];
        Y --> Z[Return File List Response];
        X -- Not Found/Empty --> Z4[404 Not Found];
    end

    subgraph Download Flow
        AA[Client Request: GET /audio/{project_id}/{filename}] --> BB{Get Audio File Path (file_manager)};
        BB -- Found --> CC[Return StreamingResponse];
        BB -- Not Found --> Z4[404 Not Found];
    end

    style Z1 fill:#f9f,stroke:#333,stroke-width:2px
    style Z2 fill:#f9f,stroke:#333,stroke-width:2px
    style Z3 fill:#f9f,stroke:#333,stroke-width:2px
    style Z4 fill:#f9f,stroke:#333,stroke-width:2px
```

## 6. 环境变量 (`.env` 模板)

(与之前版本基本相同，`GENERATED_AUDIO_DIR` 现在是项目目录的父目录)

```dotenv
# .env.example - Copy this to .env and fill in your values

# FastAPI/Uvicorn Server Settings
HOST=0.0.0.0
PORT=8000
RELOAD=true # Set to false in production

# Security - Generate a strong secret key
API_KEY=YOUR_STRONG_SECRET_API_KEY_HERE

# Spark-TTS Configuration
SPARK_TTS_MODEL_DIR=./pretrained_models/Spark-TTS-0.5B
SPARK_TTS_DEVICE=0

# File Management
# Base directory to store generated audio projects
GENERATED_AUDIO_DIR=./generated_audio
MAX_PROMPT_SIZE_MB=1
# Base URL for constructing audio URLs (optional, if needed for M3U8 absolute URLs)
# AUDIO_BASE_URL=http://yourdomain.com
```

## 7. Python 依赖 (`requirements.txt`)

(与之前版本相同)

```
fastapi>=0.100.0
uvicorn[standard]>=0.20.0
pydantic>=2.0.0
python-dotenv>=1.0.0
pydub>=0.25.0
# Ensure ffmpeg/ffprobe are installed on the system for pydub
```

## 8. 其他必要信息 (Setup Notes)

(与之前版本相同，强调 `GENERATED_AUDIO_DIR` 下会创建项目子目录)

*   **外部依赖:** 需要 `ffmpeg`。
*   **模型文件:** 确保 `SPARK_TTS_MODEL_DIR` 正确。
*   **目录创建:** 应用需要确保 `GENERATED_AUDIO_DIR` 存在，并在首次向某个 `project_id` 添加文件时创建对应的子目录。
*   **权限:** 运行用户需要对 `GENERATED_AUDIO_DIR` 及其子目录有读写权限。
*   **M3U8:** `/stream/{project_id}` 返回的是 M3U8 播放列表，客户端需要支持 HLS (HTTP Live Streaming) 的播放器才能播放。
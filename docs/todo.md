# Spark-TTS FastAPI Server 实现计划

本文档详细列出了实现 Spark-TTS FastAPI Server 的具体步骤，按照 ARCHITECTURE_GUIDE_V2.md 中的规范进行细化。

## 1. 项目初始化

- [x] 创建项目基本目录结构
  ```bash
  mkdir -p app/core app/models app/services app/utils generated_audio
  touch app/__init__.py app/core/__init__.py app/models/__init__.py app/services/__init__.py app/utils/__init__.py
  ```
- [x] 创建 .env 文件
  ```bash
  cp .env.example .env  # 需要先创建 .env.example
  ```
- [x] 创建 requirements.txt 文件，添加依赖项
  ```
  fastapi>=0.100.0
  uvicorn[standard]>=0.20.0
  pydantic>=2.0.0
  python-dotenv>=1.0.0
  pydub>=0.25.0
  ```

## 2. 核心模块实现

### 2.1 配置模块 (app/core/config.py)

- [x] 实现 `Settings` 类，用于加载和管理配置
  - [x] 从 .env 文件加载环境变量
  - [x] 定义所有配置项（HOST, PORT, RELOAD, API_KEY, SPARK_TTS_MODEL_DIR, SPARK_TTS_DEVICE, GENERATED_AUDIO_DIR, MAX_PROMPT_SIZE_MB, AUDIO_BASE_URL）
  - [x] 实现 `get_settings()` 函数，返回单例 Settings 实例

### 2.2 安全模块 (app/core/security.py)

- [x] 实现 API Key 验证功能
  - [x] 创建 `APIKeyHeader` 类，用于从请求头中获取 API Key
  - [x] 实现 `get_api_key()` 依赖函数，验证 API Key 是否有效

### 2.3 异常处理模块 (app/core/exceptions.py)

- [x] 定义自定义异常类
  - [x] `TTSError`: TTS 处理相关错误
  - [x] `FileProcessingError`: 文件处理相关错误
  - [x] `ValidationError`: 输入验证相关错误
  - [x] `ProjectNotFoundError`: 项目不存在错误
- [x] 实现异常处理器
  - [x] 注册异常处理器到 FastAPI 应用

## 3. 模型模块实现

### 3.1 请求模型 (app/models/request.py)

- [x] 实现 `SynthesizeRequest` Pydantic 模型
  - [x] `text`: str (必填)
  - [x] `project_id`: Optional[str] = None
  - [x] `prompt_text`: Optional[str] = None
  - [x] `output_format`: str = "wav"
  - [x] `split_sentences`: bool = False
- [x] 实现 `PromptSpeechFile` Pydantic 模型 (用于文件上传)
  - [x] `prompt_speech`: UploadFile

### 3.2 响应模型 (app/models/response.py)

- [x] 实现 `SynthesizeResponse` Pydantic 模型
  - [x] `status`: str
  - [x] `project_id`: str
  - [x] `stream_url`: str
- [x] 实现 `AudioFileInfo` Pydantic 模型
  - [x] `order`: int
  - [x] `filename`: str
  - [x] `download_url`: str
- [x] 实现 `ProjectFilesResponse` Pydantic 模型
  - [x] `project_id`: str
  - [x] `files`: List[AudioFileInfo]
- [x] 实现 `ErrorResponse` Pydantic 模型
  - [x] `status`: str = "error"
  - [x] `message`: str

## 4. 工具模块实现

### 4.1 文本分割器 (app/utils/text_splitter.py)

- [x] 实现 `split_text_into_sentences()` 函数
  - [x] 参数: `text: str`
  - [x] 返回: `List[str]` (分割后的句子列表)
  - [x] 使用正则表达式或 NLP 库分割文本为句子
  - [x] 处理中英文混合文本的分割

## 5. 服务模块实现

### 5.1 TTS 服务 (app/services/tts_service.py)

- [x] 实现 `TTSService` 类
  - [x] `__init__()` 方法，初始化配置
  - [x] `synthesize()` 方法
    - [x] 参数: `text: str, project_id: Optional[str] = None, prompt_speech_path: Optional[str] = None, prompt_text: Optional[str] = None`
    - [x] 返回: `Tuple[str, str]` (project_id, 生成的音频文件路径)
    - [x] 如果 project_id 为空，生成新的 UUID 作为 project_id
    - [x] 调用 file_manager 获取项目路径和下一个文件的顺序编号
    - [x] 构建 Spark-TTS 命令行命令
    - [x] 执行命令行命令
    - [x] 处理命令执行结果
    - [x] 返回 project_id 和生成的音频文件路径
  - [x] `synthesize_multiple()` 方法
    - [x] 参数: `sentences: List[str], project_id: str, prompt_speech_path: Optional[str] = None, prompt_text: Optional[str] = None`
    - [x] 返回: `Tuple[str, List[str]]` (project_id, 生成的音频文件路径列表)
    - [x] 循环调用 `synthesize()` 方法处理每个句子
    - [x] 返回 project_id 和生成的音频文件路径列表

### 5.2 音频处理器 (app/services/audio_processor.py)

- [x] 实现 `AudioProcessor` 类
  - [x] `__init__()` 方法，初始化配置
  - [x] `convert_format()` 方法
    - [x] 参数: `input_path: str, output_format: str`
    - [x] 返回: `str` (转换后的音频文件路径)
    - [x] 使用 pydub 库转换音频格式
    - [x] 处理不同格式的转换逻辑
  - [x] `get_audio_duration()` 方法 (可选)
    - [x] 参数: `audio_path: str`
    - [x] 返回: `float` (音频时长，单位：秒)
    - [x] 使用 pydub 库获取音频时长

### 5.3 文件管理器 (app/services/file_manager.py)

- [x] 实现 `FileManager` 类
  - [x] `__init__()` 方法，初始化配置
  - [x] `get_project_path()` 方法
    - [x] 参数: `project_id: str`
    - [x] 返回: `str` (项目目录路径)
    - [x] 根据 project_id 构建项目目录路径
    - [x] 确保项目目录存在
  - [x] `get_next_order_index()` 方法
    - [x] 参数: `project_id: str`
    - [x] 返回: `int` (下一个序号)
    - [x] 查找项目目录下文件的最大序号
    - [x] 返回最大序号 + 1
  - [x] `save_audio()` 方法
    - [x] 参数: `audio_data: bytes, project_id: str, order: int, format: str = "wav"`
    - [x] 返回: `str` (保存的文件路径)
    - [x] 构建文件名: `{order:03d}_{timestamp}_{uuid}.{format}`
    - [x] 保存音频数据到文件
  - [x] `get_project_files()` 方法
    - [x] 参数: `project_id: str`
    - [x] 返回: `List[Dict[str, Any]]` (文件信息列表)
    - [x] 列出项目目录下所有音频文件
    - [x] 解析文件名，提取序号
    - [x] 按序号排序
    - [x] 构建文件信息字典列表
  - [x] `get_audio_path()` 方法
    - [x] 参数: `project_id: str, filename: str`
    - [x] 返回: `str` (完整文件路径)
    - [x] 验证文件是否存在
    - [x] 返回完整文件路径
  - [x] `validate_prompt_size()` 方法
    - [x] 参数: `file_size: int, max_size_mb: float = 1.0`
    - [x] 返回: `bool` (是否有效)
    - [x] 验证文件大小是否超过限制

### 5.4 流媒体服务 (app/services/stream_service.py)

- [x] 实现 `StreamService` 类
  - [x] `__init__()` 方法，初始化配置
  - [x] `generate_m3u8_playlist()` 方法
    - [x] 参数: `project_id: str, files: List[Dict[str, Any]], base_url: Optional[str] = None`
    - [x] 返回: `str` (M3U8 播放列表内容)
    - [x] 构建 M3U8 播放列表头部
    - [x] 循环添加每个音频文件的 URL
    - [x] 返回完整的 M3U8 播放列表内容

## 6. 主应用实现

### 6.1 主应用入口 (app/main.py)

- [x] 创建 FastAPI 应用实例
  - [x] 配置应用元数据（标题、描述、版本等）
  - [x] 注册异常处理器
- [x] 实现 API 端点
  - [x] `POST /synthesize` 端点
    - [x] 参数: 请求体 (SynthesizeRequest)，文件 (UploadFile)
    - [x] 返回: SynthesizeResponse
    - [x] 验证 API Key
    - [x] 处理请求参数
    - [x] 处理上传的提示音频文件（如果有）
    - [x] 根据 split_sentences 参数决定是否分割文本
    - [x] 调用 TTS 服务生成音频
    - [x] 根据 output_format 参数决定是否转换格式
    - [x] 构建响应
  - [x] `GET /stream/{project_id}` 端点
    - [x] 参数: project_id (路径参数)
    - [x] 返回: StreamingResponse (M3U8 播放列表)
    - [x] 获取项目文件列表
    - [x] 生成 M3U8 播放列表
    - [x] 返回 StreamingResponse，设置正确的 Content-Type
  - [x] `GET /projects/{project_id}/files` 端点
    - [x] 参数: project_id (路径参数)
    - [x] 返回: ProjectFilesResponse
    - [x] 获取项目文件列表
    - [x] 构建响应
  - [x] `GET /audio/{project_id}/{filename}` 端点
    - [x] 参数: project_id, filename (路径参数)
    - [x] 返回: StreamingResponse (音频文件)
    - [x] 获取音频文件路径
    - [x] 返回 StreamingResponse，设置正确的 Content-Type

## 7. 环境配置

### 7.1 .env.example 文件

- [ ] 创建 .env.example 文件，包含所有必要的环境变量
  ```dotenv
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

## 8. 测试计划

### 8.1 单元测试

- [ ] 测试 text_splitter.py
  - [ ] 测试中文分句
  - [ ] 测试英文分句
  - [ ] 测试中英文混合分句
- [ ] 测试 file_manager.py
  - [ ] 测试 get_project_path
  - [ ] 测试 get_next_order_index
  - [ ] 测试 save_audio
  - [ ] 测试 get_project_files
  - [ ] 测试 get_audio_path
  - [ ] 测试 validate_prompt_size
- [ ] 测试 audio_processor.py
  - [ ] 测试 convert_format
  - [ ] 测试 get_audio_duration
- [ ] 测试 stream_service.py
  - [ ] 测试 generate_m3u8_playlist

### 8.2 集成测试

- [ ] 测试 `/synthesize` 端点
  - [ ] 测试基本文本合成
  - [ ] 测试带 project_id 的文本合成
  - [ ] 测试带提示音频的文本合成
  - [ ] 测试分句合成
  - [ ] 测试格式转换
- [ ] 测试 `/stream/{project_id}` 端点
  - [ ] 测试有效 project_id
  - [ ] 测试无效 project_id
- [ ] 测试 `/projects/{project_id}/files` 端点
  - [ ] 测试有效 project_id
  - [ ] 测试无效 project_id
- [ ] 测试 `/audio/{project_id}/{filename}` 端点
  - [ ] 测试有效 project_id 和 filename
  - [ ] 测试无效 project_id 或 filename

## 9. 部署计划

- [ ] 准备生产环境配置
  - [ ] 设置 RELOAD=false
  - [ ] 生成强密码 API_KEY
  - [ ] 配置适当的 HOST 和 PORT
- [ ] 安装依赖
  ```bash
  pip install -r requirements.txt
  ```
- [ ] 安装 ffmpeg
  ```bash
  # Ubuntu/Debian
  apt-get install ffmpeg
  
  # CentOS/RHEL
  yum install ffmpeg
  
  # macOS
  brew install ffmpeg
  ```
- [ ] 启动服务
  ```bash
  uvicorn app.main:app --host $HOST --port $PORT
  ```

## 10. 文档计划

- [ ] 更新 README.md
  - [ ] 添加项目描述
  - [ ] 添加安装说明
  - [ ] 添加使用说明
  - [ ] 添加 API 文档链接
- [ ] 创建 API 文档
  - [ ] 使用 FastAPI 自动生成的 Swagger UI 文档
  - [ ] 添加每个端点的详细说明和示例
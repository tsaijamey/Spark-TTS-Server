# Spark-TTS FastAPI Server 设置指南

本文档详细说明了如何设置和运行 Spark-TTS FastAPI Server。

## 1. 环境设置

### 1.1 创建并激活虚拟环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# 在 Linux/macOS 上
source .venv/bin/activate
# 在 Windows 上
.venv\Scripts\activate
```

### 1.2 安装依赖

```bash
# 确保已激活虚拟环境
pip install -r requirements.txt
```

## 2. 配置

### 2.1 创建 .env 文件

从 .env.example 复制并修改 .env 文件：

```bash
cp .env.example .env
```

然后编辑 .env 文件，设置以下配置项：

- `API_KEY`: 设置一个强密码作为 API Key
- `SPARK_TTS_MODEL_DIR`: 设置 Spark-TTS 模型目录的路径
- `SPARK_TTS_DEVICE`: 设置使用的设备（0 表示第一个 GPU，-1 表示 CPU）
- `GENERATED_AUDIO_DIR`: 设置生成的音频文件存储目录

## 3. 运行服务器

```bash
# 确保已激活虚拟环境
uvicorn app.main:app --reload
```

## 4. 访问 API 文档

服务器启动后，可以通过以下 URL 访问 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 5. 依赖说明

- `fastapi`: Web 框架
- `uvicorn`: ASGI 服务器
- `pydantic`: 数据验证
- `pydantic-settings`: 配置管理
- `python-dotenv`: 环境变量管理
- `pydub`: 音频处理
- `python-multipart`: 处理表单数据（文件上传）

## 6. 外部依赖

- `ffmpeg`: 音频格式转换（需要系统安装）
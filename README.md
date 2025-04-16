# Spark-TTS FastAPI Server

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Spark-TTS FastAPI Server 是一个基于 FastAPI 构建的 RESTful API 服务，用于通过 HTTP 接口调用 Spark-TTS 文本转语音功能。支持按项目(`project_id`)管理多次请求生成的音频，提供格式转换、按句分割、流式播放和文件下载功能。

## ✨ 功能特性

- **文本转语音合成**：支持中英文文本转语音
- **项目化管理**：通过 `project_id` 管理多次请求生成的音频文件
- **多种输出格式**：支持 WAV、MP3、OGG 等音频格式
- **流式播放**：生成 M3U8 播放列表，支持流式播放
- **文件管理**：按项目获取文件列表和下载音频文件
- **提示语音支持**：可上传提示语音文件进行语音风格转换
- **按句分割**：支持将长文本按句子分割后分别合成

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境

复制 `.env.example` 为 `.env` 并修改配置：

```bash
cp .env.example .env
```

### 运行服务

```bash
uvicorn app.main:app --reload
```

访问 API 文档：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📦 安装指南

详细安装说明请参考 [SETUP.md](docs/SETUP.md)

## 🔧 使用说明

### 基本使用

```bash
curl -X POST "http://localhost:8000/synthesize" \
  -H "X-API-Key: your_api_key" \
  -F "text=你好，这是测试文本" \
  -F "project_id=test123" \
  -F "output_format=mp3"
```

### Python 客户端示例

```python
import requests

url = "http://localhost:8000/synthesize"
headers = {"X-API-Key": "your_api_key"}
files = {
    "text": (None, "你好，这是测试文本"),
    "project_id": (None, "test123"),
    "output_format": (None, "mp3")
}
response = requests.post(url, headers=headers, files=files)
print(response.json())
```

## 📚 API 文档

完整 API 文档请参考 [API_DOCS.md](docs/API_DOCS.md)

## 🏗️ 架构设计

项目采用模块化设计，主要模块包括：

- **核心模块**：配置、安全、异常处理
- **模型模块**：请求/响应数据结构
- **服务模块**：TTS 服务、音频处理、文件管理、流媒体服务
- **工具模块**：文本分割器

详细架构设计请参考 [ARCHITECTURE_GUIDE_V2.md](docs/ARCHITECTURE_GUIDE_V2.md)

## 🛠️ 开发指南

### 项目结构

```
Spark-TTS-Server/
├── app/                  # 应用代码
│   ├── core/             # 核心模块
│   ├── models/           # 数据模型
│   ├── services/         # 服务模块
│   └── utils/            # 工具模块
├── generated_audio/      # 生成的音频文件
└── docs/                 # 文档
```

### 开发流程

1. 创建并激活虚拟环境
2. 安装开发依赖
3. 实现功能模块
4. 编写单元测试
5. 提交 Pull Request

详细开发计划请参考 [todo.md](docs/todo.md)

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件

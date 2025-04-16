# Spark-TTS API 文档

## 1. 基础信息
- 基础URL: `http://yourdomain.com` (根据实际部署环境调整)
- 认证: 需要在请求头中添加 `X-API-Key`

## 2. API 端点

### 2.1 文本合成 - POST /synthesize

#### 功能描述
接收文本和可选参数，生成语音文件并将其关联到指定或新生成的 `project_id`

#### 请求头
```
X-API-Key: your_api_key
Content-Type: multipart/form-data
```

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| text | string | 是 | 要合成的文本内容 |
| project_id | string | 否 | 项目ID，如果为空则自动生成 |
| prompt_speech | file | 否 | 提示语音文件(小于1MB)，未提供时使用DEFAULT_PROMPT_SPEECH_PATH |
| prompt_text | string | 否 | 提示文本，未提供时使用DEFAULT_PROMPT_TEXT |
| output_format | string | 否 | 输出格式(wav/mp3/ogg)，默认wav |
| split_sentences | boolean | 否 | 是否按句分割，默认false |

#### 响应
成功响应 (200):
```json
{
  "status": "success",
  "project_id": "generated_or_provided_project_id",
  "stream_url": "/stream/generated_or_provided_project_id"
}
```

#### 示例代码
**curl:**
```bash
curl -X POST "http://localhost:8000/synthesize" \
  -H "X-API-Key: your_api_key" \
  -F "text=你好，这是测试文本" \
  -F "project_id=test123" \
  -F "output_format=mp3"
```

**Python:**
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

**Node.js:**
```javascript
const axios = require('axios');
const FormData = require('form-data');

const form = new FormData();
form.append('text', '你好，这是测试文本');
form.append('project_id', 'test123');
form.append('output_format', 'mp3');

axios.post('http://localhost:8000/synthesize', form, {
  headers: {
    'X-API-Key': 'your_api_key',
    ...form.getHeaders()
  }
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

### 2.2 获取流播放列表 - GET /stream/{project_id}

#### 功能描述
获取指定项目的M3U8播放列表，用于按顺序流式播放该项目下的所有音频

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

#### 响应
成功响应 (200): M3U8播放列表内容

#### 示例代码
**curl:**
```bash
curl "http://localhost:8000/stream/test123"
```

**Python:**
```python
import requests

url = "http://localhost:8000/stream/test123"
response = requests.get(url)
print(response.text)
```

### 2.3 获取项目文件列表 - GET /projects/{project_id}/files

#### 功能描述
获取指定项目下的所有音频文件列表信息

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |

#### 响应
成功响应 (200):
```json
{
  "project_id": "test123",
  "files": [
    {
      "order": 1,
      "filename": "001_test123.mp3",
      "download_url": "/audio/test123/001_test123.mp3"
    }
  ]
}
```

### 2.4 下载音频文件 - GET /audio/{project_id}/{filename}

#### 功能描述
下载指定项目下的特定音频文件

#### 请求参数
| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | string | 是 | 项目ID |
| filename | string | 是 | 文件名 |

#### 响应
成功响应 (200): 音频文件流

## 3. 错误代码
| 状态码 | 描述 |
|--------|------|
| 400 | 请求参数错误 |
| 401 | API Key无效 |
| 404 | 项目或文件不存在 |
| 500 | 服务器内部错误 |
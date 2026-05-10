# Chat2DB-AI 企业级多数据库智能问答系统

> 对标 zoer.ai Pro，基于 Chat2DB 架构扩展，支持 6 大数据库类型的智能问答平台。

## 核心能力

- **多数据库支持**：MySQL、Oracle、PostgreSQL、TiDB、OceanBase、公司自研数据库一键切换
- **智能问答**：自然语言提问，输出排查思路、性能技巧、参数推荐、分步方案、SQL语句、风险避坑
- **RAG动态知识库**：PDF/Word/TXT/Markdown 自动解析、向量化、动态更新
- **多Agent调度**：
  - 自研数据库 → Claude 深度推理 + 内部RAG + Skills
  - 通用数据库 → DeepSeek/豆包/文心/GPT 多模型路由，负载均衡 + 故障降级
- **完整Web端**：复刻 zoer.ai Pro 交互，支持搜索、上传、FAQ、历史对话、结构化答案、导出复制

---

## 项目结构

```
chat2db-ai/
├── chat2db-ai-backend/          # FastAPI 后端
│   ├── app/
│   │   ├── api/                 # RESTful API 接口
│   │   │   ├── chat.py          # 对话接口 (流式/非流式)
│   │   │   ├── upload.py        # 文档上传/批量上传/删除
│   │   │   ├── faq.py           # 高频问题/搜索
│   │   │   ├── database.py      # 数据库管理
│   │   │   └── health.py        # 健康检查/统计
│   │   ├── core/                # 核心基础设施
│   │   │   ├── logger.py        # 结构化日志 (structlog)
│   │   │   ├── exceptions.py    # 全局异常定义与处理
│   │   │   ├── response.py      # 统一返回格式
│   │   │   └── middleware.py    # 请求追踪/耗时统计
│   │   ├── mcp/                 # MCP 三层架构
│   │   │   ├── model.py         # 模型选择 + 上下文窗口管理
│   │   │   ├── context.py       # 上下文构建 (Skills+RAG+历史)
│   │   │   ├── prompt.py        # 意图识别 + Query增强 + 输出格式化
│   │   │   └── engine.py        # 统一调度引擎
│   │   ├── rag/                 # RAG 知识库
│   │   │   ├── embeddings.py    # Embedding模型封装
│   │   │   ├── document_parser.py # PDF/DOCX/TXT/MD解析
│   │   │   ├── chunker.py       # 文本分块
│   │   │   └── chroma_store.py  # Chroma向量库存储/检索
│   │   ├── agent/               # 多模型Agent路由
│   │   │   ├── base.py          # Agent基类
│   │   │   ├── deepseek.py      # DeepSeek Agent
│   │   │   ├── doubao.py        # 豆包 Agent
│   │   │   ├── wenxin.py        # 文心一言 Agent
│   │   │   ├── openai.py        # ChatGPT Agent
│   │   │   ├── claude.py        # Claude Agent (自研库专用)
│   │   │   └── router.py        # 路由中心 + 故障降级
│   │   ├── skills/              # Skills 技能库
│   │   │   ├── base.py          # 技能基类 + 注册中心
│   │   │   ├── registry.py      # 自动注册入口
│   │   │   └── databases/       # 各数据库技能实现
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic 数据模型
│   │   ├── config.py            # 统一配置管理 (.env + yaml)
│   │   └── main.py              # FastAPI 应用入口
│   ├── skills_data/             # 技能库结构化数据
│   │   ├── mysql/
│   │   ├── oracle/
│   │   ├── postgresql/
│   │   ├── tidb/
│   │   ├── oceanbase/
│   │   └── self_db/
│   ├── uploads/                 # 上传文件暂存
│   ├── chroma_db/               # Chroma 持久化数据
│   ├── logs/                    # 日志目录
│   ├── .env                     # 开发环境变量
│   ├── .env.production          # 生产环境变量
│   ├── config.yaml              # 开发配置
│   ├── config.production.yaml   # 生产配置
│   ├── requirements.txt         # Python 依赖
│   ├── start.py                 # Python启动脚本
│   ├── start.sh                 # Linux/macOS启动脚本
│   └── start.bat                # Windows启动脚本
│
├── chat2db-ai-frontend/         # Vue3 前端
│   ├── src/
│   │   ├── api/index.js         # 统一API封装 (含SSE流式)
│   │   ├── stores/chat.js       # Pinia 状态管理
│   │   ├── utils/format.js      # Markdown渲染/复制/文件大小
│   │   ├── components/
│   │   │   ├── DatabaseSelector.vue  # 数据库选择器
│   │   │   ├── ChatWindow.vue        # 聊天主窗口
│   │   │   ├── MessageBubble.vue     # 消息气泡 (结构化展示)
│   │   │   ├── UploadPanel.vue       # 知识库上传面板
│   │   │   ├── FAQPanel.vue          # FAQ搜索面板
│   │   │   └── HistorySidebar.vue    # 历史会话侧边栏
│   │   ├── views/Home.vue       # 主页面 (三栏布局)
│   │   ├── App.vue
│   │   └── main.js
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- (可选) CUDA 用于 GPU 加速 Embedding

### 1. 后端启动

```bash
cd chat2db-ai-backend

# Linux/macOS
chmod +x start.sh
./start.sh dev 0.0.0.0 8000

# Windows
start.bat dev 0.0.0.0 8000

# 或使用Python直接启动
python start.py --env dev --host 0.0.0.0 --port 8000
```

### 2. 前端启动

```bash
cd chat2db-ai-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端默认地址: http://localhost:5173  
后端默认地址: http://localhost:8000  
API文档: http://localhost:8000/docs

---

## 配置说明

### 环境变量 (.env)

| 变量 | 说明 | 示例 |
|------|------|------|
| `DOUBAO_API_KEY` | 豆包 API Key | `your-doubao-api-key` |
| `WENXIN_API_KEY` | 文心 API Key | `your-wenxin-key` |
| `WENXIN_SECRET_KEY` | 文心 Secret Key | `your-wenxin-secret` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | `your-deepseek-key` |
| `OPENAI_API_KEY` | OpenAI API Key | `your-openai-key` |
| `CLAUDE_API_KEY` | Claude API Key (自研库) | `your-claude-key` |
| `ROUTER_STRATEGY` | 路由策略 | `priority` / `round_robin` |
| `EMBEDDING_MODEL` | Embedding模型 | `sentence-transformers/all-MiniLM-L6-v2` |

### YAML 配置 (config.yaml)

- `databases`: 支持的数据库列表及元信息
- `rag`: 分块大小、Top-K、相似度阈值
- `agents`: 各模型超时、重试、优先级
- `mcp`: 上下文窗口长度、意图识别开关
- `skills`: 技能库目录、自动重载

---

## API 接口清单

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | 非流式对话 |
| POST | `/api/chat/stream` | SSE流式对话 |
| POST | `/api/upload` | 单文件上传解析 |
| POST | `/api/upload/batch` | 批量文件上传 |
| GET | `/api/upload/list` | 已入库文档列表 |
| DELETE | `/api/upload/{filename}` | 删除文档 |
| GET | `/api/faq/hot` | 高频问题 |
| GET | `/api/faq/search` | 搜索FAQ |
| GET | `/api/databases` | 数据库列表 |
| GET | `/api/databases/{db_type}/skills` | 技能分类 |
| GET | `/api/health` | 健康检查 |
| GET | `/api/health/stats` | 系统统计 |

---

## 使用指南

### 1. 日常问答

1. 在顶部选择目标数据库类型（MySQL/Oracle/自研数据库等）
2. 在输入框中自然语言提问，例如：
   - "MySQL 主从延迟怎么排查？"
   - "CPU 飙高如何定位具体SQL？"
   - "连接数满了有哪些应急处理方案？"
3. 支持流式输出（实时打字效果）和非流式输出（结构化答案）
4. 点击消息下方的「复制」或「导出」保存答案

### 2. 上传内部文档

1. 切换到右侧「知识库」面板
2. 拖拽或选择 PDF/Word/TXT/Markdown 文件
3. 选择文档归属的数据库类型（如 MySQL、自研数据库）
4. 点击「确认上传」，系统自动解析并向量化入库
5. 上传后提问将自动引用相关文档内容

### 3. FAQ 快速查询

1. 切换到右侧「FAQ」面板
2. 浏览热门问题列表，直接点击即可发送
3. 或使用搜索框检索 Skills 技能库中的内容

### 4. 自研数据库专用模式

选择「自研数据库」后：
- 自动路由至 Claude 进行深度推理
- 优先检索内部 RAG 文档和 Skills 技能库
- 若知识库未覆盖，明确提示联系 DBA 团队
- 所有回答严格基于内部知识，不调用外部通用模型

---

## 部署说明

### Docker 部署 (推荐生产环境)

```dockerfile
# Dockerfile (chat2db-ai-backend)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "start.py", "--env", "production"]
```

```bash
# 构建并运行
docker build -t chat2db-ai-backend .
docker run -d -p 8000:8000 --env-file .env.production -v /data/chroma_db:/app/chroma_db chat2db-ai-backend
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name chat2db.company.com;

    location / {
        proxy_pass http://localhost:5173;
    }

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| 配置管理 | python-dotenv + PyYAML + Pydantic Settings |
| RAG | ChromaDB + LangChain + Sentence-Transformers |
| 文档解析 | PyPDF + python-docx + unstructured |
| 模型调用 | DeepSeek / 豆包 / 文心一言 / GPT-4o / Claude |
| 日志 | structlog (JSON格式) |
| 前端 | Vue3 + Vite + Element Plus + Pinia |
| 流式通信 | SSE (Server-Sent Events) |

---

## 开发计划

- [x] 多数据库支持与切换
- [x] Skills 结构化技能库
- [x] MCP 三层架构 (Model-Context-Prompt)
- [x] RAG 文档上传/解析/向量化
- [x] 多模型Agent路由 + 故障降级
- [x] FastAPI 接口 + 统一返回格式
- [x] Vue3 前端 (三栏布局 + zoer.ai风格)
- [ ] 对话持久化 (SQLite / MySQL)
- [ ] SQL 语法校验与风险评估
- [ ] 用户认证与权限管理
- [ ] 对话反馈与知识库自动优化

---

## License

MIT License - 内部项目使用请遵守公司合规要求。

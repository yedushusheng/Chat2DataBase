# Chat2DB-AI 架构原理

> 本文档详细描述 Chat2DB-AI 的系统架构、核心数据流、模块职责与设计原理。

---

## 系统整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层 (Vue3)                         │
│  Home.vue ──► ChatWindow.vue / UploadPanel / FAQPanel       │
│       │              │                                       │
│       ▼              ▼                                       │
│  Pinia Store    api/index.js (Axios/Fetch)                  │
│  (chat.js)           │                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │ HTTP / SSE
┌──────────────────────▼───────────────────────────────────────┐
│                      后端层 (FastAPI)                        │
│  API Routers (chat/upload/faq/database/health)              │
│       │                                                      │
│       ▼                                                      │
│  AgentRouter (app/agent/router.py) ◄── 核心调度中心          │
│       │                                                      │
│       ├──► Skills 检索 (app/skills/base.py)                 │
│       │         └── JSON 文件关键词匹配                      │
│       ├──► RAG 检索 (app/rag/chroma_store.py)               │
│       │         └── ChromaDB 相似度搜索                      │
│       └──► MCP Engine (app/mcp/engine.py)                   │
│                 ├── ModelSelector → 选择外部模型             │
│                 ├── ContextBuilder → 组装 system/user msg    │
│                 └── PromptEngine → 意图识别 + Query增强      │
│                       │                                      │
│                       ▼                                      │
│              具体 Agent (deepseek/claude/...)               │
│                       │                                      │
│                       ▼                                      │
│              外部 LLM API (HTTP Streaming)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 核心数据流

以 **流式对话** (`POST /api/chat/stream`) 为例：

1. **前端输入**：用户在 `ChatWindow.vue` 输入问题，Pinia Store 添加用户消息，调用 `api.chatStream()` 通过 Fetch 发送 SSE 请求。
2. **后端接收**：`ChatRequest` 校验参数后调用 `agent_router.chat_stream()`。
3. **Agent 路由调度**：
   - **Skills 检索**：基于关键词子串匹配从 JSON 技能库检索相关知识。
   - **RAG 检索**：ChromaDB 向量相似度搜索（当前 Embedding 为 Mock）。
   - **MCP 准备上下文**：组装完整的 System Prompt + 知识块 + 历史对话。
4. **MCP 引擎处理**：
   - `PromptEngine.analyze(query)`：意图识别（故障排查/技巧/参数/方案/SQL/通用），Query 增强。
   - `ContextBuilder.build(...)`：构建 system prompt + 知识块 + 历史对话 + 当前问题。
   - `ContextWindowManager.trim(messages)`：按 token 估算截断，保留 system 和最近用户消息。
   - `ModelSelector.select(db_type)`：选择目标模型。
5. **模型选择策略**：
   - 若 `db_type` 为自研数据库 (`self_db`) → **强制路由到 Claude**（深度推理）。
   - 否则按 `EXTERNAL_MODEL_PRIORITY` 优先级选择外部模型（默认 DeepSeek → 豆包 → 文心 → OpenAI）。
   - 支持 `priority` / `round_robin` / `random` 三种策略。
6. **模型调用**：对应 Agent 通过 `httpx.AsyncClient` 调用外部 API，流式模式下逐 chunk 返回 SSE 数据。
7. **异常降级**：若主模型失败且 `FALLBACK_ENABLED=true`，自动按优先级尝试其他模型，流式场景下会发送 `[模型服务异常，正在切换备用模型...]` 提示。
8. **前端渲染**：`api/index.js` 解析 SSE 数据逐 chunk 追加，`store.appendStreaming(chunk)` 实现打字机效果，收到 `[DONE]` 后完成渲染。

---

## 模块职责说明

| 层级 | 模块 | 核心职责 |
|------|------|---------|
| **前端** | `ChatWindow.vue` | 用户交互核心：输入框、消息列表、流式打字机效果 |
| | `MessageBubble.vue` | 消息渲染：Markdown 解析、代码高亮、分段展示 |
| | `Pinia Store` | 维护消息列表、当前数据库类型、流式状态 |
| | `api/index.js` | 封装 Axios 普通请求 + Fetch SSE 流式解析 |
| **API层** | `app/api/chat.py` | 提供 `/api/chat` 和 `/api/chat/stream` 两个端点 |
| | `app/api/upload.py` | 文档上传、解析、分块、写入 ChromaDB |
| **调度层** | `AgentRouter` | 统一入口：先查 Skills，再查 RAG，最后走 MCP → Agent |
| **知识层** | `Skills` | 基于 JSON 文件的关键词子串匹配，返回结构化知识 |
| | `RAG` | ChromaDB 向量相似度检索（当前 Embedding 为 Mock） |
| **MCP层** | `PromptEngine` | 关键词意图识别（5 类）+ Query 增强模板 |
| | `ContextBuilder` | 组装 System Prompt + 知识块 + 历史对话 |
| | `ModelSelector` | 自研库强制 Claude，其他按优先级/轮询/随机选择 |
| | `ContextWindowManager` | Token 估算截断，保留 System 和最近消息 |
| **模型层** | `DeepSeekAgent` | 默认通用模型，OpenAI 兼容格式 |
| | `ClaudeAgent` | 自研数据库专用，OpenAI 格式转 Anthropic 格式 |
| | `Doubao/Wenxin/OpenAI` | 备选模型，支持故障自动降级 Fallback |
| **基建层** | `config.py` | `.env` + `config.yaml` 双源配置，环境变量优先 |
| | `logger.py` | structlog JSON 结构化日志 |
| | `middleware.py` | 请求追踪、耗时统计 |

---

## 核心设计原理

### 1. 双知识源检索

系统同时查询两个知识源，将结果合并后注入 Prompt：

- **Skills（结构化知识）**：预置的 JSON 文件，通过关键词子串匹配快速召回。适合常见问题、标准排查步骤。
- **RAG（文档知识）**：用户上传的文档经解析、分块、向量化后存入 ChromaDB，通过语义相似度检索。适合私有文档、内部规范。

### 2. MCP 三层分离

受 MCP (Model-Context-Prompt) 架构启发，将大模型调用拆分为三层：

- **Model**：负责选择最合适的 LLM，管理上下文窗口，处理模型故障降级。
- **Context**：负责构建高质量的上下文，包括 System Prompt、检索到的知识块、历史对话。
- **Prompt**：负责理解用户意图，对 Query 进行增强（如自动添加"请提供排查思路、根因分析"等后缀），并对最终答案进行分段格式化。

### 3. 模型路由策略

- **自研数据库 (`self_db`)**：强制路由到 **Claude**，利用其深度推理能力处理复杂的内部架构问题。
- **通用数据库**：按 `EXTERNAL_MODEL_PRIORITY` 优先级选择（默认 DeepSeek → 豆包 → 文心 → OpenAI）。
- **故障降级**：主模型调用失败时，自动按优先级尝试下一个模型，流式场景下会发送切换提示。

### 4. 意图识别驱动

基于关键词匹配识别 5 种意图，自动套用不同的 Query 模板：

| 意图 | 触发词 | Query 增强 |
|------|--------|-----------|
| 故障排查 | 排查、报错、宕机、慢 | 请提供排查思路、根因分析、解决步骤 |
| 实用技巧 | 技巧、优化、命令、查看 | 请提供具体操作命令、SQL语句 |
| 参数配置 | 参数、调优、内存、并发 | 请推荐参数值、说明影响范围、风险点 |
| 解决方案 | 方案、迁移、备份、恢复 | 请提供完整方案、回滚预案 |
| SQL相关 | sql、查询、索引、执行计划 | 请提供SQL语句、执行计划分析 |

---

## 当前限制与注意事项

1. **Embedding 为 Mock**：`MockEmbeddings` 返回零向量，RAG 检索实际无法按语义召回，需替换为真实的 `HuggingFaceEmbeddings` 或 API Embedding。
2. **Skills 为简单子串匹配**：未使用 BM25 或向量检索，精度有限。
3. **意图识别为关键词规则**：未使用分类模型，对新说法覆盖不足。
4. **SQL 安全检查**：配置中声明了危险关键词，但当前仅打印日志，未实际拦截执行。

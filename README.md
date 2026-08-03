# AI-Knowledge-Assistant

> 个人知识库 RAG 问答助手:上传文档 → 自动切片向量化 → 基于检索增强生成(RAG)回答你的问题,并**逐条附上引用来源**。

基于 FastAPI + Qdrant + DeepSeek 从零实现,完整记录每一课的知识点与踩坑(见 [项目历程.md](项目历程.md))。

## ✨ 功能特性

- **注册 / 登录**:JWT 认证 + bcrypt 密码哈希
- **文档上传**:PDF / TXT / Markdown → 解析 → 滑动窗口切片 → BGE 向量化入库
- **多轮会话问答**:RAG 链路(检索 top-k → 拼 prompt → DeepSeek 生成),带对话历史上下文
- **引用溯源**:回答中的 `[n]` 对应具体文档片段,来源以结构化数据落库
- **多租户数据隔离**:所有用户共享向量库,通过 payload filter 隔离,用户间数据互不可见(有测试证明)
- **删除联动**:删除文档时 MySQL 与向量库同步清理

## 🧱 技术栈

| 层次 | 技术 |
|---|---|
| Web 框架 | FastAPI + Uvicorn |
| ORM | SQLAlchemy 2.0(async)+ asyncmy |
| 数据库 | MySQL 8.4(Docker) |
| 认证 | PyJWT + bcrypt |
| 文档解析 | pypdf |
| Embedding | sentence-transformers + `BAAI/bge-small-zh-v1.5`(512 维) |
| 向量数据库 | Qdrant(Docker,cosine) |
| LLM | DeepSeek(OpenAI 兼容协议) |

## 🏗️ 架构

```
                    ┌─────────────────────────────────────────────┐
                    │                  FastAPI                    │
                    │  JWT 认证 → 用户/会话/消息/文档(MySQL)       │
                    │                                             │
用户 ──HTTP──►      │  上传: 解析 → 切片 → BGE编码 → Qdrant       │
                    │  问答: 问题编码 → Qdrant检索(top-k)          │
                    │        → 资料+历史拼prompt → DeepSeek       │
                    │        → 回答 + sources(引用溯源)           │
                    └─────────────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 基础设施(Docker)

```bash
# MySQL 8.4
docker run -d --name ai-knowledge-mysql \
  -e MYSQL_ROOT_PASSWORD=root123456 -e MYSQL_DATABASE=ai_knowledge \
  -e MYSQL_USER=app -e MYSQL_PASSWORD=app123456 \
  -p 3306:3306 mysql:8.4

# Qdrant 向量库
docker run -d --name ai-knowledge-qdrant -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

### 2. 配置

```bash
cp .env.example .env
# 修改 .env:SECRET_KEY(≥32 字节随机串)、DEEPSEEK_API_KEY
```

### 3. 安装依赖 + 建表 + 启动

```bash
pip install -r requirements.txt
python -m app.init_db                # 建表
python -m uvicorn app.main:app --reload --reload-dir app
```

打开 <http://127.0.0.1:8000/docs> 查看交互式 API 文档。

> 💡 国内网络提示:模型下载走 HuggingFace 镜像 `HF_ENDPOINT=https://hf-mirror.com`;若 qdrant-client 请求 localhost 报 502(代理劫持),设置 `no_proxy=localhost,127.0.0.1`。

## 📡 API 一览(前缀 `/api/v1`)

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/auth/register` | 注册,返回 token |
| POST | `/auth/login` | 登录,返回 token |
| GET | `/users/me` | 当前用户信息 |
| POST | `/conversations` | 创建会话 |
| GET | `/conversations` | 会话列表 |
| GET | `/conversations/{id}` | 会话详情(归属校验,越权 404) |
| DELETE | `/conversations/{id}` | 删除会话 |
| POST | `/conversations/{id}/messages` | 发消息(RAG 问答,返回 assistant 回答 + sources) |
| GET | `/conversations/{id}/messages` | 消息列表 |
| POST | `/documents/upload` | 上传文档(三道校验:类型/大小/数量) |
| GET | `/documents` | 文档列表 |
| DELETE | `/documents/{id}` | 删除文档(MySQL + 向量库联动) |

## 📁 项目结构

```
app/
├── main.py               # FastAPI 入口,路由挂载
├── core/                 # 配置(pydantic-settings)、安全(JWT/bcrypt)
├── db/                   # 异步引擎、会话、ORM 基类
├── models/               # User / Conversation / Message / Document
├── schemas/              # Pydantic 请求响应模型
├── api/
│   ├── deps.py           # 依赖注入(get_db / get_current_user)
│   └── routers/          # auth / users / conversations / documents
└── services/
    ├── parser.py         # PDF/TXT/MD → 纯文本
    ├── chunker.py        # 滑动窗口切片
    ├── vector_store.py   # Qdrant 封装(建库/入库/检索/删除)
    └── rag.py            # RAG 组装(检索→拼prompt→DeepSeek→引用)
```

## 🔐 安全设计

- 密码 bcrypt 加盐哈希,库中无明文
- JWT 无状态认证,`sub` 存用户 id
- 资源归属校验:访问他人资源统一 404(不暴露存在性)
- 上传防护:文件名净化(防路径穿越)+ UUID 重命名 + 按用户分目录
- 多租户隔离:向量检索强制 `user_id` payload filter

## 📚 学习历程

项目从零开始开发,共九课,每一课的知识点、踩坑与验证方式记录在 [项目历程.md](项目历程.md)。

## 📝 TODO

- [ ] Streamlit 前端(上传 + 聊天 + 引用展示)
- [ ] Docker 化部署

# 本段代码由AI辅助生成
# RAG-QA-System - 基于本地知识库的 RAG 智能问答系统

> **一句话简介**：一个基于 Ollama + LangChain + ChromaDB + Streamlit 的本地知识库问答系统，支持上传 PDF/DOCX 文档并基于文档内容进行多轮对话问答。

---

## 一、环境要求

### 1. Python 环境
- Python 3.10 或更高版本
- pip 包管理器

### 2. Ollama 安装与模型下载

本项目依赖本地运行的 Ollama 服务，请先完成以下步骤：

```bash
# 1. 下载并安装 Ollama
#    访问 https://ollama.com/ 下载 Windows 版本并安装

# 2. 下载大语言模型（问答用）
ollama pull deepseek-r1:7b

# 3. 下载嵌入模型（向量化用）
ollama pull nomic-embed-text

# 4. 验证模型已安装
ollama list
```

运行后应能看到 `deepseek-r1:7b` 和 `nomic-embed-text` 两个模型。

---

## 二、安装步骤

```bash
# 1. 克隆项目到本地
git clone https://github.com/bdalxy/RAG-QA-System-tc-2405030206.git
cd RAG-QA-System-tc-2405030206

# 2. 创建 Python 虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
#    Windows PowerShell:
.\venv\Scripts\Activate.ps1
#    Windows CMD:
venv\Scripts\activate.bat

# 4. 安装项目依赖
pip install -r requirements.txt
```

---

## 三、使用说明

### 启动 Web 应用

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`。

### 操作流程

1. **上传文档**
   - 在左侧边栏点击 "Browse files" 按钮
   - 选择一份或多份 PDF / DOCX 文档（至少 5 份 NLP 相关文档）

2. **构建知识库**
   - 点击 "📥 加入知识库" 按钮
   - 系统会自动解析文档、文本分块、向量化并存入 ChromaDB
   - 侧边栏会显示当前知识库状态（文档数量、文本块数量）

3. **开始提问**
   - 在主区域底部输入框中输入问题
   - 系统会从知识库检索相关内容，由 DeepSeek-R1 模型生成回答
   - 回答下方可展开查看参考来源（引用的文档片段）

4. **多轮对话**
   - 系统自动维护对话上下文，可以进行追问或关联提问
   - 点击 "🗑️ 清除对话历史" 可重置对话记忆

5. **加载已有知识库**
   - 如果之前已构建过知识库，点击 "🔄 加载已有知识库" 即可恢复

---

## 四、项目结构

```
RAG-QA-System/
├── app.py                  # Streamlit Web 主程序
├── test_ollama.py          # Ollama 连通性测试脚本
├── requirements.txt        # Python 依赖清单
├── README.md               # 项目说明文档（本文件）
├── AI_Usage_Log.md         # AI 使用日志
├── .gitignore              # Git 忽略文件配置
├── docs/                   # 存放待加载的 PDF/DOCX 文档样例
├── chroma_db/              # ChromaDB 向量库持久化目录（自动生成）
└── src/
    ├── __init__.py         # 包初始化文件
    ├── config.py           # 全局配置（模型名、路径、提示词等）
    ├── document_loader.py  # 文档加载与文本分块
    ├── vector_store.py     # 向量化存储与检索
    └── rag_chain.py        # RAG 问答链（含命令行测试入口）
```

---

## 五、关键技术点说明

### RAG 流程
1. **文档加载**：支持 PDF（PyPDFLoader）和 DOCX（Docx2txtLoader）格式
2. **文本分块**：使用 `RecursiveCharacterTextSplitter`，chunk_size=1000，chunk_overlap=200
3. **向量化**：使用 Ollama 内置的 `nomic-embed-text` 模型将文本块转为向量
4. **向量存储**：使用 ChromaDB 进行本地持久化存储
5. **相似性检索**：基于余弦相似度返回最相关的 3 个文本块
6. **答案生成**：将检索结果注入自定义提示词，由 `deepseek-r1:7b` 模型生成回答
7. **对话记忆**：使用 `ConversationBufferMemory` 维护多轮对话上下文

### 所用模型
| 模型 | 用途 | 来源 |
|------|------|------|
| `deepseek-r1:7b` | 大语言模型，负责问答推理与生成 | Ollama 部署 |
| `nomic-embed-text` | 嵌入模型，负责文本向量化 | Ollama 部署 |

### 嵌入方式
使用 `OllamaEmbeddings(model="nomic-embed-text")` 通过 Ollama API 调用本地嵌入模型。

---

## 六、项目效果截图

> 📸 **截图 1：Web 应用主界面（含侧边栏和对话区域）**
>
> *（请在此处插入 Streamlit 应用整体界面的截图）*

> 📸 **截图 2：文档上传与知识库构建过程**
>
> *（请在此处插入上传文档后点击"加入知识库"的成功提示截图）*

> 📸 **截图 3：问答示例（含参考来源展开）**
>
> *（请在此处插入一个问答交互的截图，展示问题、回答和参考来源）*

---

## 七、本地打包（PyInstaller）

```bash
pyinstaller --onedir --name RAG-QA-System --add-data "chroma_db;chroma_db" app.py
```

注意：打包后的 exe 文件需要 **本机已安装 Ollama** 且 **已下载 deepseek-r1:7b 和 nomic-embed-text 模型**。

---

## 八、已知问题与改进方向

### 已知问题
1. deepseek-r1:7b 的推理式输出会包含 `</think>` 标记，回答中可能包含思考过程文本
2. 大文件上传时向量化速度较慢，取决于本机 CPU/GPU 性能
3. PDF 中扫描件（图片型 PDF）无法提取文字
4. Streamlit 每次刷新会重建 RAG 链，有一定性能开销

### 改进方向
- [ ] 更换为非推理模型（如 qwen2:7b）以获得更简洁的回答输出
- [ ] 增加 OCR 支持，处理扫描件 PDF
- [ ] 支持更多文档格式（txt, md, epub）
- [ ] 添加夜间模式切换
- [ ] 支持问答记录导出（CSV/PDF）
- [ ] 添加批量上传进度条
- [ ] 优化向量库增量更新时的去重逻辑

---

## 九、致谢

- [Ollama](https://ollama.com/) — 本地大模型部署平台
- [LangChain](https://python.langchain.com/) — LLM 应用开发框架
- [ChromaDB](https://www.trychroma.com/) — 向量数据库
- [Streamlit](https://streamlit.io/) — Web 应用框架
- [DeepSeek](https://www.deepseek.com/) — 开源大语言模型
# 本段代码由AI辅助生成
# RAG-QA-System - 基于本地知识库的 RAG 智能问答系统

> **一句话简介**：一个基于 Ollama + LangChain + ChromaDB + Streamlit 的本地知识库问答系统

---

## 一、环境要求

### 1. Python 环境
- Python 3.10 或更高版本
- pip 包管理器

### 2. Ollama 安装与模型下载

```bash
# 下载大语言模型（问答用）
ollama pull deepseek-r1:7b

# 下载嵌入模型（向量化用）
ollama pull nomic-embed-text

# 验证模型已安装
ollama list
```

---

## 二、安装步骤

```bash
git clone https://github.com/bdalxy/RAG-QA-System-tc-2405030206.git
cd RAG-QA-System-tc-2405030206
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 三、使用说明

```bash
streamlit run app.py
```

浏览器将自动打开 `http://localhost:8501`。

---

## 四、项目结构

```
RAG-QA-System/
├── app.py                  # Streamlit Web 主程序
├── test_ollama.py          # Ollama 连通性测试脚本
├── requirements.txt        # Python 依赖清单
├── README.md               # 项目说明文档
├── AI_Usage_Log.md         # AI 使用日志
├── .gitignore              # Git 忽略文件配置
├── pdf/                    # 知识库文档（5份NLP论文PDF）
└── src/
    ├── __init__.py         # 包初始化文件
    ├── config.py           # 全局配置
    ├── document_loader.py  # 文档加载与文本分块
    ├── vector_store.py     # 向量化存储与检索
    └── rag_chain.py        # RAG 问答链
```

---

## 五、关键技术点

### RAG 流程
1. 文档加载：PDF（PyPDFLoader）和 DOCX（Docx2txtLoader）
2. 文本分块：RecursiveCharacterTextSplitter，chunk_size=1000，chunk_overlap=200
3. 向量化：nomic-embed-text 模型
4. 向量存储：ChromaDB 本地持久化
5. 相似性检索：余弦相似度，返回最相关3个文本块
6. 答案生成：deepseek-r1:7b 模型
7. 对话记忆：ConversationBufferMemory

### 所用模型
| 模型 | 用途 |
|------|------|
| deepseek-r1:7b | 问答推理与生成 |
| nomic-embed-text | 文本向量化 |

---

## 六、项目效果截图

> 截图1：Web 应用主界面（请运行后截取）
> 截图2：文档上传与知识库构建过程（请运行后截取）
> 截图3：问答示例（请运行后截取）

---

## 七、本地打包

```bash
pyinstaller --onedir --name RAG-QA-System --add-data "chroma_db;chroma_db" app.py
```

---

## 八、已知问题与改进方向

### 已知问题
1. deepseek-r1:7b 推理式输出含思考过程文本
2. 大文件向量化速度取决于本机性能
3. PDF 扫描件无法提取文字
4. Streamlit 每次刷新重建 RAG 链

### 改进方向
- 更换非推理模型获得更简洁输出
- 增加 OCR 支持
- 支持更多文档格式
- 添加夜间模式
- 问答记录导出
- 批量上传进度条
- 向量库增量去重优化

---

## 九、致谢

- Ollama — 本地大模型部署平台
- LangChain — LLM 应用开发框架
- ChromaDB — 向量数据库
- Streamlit — Web 应用框架
- DeepSeek — 开源大语言模型
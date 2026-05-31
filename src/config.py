# 本段代码由AI辅助生成
"""
RAG-QA-System 全局配置文件
定义项目中使用的所有常量，包括模型名称、持久化路径等。
"""

# --- 向量数据库持久化路径 ---
# ChromaDB 向量库在本地磁盘的存储目录
PERSIST_DIRECTORY = "./chroma_db"

# --- 嵌入模型配置 ---
# 使用 Ollama 内置的 nomic-embed-text 模型进行文本向量化
# 该模型会将文本转换为 768 维的向量表示，用于语义检索
EMBEDDING_MODEL = "nomic-embed-text"

# --- 大语言模型配置 ---
# 使用 Ollama 部署的 DeepSeek-R1 7B 模型作为问答后端
LLM_MODEL = "deepseek-r1:7b"

# --- 文本分块参数 ---
# 每个文本块的最大字符数
CHUNK_SIZE = 1000
# 相邻文本块之间的重叠字符数，保证语义连续性
CHUNK_OVERLAP = 200

# --- 检索参数 ---
# 每次检索返回的最相关文本块数量
RETRIEVAL_K = 3

# --- RAG 系统提示词 ---
# 自定义系统提示词，要求模型严格基于提供的文档片段回答
# {context} 占位符会在运行时被实际的检索结果替换
SYSTEM_PROMPT = """你是一个基于内部知识库的问答助手。
请严格根据以下提供的参考文档片段回答问题。
如果文档中没有相关信息，请直接回答："文档中未找到相关答案"，不要编造任何内容。

参考文档片段：
{context}"""

# --- 支持的文件格式 ---
# 定义系统能够处理的文档格式及其对应的扩展名
SUPPORTED_EXTENSIONS = (".pdf", ".docx")

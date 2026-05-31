# 本段代码由AI辅助生成
"""
向量化存储与检索模块
负责将文本块向量化并存入 Chroma 向量数据库，
同时提供检索功能，根据查询返回最相关的文本块。
"""

import os
from typing import List, Optional

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from .config import EMBEDDING_MODEL, PERSIST_DIRECTORY, RETRIEVAL_K


def get_embeddings() -> OllamaEmbeddings:
    """
    获取 Ollama 嵌入模型实例。

    使用 nomic-embed-text 模型将文本转换为向量表示。
    该模型是 Ollama 内置的轻量级嵌入模型，无需额外下载大型模型。

    返回:
        OllamaEmbeddings: 已配置好的嵌入模型实例
    """
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    print(f"[嵌入模型] 已加载模型: {EMBEDDING_MODEL}")
    return embeddings


def create_vector_store(
    chunks: List[Document],
    persist_dir: str = PERSIST_DIRECTORY
) -> Chroma:
    """
    创建新的 Chroma 向量数据库并持久化到本地磁盘。

    工作流程：
    1. 获取嵌入模型实例
    2. 将文本块列表传入 Chroma.from_documents() 进行向量化
    3. Chroma 自动计算每个文本块的嵌入向量并存储
    4. 数据被持久化到指定的本地目录

    参数:
        chunks (List[Document]): 待向量化的文档块列表
        persist_dir (str): 向量库持久化目录路径，默认从 config 读取

    返回:
        Chroma: 已创建并持久化的 Chroma 向量数据库实例
    """
    # 确保持久化目录存在，如不存在则自动创建
    os.makedirs(persist_dir, exist_ok=True)

    # 获取嵌入模型
    embeddings = get_embeddings()

    # 创建 Chroma 向量数据库
    # from_documents 方法会：
    # 1. 对每个 Document 的 page_content 计算嵌入向量
    # 2. 将所有向量和元数据存入 Chroma
    # 3. 持久化到 persist_directory 指定的路径
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )

    print(f"[向量库创建] 已处理 {len(chunks)} 个文本块, "
          f"持久化目录: {persist_dir}")
    return vectordb


def load_vector_store(persist_dir: str = PERSIST_DIRECTORY) -> Optional[Chroma]:
    """
    从本地磁盘加载已存在的 Chroma 向量数据库。

    参数:
        persist_dir (str): 向量库持久化目录路径，默认从 config 读取

    返回:
        Optional[Chroma]: 加载成功返回 Chroma 实例，不存在则返回 None
    """
    # 检查持久化目录是否存在
    if not os.path.exists(persist_dir):
        print(f"[向量库加载] 持久化目录不存在: {persist_dir}")
        return None

    # 检查目录是否为空（即是否包含 Chroma 数据文件）
    # Chroma 使用 SQLite 存储，数据文件为 chroma.sqlite3
    chroma_db_file = os.path.join(persist_dir, "chroma.sqlite3")
    if not os.path.exists(chroma_db_file):
        print(f"[向量库加载] 数据库文件不存在: {chroma_db_file}")
        return None

    # 加载向量库
    embeddings = get_embeddings()
    vectordb = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings,
    )

    # 验证加载是否成功
    try:
        collection_count = vectordb._collection.count()
        print(f"[向量库加载] 成功加载, 当前文本块数量: {collection_count}")
    except Exception as e:
        print(f"[向量库加载] 加载失败: {str(e)}")
        return None

    return vectordb


def add_documents_to_store(
    vectordb: Chroma,
    chunks: List[Document]
) -> None:
    """
    向已有的 Chroma 向量库中添加新的文档块并持久化。

    参数:
        vectordb (Chroma): 已有的 Chroma 向量数据库实例
        chunks (List[Document]): 待添加的文档块列表
    """
    if not chunks:
        print("[添加文档] 没有需要添加的文档块")
        return

    before_count = vectordb._collection.count()

    # 向向量库添加文档块
    # add_documents 会自动计算嵌入向量并存储
    vectordb.add_documents(chunks)

    after_count = vectordb._collection.count()
    added_count = after_count - before_count

    print(f"[添加文档] 新增 {len(chunks)} 个文本块, "
          f"向量库总量: {before_count} -> {after_count} (增加 {added_count})")


def retrieve(
    vectordb: Chroma,
    query: str,
    k: int = RETRIEVAL_K
) -> List[Document]:
    """
    根据用户查询，从向量库中检索最相似的 k 个文本块。

    检索原理：
    1. 将用户查询通过嵌入模型转换为向量
    2. 在 Chroma 向量库中进行余弦相似度搜索
    3. 返回相似度最高的 k 个文本块

    参数:
        vectordb (Chroma): Chroma 向量数据库实例
        query (str): 用户查询文本
        k (int): 返回的最相关文本块数量，默认从 config 读取

    返回:
        List[Document]: 最相关的 k 个文档块列表，按相关度降序排列
    """
    # similarity_search 返回按相关度排序的文档列表
    results = vectordb.similarity_search(query, k=k)

    print(f"[检索完成] 查询: '{query[:50]}...', 返回 {len(results)} 个结果")
    return results

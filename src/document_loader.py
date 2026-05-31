# 本段代码由AI辅助生成
"""
文档加载与分割模块
负责从指定文件夹中批量读取 PDF 和 DOCX 文档，
并对提取的文本进行语义分块处理。
"""

import os
from typing import List

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from .config import SUPPORTED_EXTENSIONS, CHUNK_SIZE, CHUNK_OVERLAP


def load_documents_from_folder(folder_path: str) -> List[Document]:
    """
    遍历指定文件夹，加载所有 PDF 和 DOCX 文档。

    工作流程：
    1. 检查文件夹是否存在
    2. 遍历文件夹内所有文件
    3. 根据文件扩展名选择对应的加载器（PyPDFLoader 或 Docx2txtLoader）
    4. 将每个文档的内容加载为 LangChain Document 对象

    参数:
        folder_path (str): 存放文档的文件夹路径

    返回:
        List[Document]: 加载成功后的文档对象列表

    异常:
        FileNotFoundError: 文件夹路径不存在时抛出
        ValueError: 文件夹中没有支持的文档格式时抛出
    """
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"指定的文件夹不存在: {folder_path}")

    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"指定的路径不是文件夹: {folder_path}")

    all_documents: List[Document] = []
    supported_count = 0

    # 遍历文件夹中的所有文件
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # 跳过子目录，只处理文件
        if not os.path.isfile(file_path):
            continue

        # 获取文件扩展名并转为小写，方便比较
        _, ext = os.path.splitext(filename)
        ext_lower = ext.lower()

        try:
            # 根据文件扩展名选择对应的加载器
            if ext_lower == ".pdf":
                # 使用 PyPDFLoader 加载 PDF 文件
                loader = PyPDFLoader(file_path)
                documents = loader.load()
                all_documents.extend(documents)
                supported_count += 1
                print(f"[加载成功] PDF 文件: {filename}, 页数: {len(documents)}")

            elif ext_lower == ".docx":
                # 使用 Docx2txtLoader 加载 Word 文档
                loader = Docx2txtLoader(file_path)
                documents = loader.load()
                all_documents.extend(documents)
                supported_count += 1
                print(f"[加载成功] DOCX 文件: {filename}")

            else:
                # 跳过不支持的文件格式
                print(f"[跳过] 不支持的文件格式: {filename} (扩展名: {ext})")

        except Exception as e:
            # 捕获单个文件加载过程中的异常，继续处理后续文件
            print(f"[加载失败] 文件: {filename}, 错误信息: {str(e)}")
            continue

    # 检查是否有成功加载的文档
    if supported_count == 0:
        raise ValueError(
            f"文件夹 '{folder_path}' 中没有找到支持的文档格式 "
            f"({', '.join(SUPPORTED_EXTENSIONS)})"
        )

    print(f"\n[汇总] 共加载 {supported_count} 个文档, "
          f"生成 {len(all_documents)} 个 Document 对象")
    return all_documents


def split_documents(
    documents: List[Document],
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """
    使用 RecursiveCharacterTextSplitter 对文档列表进行分块处理。

    分块策略：
    - 递归地按分隔符（\\n\\n -> \\n -> 空格 -> 空字符）进行分割
    - 保证每个文本块在 chunk_size 范围内
    - 相邻块之间有 chunk_overlap 字符的重叠，保持语义连续性

    参数:
        documents (List[Document]): 待分块的文档对象列表
        chunk_size (int): 每个文本块的最大字符数，默认从 config 读取
        chunk_overlap (int): 相邻文本块之间的重叠字符数，默认从 config 读取

    返回:
        List[Document]: 分块后的文档对象列表
    """
    # 创建递归字符级文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # 按优先级从高到低的分隔符列表
        separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""],
        # 使用长度函数确保按字符数精确计算
        length_function=len,
    )

    # 执行分块操作
    chunks = text_splitter.split_documents(documents)

    print(f"[分块完成] 原始文档数: {len(documents)}, "
          f"分块后文本块数: {len(chunks)}, "
          f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    return chunks
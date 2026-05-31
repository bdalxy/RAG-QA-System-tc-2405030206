# 本段代码由AI辅助生成
"""
RAG 问答链模块
将检索器（Retriever）与大语言模型（LLM）连接，
构建完整的 RAG（检索增强生成）问答流水线。
支持对话记忆功能，实现多轮对话上下文理解。
"""

from typing import Optional

from langchain_ollama import OllamaLLM
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.chat import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_chroma import Chroma

from .config import LLM_MODEL, SYSTEM_PROMPT, RETRIEVAL_K
from .vector_store import load_vector_store


def get_llm() -> OllamaLLM:
    """
    获取 Ollama 大语言模型实例。

    使用 deepseek-r1:7b 模型，temperature 设为 0 以确保回答的确定性，
    减少模型"幻觉"，严格基于检索到的文档内容回答。

    返回:
        OllamaLLM: 已配置好的大语言模型实例
    """
    llm = OllamaLLM(
        model=LLM_MODEL,
        temperature=0,  # 温度设为 0，使输出更确定、更少随机性
    )
    print(f"[大模型] 已加载模型: {LLM_MODEL}, temperature=0")
    return llm


def create_rag_chain(
    vectordb: Chroma,
    memory: Optional[ConversationBufferMemory] = None
) -> ConversationalRetrievalChain:
    """
    创建完整的 RAG 问答链。

    工作流程：
    1. 从向量库获取检索器（retriever），配置检索 k 个最相关文本块
    2. 构建自定义系统提示词，要求模型严格基于文档回答
    3. 使用 ChatPromptTemplate 组合系统提示词和用户问题
    4. 如果是首次调用（无 memory），则创建对话记忆
    5. 通过 ConversationalRetrievalChain.from_llm 组装完整链路

    参数:
        vectordb (Chroma): 已加载的 Chroma 向量数据库实例
        memory (Optional[ConversationBufferMemory]): 对话记忆对象，
            如果为 None 则自动创建新的记忆实例

    返回:
        ConversationalRetrievalChain: 配置完成的 RAG 问答链
    """
    # 步骤1：从向量库获取检索器
    # search_type="similarity" 表示使用余弦相似度检索
    # search_kwargs={"k": RETRIEVAL_K} 设置每次检索返回 3 个最相关文本块
    retriever = vectordb.as_retriever(
        search_type="similarity",
        search_kwargs={"k": RETRIEVAL_K},
    )

    # 步骤2：构建自定义提示词模板
    # 系统消息：定义 AI 助手的行为规则
    system_message_prompt = SystemMessagePromptTemplate.from_template(
        SYSTEM_PROMPT
    )
    # 人类消息：用户问题的占位符
    human_message_prompt = HumanMessagePromptTemplate.from_template(
        "{question}"
    )

    # 步骤3：组合完整的 ChatPromptTemplate
    chat_prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        human_message_prompt,
    ])

    # 步骤4：处理对话记忆
    if memory is None:
        # 创建新的对话记忆，用于维护多轮对话的上下文
        memory = ConversationBufferMemory(
            memory_key="chat_history",      # 记忆在链中的键名
            return_messages=True,           # 返回消息对象而非字符串
            output_key="answer",            # 输出内容的键名
        )
        print("[对话记忆] 已创建新的对话记忆")

    # 步骤5：获取 LLM 实例
    llm = get_llm()

    # 步骤6：组装完整的 ConversationalRetrievalChain
    # combine_docs_chain_kwargs 中的 prompt 用于控制如何将检索结果与用户问题组合
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        # 将自定义提示词传入文档组合链
        combine_docs_chain_kwargs={"prompt": chat_prompt},
        # 返回源文档，方便用户查看回答依据
        return_source_documents=True,
        # 确保输出键名为 "answer"
        output_key="answer",
    )

    print("[RAG链] 问答链创建完成")
    return qa_chain


# ============================================================
# 命令行测试入口
# 用于在没有 Streamlit 界面的情况下，在终端中测试 RAG 问答效果
# 运行方式：python -m src.rag_chain
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("RAG-QA-System 命令行测试")
    print("=" * 60)

    # 1. 加载向量库
    print("\n[步骤1] 加载向量库...")
    vectordb = load_vector_store()

    if vectordb is None:
        build_command = (
            "python -c \"from src.document_loader import load_documents_from_folder, split_documents; "
            "from src.vector_store import create_vector_store; "
            "docs = load_documents_from_folder('./docs'); "
            "chunks = split_documents(docs); "
            "create_vector_store(chunks)\""
        )
        print("\n[错误] 未找到向量库！请先运行以下命令构建知识库：")
        print(f"  {build_command}")
        exit(1)

    # 2. 创建 RAG 问答链
    print("\n[步骤2] 创建 RAG 问答链...")
    qa_chain = create_rag_chain(vectordb)

    # 3. 定义测试问题
    # 前 5 个为文档相关问题，后 2 个为无关问题
    test_questions = [
        # --- 文档相关问题（应能基于知识库回答） ---
        # 对应 N19-1423: BERT 经典论文
        "BERT模型是如何通过双向预训练来提升语言理解能力的？",
        # 对应 2021.emnlp-main.132: Cross-Attention 与机器翻译
        "在机器翻译任务中，为什么只微调Cross-Attention层就能达到接近全参数微调的效果？",
        # 对应 2024.findings-acl.732: LLM 生成训练数据与逻辑谬误识别
        "如何使用大语言模型生成训练数据来解决逻辑谬误识别中的类别不平衡问题？",
        # 对应 2025.findings-emnlp.1392: 强化学习提升 NLU
        "强化学习方法PPO是如何提升大语言模型的语言理解能力的？",
        # 对应 2021.ccl-1.108: BERT 后训练方法
        "BERT预训练后，后训练（post-training）方法如何帮助模型适应特定领域任务？",

        # --- 无关问题（应回答"文档中未找到相关答案"） ---
        "2024年奥运会在哪个城市举办？",
        "Python的异步编程和同步编程有什么区别？",
    ]

    print("\n" + "=" * 60)
    print("开始测试问答")
    print("=" * 60)

    # 4. 循环提问并记录效果
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─' * 50}")
        print(f"[问题 {i}] {question}")
        print(f"{'─' * 50}")

        try:
            # 调用问答链获取回答
            result = qa_chain.invoke({"question": question})
            answer = result.get("answer", "未获取到回答")

            print(f"[回答] {answer}")

            # 显示参考源文档（如有）
            source_docs = result.get("source_documents", [])
            if source_docs:
                print(f"\n[参考源] 共 {len(source_docs)} 个文档片段:")
                for j, doc in enumerate(source_docs, 1):
                    source = doc.metadata.get("source", "未知来源")
                    preview = doc.page_content[:100].replace("\n", " ")
                    print(f"  {j}. [{source}] {preview}...")

        except Exception as e:
            print(f"[错误] 问答过程出现异常: {str(e)}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("请评估以上 5 个文档相关问题 + 2 个无关问题的回答质量。")
    print("=" * 60)
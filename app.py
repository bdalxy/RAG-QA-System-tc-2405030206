# 本段代码由AI辅助生成
"""
RAG-QA-System Streamlit 主程序
提供 Web 界面，支持文档上传、知识库构建、多轮问答对话等功能。
运行方式：streamlit run app.py
"""

import os
import tempfile
import shutil
import streamlit as st

# --- 导入项目自定义模块 ---
from src.config import PERSIST_DIRECTORY
from src.document_loader import load_documents_from_folder, split_documents
from src.vector_store import (
    create_vector_store,
    load_vector_store,
    add_documents_to_store,
)
from src.rag_chain import create_rag_chain


# ============================================================
# 页面配置
# ============================================================
st.set_page_config(
    page_title="RAG 本地知识库问答系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 自定义 CSS 样式
# ============================================================
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    .status-card {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .source-block {
        background: #e8f4fd;
        border-left: 4px solid #2196F3;
        padding: 0.5rem;
        margin: 0.5rem 0;
        font-size: 0.85rem;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# Session State 初始化
# 使用 st.session_state 维护跨请求的持久化状态
# ============================================================
def init_session_state() -> None:
    """初始化 Streamlit 会话状态中的所有关键变量"""
    # 对话历史：存储所有用户和助手的消息
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 向量库对象：当前加载的 Chroma 向量数据库实例
    if "vectordb" not in st.session_state:
        st.session_state.vectordb = None

    # 文档数量：已加入知识库的文档总数
    if "doc_count" not in st.session_state:
        st.session_state.doc_count = 0

    # 对话记忆：用于多轮对话的上下文记忆
    if "memory" not in st.session_state:
        from langchain_classic.memory import ConversationBufferMemory
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

    # 知识库文本块数量
    if "chunk_count" not in st.session_state:
        st.session_state.chunk_count = 0


# ============================================================
# 知识库构建函数
# ============================================================
def build_knowledge_base(uploaded_files) -> None:
    """
    处理用户上传的文件，构建/更新知识库。

    工作流程：
    1. 将上传的文件保存到临时目录
    2. 调用 document_loader 加载并解析文档
    3. 调用 split_documents 对文本进行分块
    4. 创建或更新 Chroma 向量库
    5. 更新 session_state 中的状态信息

    参数:
        uploaded_files: Streamlit file_uploader 返回的上传文件列表
    """
    if not uploaded_files:
        st.warning("请先上传文档文件！")
        return

    with st.spinner("正在处理文档，请稍候..."):
        try:
            # 步骤1：创建临时目录，将上传文件保存到磁盘
            temp_dir = tempfile.mkdtemp(prefix="rag_docs_")
            saved_count = 0

            for uploaded_file in uploaded_files:
                # 检查文件扩展名是否支持
                filename = uploaded_file.name
                _, ext = os.path.splitext(filename)
                if ext.lower() not in (".pdf", ".docx"):
                    st.warning(f"跳过不支持的文件格式: {filename}")
                    continue

                # 保存文件到临时目录
                file_path = os.path.join(temp_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                saved_count += 1

            if saved_count == 0:
                st.error("没有有效的文档文件被保存！")
                return

            st.info(f"已保存 {saved_count} 个文件，正在解析...")

            # 步骤2：加载文档
            documents = load_documents_from_folder(temp_dir)
            st.info(f"已加载 {len(documents)} 个文档页面")

            # 步骤3：文本分块
            chunks = split_documents(documents)
            st.info(f"已分割为 {len(chunks)} 个文本块")

            # 步骤4：创建或更新向量库
            if st.session_state.vectordb is None:
                # 首次构建：创建新的向量库
                st.session_state.vectordb = create_vector_store(chunks)
                st.session_state.doc_count = saved_count
            else:
                # 增量更新：向已有向量库添加文档
                add_documents_to_store(st.session_state.vectordb, chunks)
                st.session_state.doc_count += saved_count

            # 步骤5：更新状态
            st.session_state.chunk_count = (
                st.session_state.vectordb._collection.count()
            )

            st.success(f"知识库更新成功！当前文档数: {st.session_state.doc_count}, "
                       f"文本块数: {st.session_state.chunk_count}")

            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)

        except Exception as e:
            st.error(f"知识库构建失败: {str(e)}")


# ============================================================
# 侧边栏渲染
# ============================================================
def render_sidebar() -> None:
    """渲染 Streamlit 侧边栏，包含文档上传和知识库管理功能"""
    with st.sidebar:
        st.markdown("## 📁 知识库管理")

        # --- 文件上传组件 ---
        st.markdown("### 上传文档")
        uploaded_files = st.file_uploader(
            "支持 PDF 和 DOCX 格式",
            type=["pdf", "docx"],
            accept_multiple_files=True,  # 允许多文件上传
            help="选择一份或多份 PDF/DOCX 文档上传到知识库",
        )

        # --- 加入知识库按钮 ---
        if st.button("📥 加入知识库", type="primary", use_container_width=True):
            build_knowledge_base(uploaded_files)

        st.divider()

        # --- 知识库状态显示 ---
        st.markdown("### 📊 知识库状态")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("文档数量", st.session_state.doc_count)
        with col2:
            st.metric("文本块数", st.session_state.chunk_count)

        # 加载已有向量库的按钮
        if st.button("🔄 加载已有知识库", use_container_width=True):
            with st.spinner("正在加载向量库..."):
                vectordb = load_vector_store()
                if vectordb is not None:
                    st.session_state.vectordb = vectordb
                    st.session_state.chunk_count = (
                        vectordb._collection.count()
                    )
                    st.success(f"已加载知识库，共 {st.session_state.chunk_count} 个文本块")
                    st.rerun()
                else:
                    st.warning("未找到已存在的知识库，请先上传文档构建")

        st.divider()

        # --- 清除对话按钮 ---
        if st.button("🗑️ 清除对话历史", use_container_width=True):
            st.session_state.messages = []
            # 重置对话记忆
            from langchain_classic.memory import ConversationBufferMemory
            st.session_state.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer",
            )
            st.success("对话历史已清除")
            st.rerun()

        # --- 使用说明 ---
        st.divider()
        with st.expander("📖 使用说明"):
            st.markdown("""
            1. **上传文档**：点击"Browse files"选择 PDF/DOCX 文件
            2. **构建知识库**：点击"加入知识库"按钮
            3. **开始提问**：在下方输入框中输入问题
            4. **查看来源**：每次回答后会显示参考文档来源
            
            **提示**：
            - 确保 Ollama 服务已启动
            - 已下载 deepseek-r1:7b 和 nomic-embed-text 模型
            - 知识库数据保存在 `chroma_db/` 目录
            """)


# ============================================================
# 主区域渲染
# ============================================================
def render_main() -> None:
    """渲染 Streamlit 主区域，包含对话展示和问答交互"""
    # 标题
    st.markdown(
        '<div class="main-header"><h1>📚 RAG 本地知识库问答系统</h1>'
        '<p>基于 Ollama + LangChain + ChromaDB 构建</p></div>',
        unsafe_allow_html=True,
    )

    # --- 显示历史对话 ---
    st.markdown("### 💬 对话记录")
    chat_container = st.container()

    with chat_container:
        if not st.session_state.messages:
            st.info("👋 欢迎使用 RAG 问答系统！请先在侧边栏上传文档构建知识库，然后开始提问。")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

                # 如果是助手消息且包含源文档，显示参考来源
                if message["role"] == "assistant" and "sources" in message:
                    with st.expander("📎 查看参考来源"):
                        for i, source in enumerate(message["sources"], 1):
                            st.markdown(
                                f'<div class="source-block">'
                                f'<strong>来源 {i}:</strong> {source.get("source", "未知")}<br>'
                                f'{source.get("content", "")[:200]}...'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

    # --- 输入区域 ---
    st.markdown("### ✍️ 输入问题")

    # 使用 chat_input 组件（Streamlit 1.32+ 支持）
    if prompt := st.chat_input("请输入您的问题..."):
        # 检查向量库是否已初始化
        if st.session_state.vectordb is None:
            # 尝试自动加载已有的向量库
            vectordb = load_vector_store()
            if vectordb is not None:
                st.session_state.vectordb = vectordb
                st.session_state.chunk_count = vectordb._collection.count()
            else:
                st.error("❌ 知识库尚未构建！请先在侧边栏上传文档并点击'加入知识库'。")
                return

        # 将用户消息添加到对话历史
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
        })

        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 获取助手回答
        with st.chat_message("assistant"):
            with st.spinner("🤔 正在检索知识库并生成回答..."):
                try:
                    # 每次提问都重建 RAG 链（因为 memory 在 session_state 中）
                    qa_chain = create_rag_chain(
                        vectordb=st.session_state.vectordb,
                        memory=st.session_state.memory,
                    )

                    # 调用问答链
                    result = qa_chain.invoke({"question": prompt})
                    answer = result.get("answer", "抱歉，未能生成回答。")

                    # 提取源文档信息
                    source_docs = result.get("source_documents", [])
                    sources = []
                    for doc in source_docs:
                        sources.append({
                            "source": doc.metadata.get("source", "未知来源"),
                            "content": doc.page_content,
                        })

                    # 显示回答
                    st.markdown(answer)

                    # 显示参考来源
                    if sources:
                        with st.expander("📎 查看参考来源"):
                            for i, source in enumerate(sources, 1):
                                st.markdown(
                                    f'<div class="source-block">'
                                    f'<strong>来源 {i}:</strong> {source.get("source", "未知")}<br>'
                                    f'{source.get("content", "")[:200]}...'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )

                    # 将助手消息保存到对话历史
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                except Exception as e:
                    error_msg = f"问答过程出错: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": [],
                    })


# ============================================================
# 主入口
# ============================================================
def main() -> None:
    """Streamlit 应用主入口函数"""
    # 初始化会话状态
    init_session_state()

    # 渲染侧边栏
    render_sidebar()

    # 渲染主区域
    render_main()


if __name__ == "__main__":
    main()
# 本段代码由AI辅助生成
"""
RAG-QA-System 模型连通性测试脚本
用于验证 Ollama 服务是否正常运行，
以及 deepseek-r1:7b 和 nomic-embed-text 模型是否可用。
"""

import sys
from langchain_ollama import OllamaLLM, OllamaEmbeddings


def test_llm() -> bool:
    """
    测试大语言模型连通性。
    使用 deepseek-r1:7b 发送测试问题，验证是否能正常响应。

    返回:
        bool: 测试通过返回 True，失败返回 False
    """
    try:
        print("[测试1] 正在测试 LLM 连通性 (deepseek-r1:7b)...")
        llm = OllamaLLM(model="deepseek-r1:7b")
        response = llm.invoke("你好，1+1等于几？")
        print(f"[测试1 通过] 响应片段: {response[:200]}...")
        return True
    except Exception as e:
        print(f"[测试1 失败] 错误: {e}")
        return False


def test_embeddings() -> bool:
    """
    测试嵌入模型连通性。
    使用 nomic-embed-text 对测试文本进行向量化，验证嵌入服务是否正常。

    返回:
        bool: 测试通过返回 True，失败返回 False
    """
    try:
        print("[测试2] 正在测试 Embedding 连通性 (nomic-embed-text)...")
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        result = embeddings.embed_query("测试文本向量化")
        print(f"[测试2 通过] 向量维度: {len(result)}")
        return True
    except Exception as e:
        print(f"[测试2 失败] 错误: {e}")
        return False


def main() -> int:
    """
    主测试函数，依次测试 LLM 和 Embedding 模型连通性。

    返回:
        int: 全部通过返回 0，任一失败返回 1
    """
    print("=" * 50)
    print("RAG-QA-System Ollama 连通性测试")
    print("=" * 50)

    llm_ok = test_llm()
    emb_ok = test_embeddings()

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    print(f"  LLM (deepseek-r1:7b):       {'通过' if llm_ok else '失败'}")
    print(f"  Embedding (nomic-embed-text): {'通过' if emb_ok else '失败'}")
    print("=" * 50)

    if llm_ok and emb_ok:
        print("\n所有测试通过！Ollama 服务连接正常，可以运行 RAG-QA-System。")
        return 0
    else:
        print("\n部分测试失败！请检查：")
        print("  1. Ollama 服务是否已启动 (运行 'ollama serve')")
        print("  2. 模型是否已下载 (运行 'ollama list')")
        print("  3. 如未下载模型，请运行：")
        print("     ollama pull deepseek-r1:7b")
        print("     ollama pull nomic-embed-text")
        return 1


if __name__ == "__main__":
    sys.exit(main())
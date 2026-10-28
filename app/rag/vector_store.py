import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.chains import RetrievalQA
from app.rag.knowledge_loader import load_all_knowledge
from app.config import settings
from loguru import logger

DB_PATH = "./faiss_db"

def build_vector_db():
    """构建FAISS向量库，首次运行调用一次"""
    logger.info("开始构建FAISS向量知识库...")
    texts = load_all_knowledge()
    # 使用兼容OpenAI接口的Embedding
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL
    )
    db = FAISS.from_texts(texts, embeddings)
    db.save_local(DB_PATH)
    logger.info(f"向量库构建完成，保存至 {DB_PATH}")
    return db

def get_vector_db():
    """加载本地FAISS向量库，如果不存在则重新构建"""
    embeddings = OpenAIEmbeddings(
        openai_api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL
    )
    if os.path.exists(DB_PATH):
        db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        db = build_vector_db()
    return db

def get_rag_chain(top_k: int = 3, temperature: float = 0.7):
    """获取RAG问答链，导览智能体调用"""
    db = get_vector_db()
    retriever = db.as_retriever(search_kwargs={"k": top_k})

    llm = ChatOpenAI(
        openai_api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
        temperature=temperature
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

import os
from langchain.text_splitter import RecursiveCharacterTextSplitter

def load_all_knowledge(folder_path: str = "knowledge_data"):
    """读取knowledge_data文件夹全部txt知识库文件，分割文本块"""
    all_text = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf‑8") as f:
                text = f.read()
                all_text.append(text)

    full_content = "\n".join(all_text)
    # 文本分割，把长文档切小块，用于向量入库
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "，"]
    )
    chunks = splitter.split_text(full_content)
    return chunks

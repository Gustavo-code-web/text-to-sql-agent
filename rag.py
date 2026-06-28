from db import get_db, get_schema_per_table
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIR = "D:\\JupyterProject2\\chroma_schema_db"
COLLECTION_NAME = "table_schemas"

embeddings = HuggingFaceEmbeddings(model_name = "BAAI/bge-small-zh-v1.5")

def build_schema_documents() -> list[Document]:
    """将每张表的结构做成Document（一表一文档）"""
    conn = get_db()

    try:
        schema_dict = get_schema_per_table(conn)
    finally:
        conn.close()

    docs = []
    for table_name,schema_text in schema_dict.items():
        doc = Document(
            page_content = schema_text,
            metadata = {'table_name': table_name},
        )
        docs.append(doc)
    return docs

def build_vectorstore():
    """把所有表文档向量化，存进Chroma（自动化持久到PERSIST_DIR）"""
    docs = build_schema_documents()

    vectorstore = Chroma.from_documents(
        documents = docs,
        embedding = embeddings,
        collection_name = COLLECTION_NAME,
        persist_directory = PERSIST_DIR
    )
    return vectorstore

def get_vectorstore() -> Chroma:
    """连接已存在的Chroma向量库（查询时用，不重新建库）"""
    return Chroma(
        collection_name = COLLECTION_NAME,
        embedding_function = embeddings,
        persist_directory = PERSIST_DIR
    )

def retrieve_relevant_schema(question: str, k: int = 5) -> str:
    """根据问题检索最相关的k张表结构，拼成文本返回"""
    vectorstore = get_vectorstore()
    docs = vectorstore.similarity_search(question, k=k)
    schema_text = "\n".join([doc.page_content for doc in docs])

    return schema_text
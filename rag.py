from db import get_db, get_schema_per_table
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

PERSIST_DIR = "D:\\JupyterProject2\\chroma_schema_db"
COLLECTION_NAME = "table_schemas"
EXAMPLES_PERSIST_DIR = "D:\\JupyterProject2\\chroma_examples_db"
EXAMPLES_COLLECTION = "sql_examples"

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

def train_sql(question: str, sql: str):
    """把一对【问题->正确SQL】存进向量数据库，让agent越用越聪明"""
    doc = Document(
        page_content=question,
        metadata={
            'sql': sql,
            'question': question
        }
    )
    vectorstore = Chroma(
        collection_name=EXAMPLES_COLLECTION,
        embedding_function=embeddings,
        persist_directory=EXAMPLES_PERSIST_DIR
    )
    vectorstore.add_documents([doc])

def retrieve_similar_examples(question: str, k: int = 3):
    """检索与当前问题最相似的历史【问题->SQL】示例，拼成few-shot文本"""
    vectorstore = Chroma(
        collection_name=EXAMPLES_COLLECTION,
        embedding_function=embeddings,
        persist_directory=EXAMPLES_PERSIST_DIR
    )
    try:
        docs = vectorstore.similarity_search(question, k=k)
    except Exception as e:
        print(f'示例库暂时为空：{e}')
        return ''

    if not docs:
        return ''

    example_text = "【参考历史示例（Few-Shot）】\n"
    for i, doc in enumerate(docs, 1):
        ex_question = doc.metadata.get('question', '未知问题')
        ex_sql = doc.metadata.get('sql', '未知SQL')
        example_text += f'--- 示例{i} ---'
        example_text += f'示例问题：{ex_question}\n'
        example_text += f'对应SQL：{ex_sql}\n\n'

    return example_text.strip()
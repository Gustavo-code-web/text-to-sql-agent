from state import AgentState
from langchain_openai import ChatOpenAI
import os
from db import get_schema, run_sql, get_db
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

class SQLoutput(BaseModel):
    thought_process: str = Field(description='一步步地思考过程，分析可能用到哪些表和字段')
    sql_query: str = Field(description='最终生成的可执行的MySQL语句，仅返回SQL语句，不要有别的markdown标记')

llm = ChatOpenAI(
    model = 'deepseek-v4-pro',
    api_key = os.environ.get('DEEPSEEK_API_KEY'),
    base_url = 'https://api.deepseek.com',
    max_retries = 2,
    reasoning_effort = 'high',
    extra_body = {'thinking': {'type': 'enabled'}}
)

def schema_node(state: AgentState) -> dict:
    """获取数据库结构，写入state"""
    conn = get_db()
    try:
        schema_text = get_schema(conn)
    finally:
        conn.close()

    return {'schema': schema_text}

def generate_sql_node(state: AgentState) -> dict:
    """根据question+schema，让LLM生成SQL语句"""
    question = state['question']
    schema = state['schema']
    error = state.get('error', False)
    error_msg = state.get('result', '')
    error_sql = state.get('sql', '')

    error_context = ""
    if error:
        error_context = f"""你的sql语句报错了，你生成的错误sql是{error_sql},MySQL的报错信息是{error_msg}。
请仔细阅读报错信息，修正错误，重新生成正确的SQL语句。"""

    parser = PydanticOutputParser(pydantic_object=SQLoutput)

    system_prompt = """
      你是一位资深的MySQL专家，你的唯一任务是：根据用户提供的自然语言问题，结合下方的【数据库表结构】，编写出准确、高效且安全的 SQL 查询语句。
      【数据库表结构】：{schema},【输出格式要求】：{format_instructions}，{error_context}
      在正式生成SQL前，你必须在‘thought_process’中先分析用户的问题：
      1.核心需求是什么？
      2.要用到哪几张表，哪些字段？
      3.多表关联的join条件？
      4.是否需要用到过滤条件（where），模糊查询（like），分组聚合（group by），条件判断（if/case when），窗口函数，排序规则等。
    """

    prompt = ChatPromptTemplate.from_messages([
        ('system', system_prompt),
        ('user', "用户问题: {question}")
    ])
    chain = prompt | llm | parser

    response = chain.invoke({
        'schema': schema,
        'question': question,
        'format_instructions': parser.get_format_instructions(),
        'error_context': error_context
    })

    return {'sql': response.sql_query}

def run_sql_node(state: AgentState) -> dict:
    """执行state中的SQL，并将结果或报错信息存入state。"""
    sql = state['sql']
    current_retry = state.get('retry_count', 0)
    conn = get_db()
    try:
        result = run_sql(conn, sql)
        if isinstance(result, str) and result.startswith("SQL执行出错"):
            return {'result': result, 'error': True, 'retry_count': current_retry + 1}
        else:
            return {'result': str(result),'error': False, 'retry_count': current_retry}

    finally:
        conn.close()

def explain_node(state: AgentState) -> dict:
    """将数据库结果翻译为自然语言回答用户"""
    question = state['question']
    result = state['result']
    system_prompt = """你是一个专业且贴心的数据分析师。
    你的任务是将【数据库查询结果】转化为通俗易懂的自然语言，回答用户的【原始问题】。

    【数据库查询结果】
    {result}

    【回答要求】：
    1. 直接回答问题，语气自然专业。
    2. 可以给用户解释 SQL 是怎么写的。
    3. 如果结果是空的（如 []），请委婉地告诉用户没有找到符合条件的数据。
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "用户的原始问题是: {question}")
    ])

    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        'question': question,
        'result': result,
        'sql': state['sql']
    })
    return {'answer': answer}




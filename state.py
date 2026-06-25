from typing import TypedDict
class AgentState(TypedDict):
    question: str      # 用户的问题
    schema: str        # 表结构（每列的列名）
    sql: str           # 生成的SQL语句
    result: str        # 执行结果
    answer: str        # 最终答案
    error: bool        # 是否报错
    retry_count: int   # 重试次数
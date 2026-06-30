from dotenv import load_dotenv
from graph import build_graph
import os
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from rag import train_sql
load_dotenv()

def main():
    postgres_url = os.getenv('POSTGRES_URL', '')
    with ConnectionPool(
        conninfo=postgres_url,
        max_size=20,
        kwargs={'autocommit': True}
    ) as pool:
        checkpointer = PostgresSaver(pool)
        checkpointer.setup()
        app = build_graph(checkpointer=checkpointer)
        config = {'configurable': {'thread_id': 'session_user_001'}}
        while True:
            question = input('\n输入你的问题(输入‘quit’或者‘exit’结束)：').strip()
            if question.lower() in ['quit', 'exit']:
                print('bye')
                break
            if not question:
                continue
            result = app.invoke({'question': question}, config=config)
            print(result['answer'])
            print(result['sql'])

            if result.get('error', False):
                print('本次执行出错')
                continue
            feedback = input("\n 若查询结果正确（按y存入数据库/其他键跳过）：").strip().lower()
            if feedback == 'y':
                train_sql(question, result['sql'])
                print('已存入')
            else:
                print('已跳过')

if __name__ == '__main__':
    main()
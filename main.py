from dotenv import load_dotenv
from graph import build_graph
import os
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
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
        question1 = "2024年报名人数最多的学科是哪个?"
        result1 = app.invoke({'question': question1}, config=config)
        print(result1['answer'])
        print(result1['sql'])
        question2 = "那他的平均学习天数是多少？"
        result2 = app.invoke({'question': question2}, config=config)
        print(result2['answer'])
        print(result2['sql'])

if __name__ == '__main__':
    main()
import os
from dotenv import load_dotenv
import pymysql

load_dotenv()

def get_db():
    """连接MySQL，返回一个连接对象conn"""
    conn = pymysql.connect(
        host = os.getenv('DB_HOST', 'localhost'),
        port = int(os.getenv('DB_PORT', '3306')),
        user = os.getenv('DB_USER', 'root'),
        password = os.getenv('DB_PASSWORD', 'topking1226@'),
        database = os.getenv('DB_NAME', 'mianshi'),
        charset = 'utf8',
        cursorclass = pymysql.cursors.DictCursor
    )
    return conn

def get_schema(conn) -> str:
    """取出数据库中所有表的结构（表名+列名），拼成文本返回给LLM"""
    schema_lines = []
    with conn.cursor() as cursor:
        cursor.execute('show tables;')
        tables = cursor.fetchall()

        for table_row in tables:
            table_name = list(table_row.values())[0]
            cursor.execute(f'desc {table_name};')
            columns = cursor.fetchall()

            col_details = []
            for col in columns:
                col_name = col['Field']
                col_type = col['Type']
                col_details.append(f'{col_name}({col_type})')

            schema_lines.append(f'表 {table_name}: {", ".join(col_details)}')

    return '\n'.join(schema_lines)


def run_sql(conn, sql: str) -> str:
    """执行SQL语句，返回查询结果"""
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()
            return rows

    except Exception as e:
        return f'SQL执行出错 {str(e)}'


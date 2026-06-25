from dotenv import load_dotenv
from graph import build_graph
load_dotenv()

def main():
    app = build_graph()
    question = "帮我拉一份 2020年7月份 的客户消费报表。我要看到每个人的 姓名、customer_id 以及这一个月他们在咱们这儿的 总消费金额。对了，金额必须按从大到小排个序。"
    result = app.invoke({"question": question})
    print(result['answer'])

if __name__ == '__main__':
    main()
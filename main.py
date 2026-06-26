from dotenv import load_dotenv
from graph import build_graph
load_dotenv()

def main():
    app = build_graph()
    question = "帮我统计一下 2023年10月份 这 5 天里，每天的整体销售总额(表的字段名可能是英文，你要自己去找正确的字段)。并且帮我算一下，每天的销售总额有没有达到 10万元 的及格线？最后，帮我画一张柱状图，展示这 5 天的销售总额趋势，并在图上画一条 10万元 的红色达标基准线。"
    result = app.invoke({"question": question})
    print(result['answer'])

if __name__ == '__main__':
    main()
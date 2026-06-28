from dotenv import load_dotenv
from graph import build_graph
load_dotenv()

def main():
    app = build_graph()
    question = "帮我分析 2024 年各学科的学员学习坚持情况。请筛选出 2024 年报名人数达到 50 人的学科，并按学科统计输出以下指标：报名总数、平均最长连续学习天数、坚持达标率（即最长连续学习天数≥3天的报名占比），以及人均累计观看时长。所有数值指标请保留 2 位小数，最终结果按坚持达标率降序排列。"
    result = app.invoke({"question": question})
    print(result['answer'])
    print(result['sql'])

if __name__ == '__main__':
    main()
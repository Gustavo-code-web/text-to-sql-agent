from dotenv import load_dotenv
from graph import build_graph
load_dotenv()

def main():
    app = build_graph()
    question = "特级教师有几个？分别是谁？"
    result = app.invoke({"question": question})
    print(result['answer'])

if __name__ == '__main__':
    main()
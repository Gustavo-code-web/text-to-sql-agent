from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import *

def should_retry(state: AgentState) -> str:
    """裁判函数，决定流向"""
    error = state.get('error')
    retry_count = state.get('retry_count', 0)
    if error and retry_count<3:
        print(f'正在进行第{retry_count}次重试')
        return 'retry'
    return 'continue'

def build_graph(checkpointer=None):
    graph = StateGraph(AgentState)

    graph.add_node('schema', schema_node)
    graph.add_node('generate_sql', generate_sql_node)
    graph.add_node('run_sql', run_sql_node)
    graph.add_node('chart', generate_and_run_chart_node)
    graph.add_node('explain', explain_node)

    graph.add_edge(START, 'schema')
    graph.add_edge('schema', 'generate_sql')
    graph.add_edge('generate_sql', 'run_sql')
    graph.add_conditional_edges('run_sql', should_retry, {'retry': 'generate_sql','continue': 'chart'})
    graph.add_edge('chart', 'explain')
    graph.add_edge('explain', END)
    return graph.compile(checkpointer=checkpointer)
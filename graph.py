from langgraph.graph import StateGraph, START, END
from state import AgentState
from nodes import *

def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node('schema', schema_node)
    graph.add_node('generate_sql', generate_sql_node)
    graph.add_node('run_sql', run_sql_node)
    graph.add_node('explain', explain_node)

    graph.add_edge(START, 'schema')
    graph.add_edge('schema', 'generate_sql')
    graph.add_edge('generate_sql', 'run_sql')
    graph.add_edge('run_sql', 'explain')
    graph.add_edge('explain', END)
    return graph.compile()
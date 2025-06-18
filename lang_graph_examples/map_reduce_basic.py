"""
This module is an example of a LangGraph that executes map-reduce.
The graph is similar to that in parallel_basic.py. The difference is that
this example uses three parallel nodes whereas parallel_basic.py uses two.
"""

import os
from typing import TypedDict, List
from typing_extensions import Annotated
import operator
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph

# ---------------------------------------------
# Step 1: Set up OpenAI.
# ----------------------------------------------

# Load API key from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Ensure the API key is available
if not api_key:
    raise ValueError("No API key found. Please check your .env file.")

# Create an OpenAI client
client = OpenAI(api_key=api_key)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# ---------------------------------------------
# Step 2: Define the shared state structure.
# Define the shared state with Annotated merge for summaries.
# The Annotated merge allows each agent to append a str
# (hte summary made by that agent) to the list of summaries.
# Without Annotated operator.add, the list, summaries, would be
# overwritten by each agent, instead of appending to it.

# ----------------------------------------------


class State(TypedDict):
    docs: List[str]
    summaries: Annotated[List[str], operator.add]
    final_summary: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.

# ----------------------------------------------

# There are multiple map_nodes. Each node is an agent.
# The j-th map_node agent calls summarize_nth_doc(j).


def summarize_nth_doc(n: int):
    '''
    Returns a function that summarizes the nth document in 
    state["docs"].
    This is an example of a function factory using closures.

    '''
    def fn(state):
        doc = state["docs"][n]
        content = llm.invoke(f"Summarize: {doc}").content
        # Append the singleton list containing content to
        # the list state["summaries"].
        # The Annotated operator.add appends a list to a list.
        # If x and y are lists then x + y is a list.
        return {"summaries": [content]}
    return fn


# Reduce node calls combine_summaries
def combine_summaries(state):
    '''
    Reads the list, state["summaries"], and combines the list
    of summaries into a single summary in state["final_summary"].

    '''
    text = "\n".join(state['summaries'])
    final = llm.invoke(f"Combine into a single summary: {text}").content
    return {"final_summary": final}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(State)

# # 4.2 Add nodes to the graph.
# 4.1 Create builder
builder = StateGraph(State)

# 4.2 Specify nodes of the graph
# Give a name to each node and specify the function
# that will be executed by the node.

# Add dummy entry node.
builder.add_node("entry_node", lambda x: x)

# Add 3 map nodes: map_node_0, map_node_1, map_node_2
# summarize_nth_doc(n) is the function fn(state) that
# returns a dict {"summaries": [content]}
for n in range(3):
    builder.add_node(f"map_node_{n}", summarize_nth_doc(n))

# Add reduce node
builder.add_node("reduce_node", combine_summaries)

# 4.3 Specify the edges between nodes of the graph.
for n in range(3):
    # Fan out: Connect entry_node to map nodes.
    builder.add_edge("entry_node", f"map_node_{n}")

    # Fan in: Connect map nodes to reduce node.
    builder.add_edge(f"map_node_{n}", "reduce_node")

# 4.4 Set the entry and finish nodes of the graph
builder.set_entry_point("entry_node")
builder.set_finish_point("reduce_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------

# graph_prompt, is a dict that specifies some fields of state.
graph_prompt = {
    # docs is a list of documents to summarize.
    "docs": [
        "Python is a programming language created by Guido and is used at colleges and schools.",
        "LangGraph is a Python library for building graphs that control how LLMs interact. It is used at Caltech.",
        "Map-Reduce is a distributed processing technique for large-scale data analysis."
    ]
}
# Execute the graph.
result = graph.invoke(graph_prompt)
# result is the final value of state.
print("\n✅ Final Summary:\n")
print(result['final_summary'])

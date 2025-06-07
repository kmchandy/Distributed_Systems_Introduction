"""
This module is an example of a LangGraph with a single node.
"""

import os
from typing import TypedDict
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

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# ---------------------------------------------
# Step 2: Define the shared state structure
# ----------------------------------------------


class MyState(TypedDict):
    question: str
    answer: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph. These are typically LLM
# agents.
# ----------------------------------------------


def answer_agent(state: MyState) -> dict:
    # The agent reads state["question"] and writes
    # state["answer"].
    response = llm.invoke(state["question"])
    return {"answer": response.content}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(MyState)

# 4.2 Add nodes to the graph.
# Give a name to the node and specify the function
# that will be executed by the node.
builder.add_node("answer_node", answer_agent)

# 4.3 Define the edges between nodes of the graph.
# In this case, the graph has a single node and
# no edges.

# 4.4 Specify the entry and finish points of the graph.
builder.set_entry_point("answer_node")
builder.set_finish_point("answer_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: Run the graph with an input
# The input is a dictionary that conforms to the
# state structure.
# In this case the entry point -- i.e. answer_node --
# is invoked with MyState["question"] set to
# "What is the capital of France?", while
# MyState["answer"] is empty.
# The result is the state after the nodes in the
# graph have been executed.
# ----------------------------------------------
result = graph.invoke({"question": "What is the capital of France?"})
print(result)

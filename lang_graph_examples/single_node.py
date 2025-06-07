"""
This module is a simple example of how to use LangGraph with OpenAI's GPT-3.5-turbo model.
The module has 5 steps:
1. Set up OpenAI API client.
2. Define a shared state structure using TypedDict.
3. Specify the functions that will be executed by nodes in the graph.
4. Build the state graph with nodes and edges.
5. Run the graph with an input.
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
# This structure is often a TypedDict.
# ----------------------------------------------


class QAState(TypedDict):
    question: str
    answer: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph
# ----------------------------------------------


def answer_func(state: QAState) -> dict:
    response = llm.invoke(state["question"])
    return {"answer": response.content}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------
builder = StateGraph(QAState)
# Add nodes to the graph
builder.add_node("answer_node", answer_func)

# Define the edges between nodes of the graph.
# In this case, the graph has a single node and
# no edges.
# Specify the entry and finish points of the graph.
builder.set_entry_point("answer_node")
builder.set_finish_point("answer_node")

graph = builder.compile()

# ---------------------------------------------
# Step 5: Run the graph with an input
# ----------------------------------------------
result = graph.invoke({"question": "What is the capital of France?"})
print(result)

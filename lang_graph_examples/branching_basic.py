"""
This module is a simple example of how to use LangGraph with OpenAI's GPT-3.5-turbo model.
The graph is an example of branching in LangGraph.
The module has 5 steps:
1. Set up OpenAI API client.
2. Define a shared state structure using TypedDict.
3. Specify the functions that will be executed by nodes in the graph.
4. Build the state graph with nodes and edges.
5. Run the graph with an input.
"""

import sys
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

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# ---------------------------------------------
# Step 2: Define the shared state structure
# This structure is often a TypedDict.
# ----------------------------------------------


class UserState(TypedDict):
    question: str
    answer: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph
# ----------------------------------------------

# Tech support agent


def tech_agent(state: UserState) -> dict:
    response = llm.invoke(f"Answer as tech support: {state['question']}")
    return {"answer": response.content}

# General help desk agent


def general_agent(state: UserState) -> dict:
    response = llm.invoke(f"Answer as general help desk: {state['question']}")
    return {"answer": response.content}

# Router function for branching


def router(state: UserState) -> str:
    if 'tech' in state['question'].lower():
        return {"next_node": "tech_node"}
    else:
        return {"next_node": "general_node"}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------
builder = StateGraph(UserState)

# Add nodes to the graph
builder.add_node("router_node", router)
builder.add_node("tech_node", tech_agent)
builder.add_node("general_node", general_agent)

# Add edges to the graph with conditional branching
builder.add_conditional_edges(
    "router_node",
    lambda x: x["next_node"],  # routing function
    {
        "tech_node": "tech_node",
        "general_node": "general_node"
    }
)

# Set the entry and finish points for the graph
builder.set_entry_point("router_node")
builder.set_finish_point("tech_node")
builder.set_finish_point("general_node")

graph = builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------
inputs = [
    {"question": "I need help with tech specs for my laptop."},
    {"question": "What are your office hours?"}
]

for i, inp in enumerate(inputs):
    print(f"\n❓ Input {i+1}: {inp['question']}")
    result = graph.invoke(inp)
    print("💬 Response:", result['answer'])

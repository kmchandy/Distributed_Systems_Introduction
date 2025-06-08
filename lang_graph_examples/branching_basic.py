"""
This module is an example of a LangGraph with a branching
node that routes the flow based on content.

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

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)

# ---------------------------------------------
# Step 2: Define the shared state structure
# This structure is often a TypedDict.
# ----------------------------------------------


class MyState(TypedDict):
    question: str
    answer: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph
# ----------------------------------------------


def tech_agent(state: MyState) -> dict:
    response = llm.invoke(f"Answer as tech support: {state['question']}")
    return {"answer": response.content}

# General help desk agent


def general_agent(state: MyState) -> dict:
    response = llm.invoke(f"Answer as general help desk: {state['question']}")
    return {"answer": response.content}

# Router function for branching


def router(state: MyState) -> str:
    if 'tech' in state['question'].lower():
        return {"next_node": "tech_node"}
    else:
        return {"next_node": "general_node"}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------
builder = StateGraph(MyState)

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

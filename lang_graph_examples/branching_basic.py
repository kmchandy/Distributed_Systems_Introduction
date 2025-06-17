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


class State(TypedDict):
    question: str
    answer: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.
# Here we specify three agents:
# tech_agent, help_desk_agent, and router_agent.
# ----------------------------------------------
# tech agent


def tech_agent(state: State) -> dict:
    response = llm.invoke(f"Answer as tech support: {state['question']}")
    return {"answer": response.content}

# help_desk help desk agent


def help_desk_agent(state: State) -> dict:
    response = llm.invoke(
        f"Answer as help_desk help desk: {state['question']}")
    return {"answer": response.content}

# Router agent for branching


def router_agent(state: State) -> str:
    if 'tech' in state['question'].lower():
        return {"next": "IT_help"}
    else:
        return {"next": "help_desk"}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(State)

# 4.2 Add nodes to the graph.
# Give a name to the node and specify the function
# that will be executed by the node.
# Here we create three nodes:
# router_node, tech_node, and help_desk_node.
builder.add_node("router_node", router_agent)
builder.add_node("tech_node", tech_agent)
builder.add_node("help_desk_node", help_desk_agent)

# 4.3 Add edges to the graph.
# In this example, all the edges are conditional edges.
# The code for conditional branching
builder.add_conditional_edges(
    # router_node is the name of node from which branching occurs
    "router_node",
    # route_agent returns dicts {'next': 'node_name'}
    # So the lambda function argument is 'next'.
    lambda x: x["next"],
    # The lambda function returns either "IT_help" or "help_desk".
    # The following dict specifies the next node to be executed
    # depending on the value returned by the lambda function.
    {
        "IT_help": "tech_node",
        "help_desk": "help_desk_node"
    }
)

# 4.4 Set the entry and finish points for the graph
builder.set_entry_point("router_node")
builder.set_finish_point("tech_node")
builder.set_finish_point("help_desk_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------
graph_prompts = [
    {"question": "I need help with tech specs for my laptop."},
    {"question": "What are your office hours?"}
]

for i, graph_prompt in enumerate(graph_prompts):
    print(f"\n❓ Input {i+1}: {graph_prompt['question']}")
    result = graph.invoke(graph_prompt)
    print("💬 Response:", result['answer'])

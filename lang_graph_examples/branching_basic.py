"""
This module is an example of a LangGraph with a branching
node that routes the flow of execution through the graph
based on the state.

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
#
# ----------------------------------------------


class State(TypedDict):
    question: str
    answer: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.
# Each function returns a dict with keys that are
# also keys of State.
# Here we specify three functions:
# tech_function, help_desk_function, and router_function.
#
# ----------------------------------------------

# tech function


def tech_function(state: State) -> dict:
    prompt = f"You are a tech support expert. Answer the question: {state['question']}"
    response = llm.invoke(prompt)
    # state["answer"] becomes response.content.
    return {"answer": response.content}

# help_desk help desk function


def help_desk_function(state: State) -> dict:
    prompt = f"You are a help desk assistant. Answer the question: {state['question']}"
    response = llm.invoke(prompt)
    # state["answer"] becomes response.content.
    return {"answer": response.content}

# Router function for branching


def router_function(state: State) -> dict:
    '''
    This function is used in builder.add_conditional_edges()
    which routes flow to tech_node if this function returns
    {"next": "ask_IT"} and to help_desk_node if this function
    returns {"next": "ask_help_desk"}.

    '''
    if 'tech' in state['question'].lower():
        return {"next": "ask_IT"}
    else:
        return {"next": "ask_help_desk"}


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
builder.add_node("router_node", router_function)
builder.add_node("tech_node", tech_function)
builder.add_node("help_desk_node", help_desk_function)

# 4.3 Add edges to the graph.
# In this example, all the edges are conditional edges.
# The code for conditional branching
builder.add_conditional_edges(
    # router_node is the name of node from which branching occurs
    "router_node",
    # route_function returns dicts {'next': 'node_name'}
    # So the lambda function argument is 'next'.
    lambda x: x["next"],
    # The lambda function returns either "ask_IT" or "ask_help_desk".
    # The following dict specifies the next node to be executed
    # depending on the value returned by the lambda function.
    {
        "ask_IT": "tech_node",
        "ask_help_desk": "help_desk_node"
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

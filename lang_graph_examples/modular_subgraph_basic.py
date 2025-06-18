"""
This module is an example of a LangGraph in which the main graph
calls another graph -- a subgraph

"""

import os
from typing import TypedDict, List
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

# ----------------------------------------------
# SPECIFY THE SUBGRAPH.
# ----------------------------------------------


# ----------------------------------------------
# Step 2: Define the shared state structure.
# We begin by specifying the subgraph which can be
# called by the main graph.

# ----------------------------------------------


class SubGraphState(TypedDict):
    user_id: str
    auth_token: str
    is_authenticated: bool

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.
# Here we specify the subgraph called
# by the main graph.

# ----------------------------------------------


def check_token(state: SubGraphState):
    if state["auth_token"] == "valid_token_123":
        return {"is_authenticated": True}
    else:
        return {"is_authenticated": False}


def deny_access(state: SubGraphState):
    print(
        f"Access Denied. Invalid authentication token: {state['auth_token']}")
    return state


def allow_access(state: SubGraphState):
    print(f"Access Granted for user: {state['user_id']}")
    return state


# ---------------------------------------------
# Step 4: Build the graph
# This is the subgraph that checks authentication.

# ----------------------------------------------
# 4.1 Create builder for the subgraph
sub_graph_builder = StateGraph(SubGraphState)

# 4.2 Add nodes to the graph.
# These are the nodes in the subgraph.
sub_graph_builder.add_node("check_token_node", check_token)
sub_graph_builder.add_node("allow_access_node", allow_access)
sub_graph_builder.add_node("deny_access_node", deny_access)

# 4.3 Specify the edges between nodes of the graph.
sub_graph_builder.add_conditional_edges(
    "check_token_node",
    lambda state: "allow_access" if state["is_authenticated"] else "deny_access",
    {
        "allow_access": "allow_access_node",
        "deny_access": "deny_access_node"
    }
)

# 4.4 Set the entry and finish points for the graph
sub_graph_builder.set_entry_point("check_token_node")
sub_graph_builder.set_finish_point("allow_access_node")
sub_graph_builder.set_finish_point("deny_access_node")

# 4.5 Compile the graph
# This compiles the subgraph so it can be called by the main graph.
sub_graph = sub_graph_builder.compile()
# ---------------------------------------------
# Step 5: Run graph

# We will run the main graph which will call this subgraph.
# ----------------------------------------------

# ---------------------------------------------
# SPECIFY THE MAIN GRAPH WHICH CALLS THE SUBGRAPH.
# ----------------------------------------------

# ---------------------------------------------
# Step 1 has already been executed.
# Step 2: Define the shared state structure.

# ----------------------------------------------


class MainGraphState(SubGraphState):
    pass

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.

# In this example the main graph does nothing other
# than call the subgraph.
# The main graph has no nodes.
# ----------------------------------------------

# ---------------------------------------------
# Step 4: Build the main graph

# ----------------------------------------------


# 4.1 Create builder
main_builder = StateGraph(MainGraphState)

# 4.2 Add nodes to the graph.
# Give a name to the node and specify the function
# that will be executed by the node.
# In this example the main graph has a single node.
main_builder.add_node("authenticate_node", sub_graph)

# 4.3 Add edges to the graph.
# In this case, the graph has a single node and so there
# are no edges.

# 4.4 Set the entry and finish points for the graph
main_builder.set_entry_point("authenticate_node")
main_builder.set_finish_point("authenticate_node")

# 4.5 Compile the graph
main_graph = main_builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------
print("---- Results of valid and invalid token tests ---- \n")
print("---- Valid Token Test ----")
graph_prompt = {
    "user_id": "alice",
    "auth_token": "valid_token_123",
    "is_authenticated": False
}
main_graph.invoke(graph_prompt)

print("\n---- Invalid Token Test ----")
graph_prompt = {
    "user_id": "bob",
    "auth_token": "invalid_token_999",
    "is_authenticated": False
}
main_graph.invoke(graph_prompt)

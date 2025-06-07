"""
This module is a simple example of how to use LangGraph with OpenAI's GPT-3.5-turbo model.
The graph in this module has only two nodes and one edge.
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

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# ---------------------------------------------
# Step 2: Define the shared state structure
# This structure is often a TypedDict.
# ----------------------------------------------


class GreetState(TypedDict):
    name: str
    greeting: str
    compliment: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph
# ----------------------------------------------


def greet_agent(state: GreetState) -> dict:
    name = state["name"]
    response = llm.invoke(
        f"Say two kind short sentences about the name {name}.\n")
    return {"greeting": response.content}


def compliment_agent(state: GreetState) -> dict:
    greeting = state["greeting"]
    response = llm.invoke(f"{greeting} Say one motivational sentence.")
    return {"compliment": response.content}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------
builder = StateGraph(GreetState)
# Add nodes to the graph
builder.add_node("greet_node", greet_agent)
builder.add_node("compliment_node", compliment_agent)
# Add edges to the graph
builder.add_edge("greet_node", "compliment_node")
# Set the entry and finish points for the graph
builder.set_entry_point("greet_node")
builder.set_finish_point("compliment_node")

graph = builder.compile()

# ---------------------------------------------
# Step 5: EXECUTE SCRIPT DIRECTLY
# ----------------------------------------------
if __name__ == "__main__":
    '''Example Usage
    python3 LangGraph_Simple_Two_nodes_Example.py "Violet"
    '''
    if len(sys.argv) < 2:
        print("Usage: python3 LangGraph_Simple_Two_nodes_Example.py [name]")
        sys.exit(1)
    # Get input_name from command line arguments
    input_name = sys.argv[1]

    # Run graph with the input and print result.
    result = graph.invoke({"name": input_name})
    print(result)

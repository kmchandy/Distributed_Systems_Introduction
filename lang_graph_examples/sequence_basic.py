"""
This module is an example of a LangGraph with two nodes in sequence.
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


class MyState(TypedDict):
    name: str
    greeting: str
    compliment: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph
# ----------------------------------------------


def greet_agent(state: MyState) -> dict:
    name = state["name"]
    response = llm.invoke(
        f"Say a single kind short sentence about the name {name}.\n")
    # Put the content of the response into the state of the agent.
    # state["greeting"] becomes response.content.
    # The response is not printed.
    return {"greeting": response.content}


def compliment_agent(state: MyState) -> dict:
    greeting = state["greeting"]
    response = llm.invoke(
        f"Say one motivational sentence based on {greeting}.")
    # Put the content of the response into the state of the agent.
    # state["compliment"] becomes response.content
    return {"compliment": response.content}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(MyState)

# 4.2 Add nodes to the graph.
# Give a name to the node and specify the function
# that will be executed by the node.
# Here we create two nodes called "greet_node" and "compliment_node".
builder.add_node("greet_node", greet_agent)
builder.add_node("compliment_node", compliment_agent)

# 4.3 Define the edges between nodes of the graph.
# In this case, the graph has a single edge.
# The edge is from "greet_node" to "compliment_node".
builder.add_edge("greet_node", "compliment_node")

# 4.4 Specify the entry and finish points of the graph.
builder.set_entry_point("greet_node")
builder.set_finish_point("compliment_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: EXECUTE SCRIPT DIRECTLY
# ----------------------------------------------

'''
Execution of the graph is as follows.
The graph is invoked with an input that is a dictionary.
The keys of the input dict must match the keys in MyState.

The entry point node, greet_node, is executed with a state
specified by the dict, {"name": input_name}, in the invoke.
So, when greet_node is executed state["name"] is set to input_name,
and state["greeting"] and state["compliment"] are unspecified.

greet_node puts the result of the LLM invocation into state["greeting"].
Then execution of compliment_node begins with a state with values for
the keys "name" and "greeting", and state["compliment"] is unspecified.
compliment_node puts the result of the LLM invocation into state["compliment"].
Finally, the graph returns a state with values for all three keys.
'''
if __name__ == "__main__":
    '''Example Usage
    python3 LangGraph_Simple_Two_nodes_Example.py "Violet"
    '''
    if len(sys.argv) < 2:
        print("Usage: python3 LangGraph_Simple_Two_nodes_Example.py [name]")
        sys.exit(1)
    # Get input_name from command line arguments
    input_name = sys.argv[1]

    # Execute the graph. The input to the graph is a dict and pretty print
    # the result of the graph execution.
    result = graph.invoke({"name": input_name})
    import pprint
    pprint.pprint(result)

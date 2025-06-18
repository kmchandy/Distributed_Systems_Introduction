"""
This module is an example of a LangGraph with two nodes in parallel and
where both needs feed into a single merge node.

"""

import pprint
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
# The state is a TypedDict.
# ----------------------------------------------


class State(TypedDict):
    name: str
    topic: str
    greeting: str
    fact: str
    summary: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.
# The functions return a dict where the keys are
# also keys of State.
# ----------------------------------------------


def greet_function(state: State) -> dict:
    '''
    Reads state['name'] and assigns value to state['greeting'].

    '''
    prompt = f"Say a short sentence about {state['name']}."
    response = llm.invoke(prompt)
    # state["greeting"] becomes response.content.
    return {"greeting": response.content}


def topic_function(state: State) -> dict:
    '''
    Reads state['topic'] and assigns value to state['fact'].

    '''
    prompt = f"Tell me a short fact about {state['topic']}."
    response = llm.invoke(prompt)
    # state["fact"] becomes response.content.
    return {"fact": response.content}


def merge_function(state: State) -> dict:
    '''
    Reads state['greeting'] and state['fact'] and 
    assigns value to state['summary'].

    '''
    prompt = f"Make a joke about {state['greeting']} and {state['fact']}"
    response = llm.invoke(prompt)
    # state["summary"] becomes response.content.
    return {"summary": response.content}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(State)

# 4.2 Specify nodes of the graph
# Give a name to each node and specify the function
# that will be executed by the node.
# In this case, in addition to greet_node, topic_node, and
# merge_node, we create an entry node that feeds both
# greet_node and topic_node. The entry node is a no-op.
builder.add_node("entry_node", lambda x: x)
builder.add_node("greet_node", greet_function)
builder.add_node("topic_node", topic_function)
builder.add_node("merge_node", merge_function)

# 4.3 Specify the edges between nodes of the graph.
builder.add_edge("entry_node", "greet_node")
builder.add_edge("entry_node", "topic_node")
builder.add_edge("greet_node", "merge_node")
builder.add_edge("topic_node", "merge_node")

# 4.4 Set the entry and finish nodes of the graph
builder.set_entry_point("entry_node")
builder.set_finish_point("merge_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------

# graph_prompt, is a dict that specifies some fields of state.
graph_prompt = {
    "name": "Prof. K. Mani Chandy",
    "topic": "distributed systems"
}
# Execute the graph.
result = graph.invoke(graph_prompt)
# result is the final value of state.
print(f"Printing the state after graph execution completes. \n")
print("🎉 Result:\n")
pprint.pprint(result)

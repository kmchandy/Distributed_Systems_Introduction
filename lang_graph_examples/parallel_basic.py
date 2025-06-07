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
# This structure is often a TypedDict.
# ----------------------------------------------


class MyState(TypedDict):
    name: str
    topic: str
    greeting: str
    fact: str
    summary: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph
# ----------------------------------------------


def greet_agent(state: MyState) -> dict:
    '''
    Reads state['name'] and assigns value to state['greeting'].
    '''
    response = llm.invoke(f"Say a short sentence about {state['name']}.")
    return {"greeting": response.content}


def topic_agent(state: MyState) -> dict:
    '''
    Reads state['topic'] and assigns value to state['fact'].
    '''
    response = llm.invoke(f"Tell me a short fact about {state['topic']}.")
    return {"fact": response.content}


def merge_agent(state: MyState) -> dict:
    '''
    Reads state['greeting'] and state['fact'] and 
    assigns value to state['summary'].
    '''
    response = llm.invoke(
        f"Make a joke about {state['greeting']} and {state['fact']}")
    return {"summary": response.content}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(MyState)

# 4.2 Specify nodes of the graph
# Give a name to each node and specify the function
# that will be executed by the node.
# In this case, in addition to greet_node, topic_node, and
# merge_node, we create an entry node that feeds both
# greet_node and topic_node. The entry node is a no-op.
builder.add_node("entry_node", lambda x: x)
builder.add_node("greet_node", greet_agent)
builder.add_node("topic_node", topic_agent)
builder.add_node("merge_node", merge_agent)

# 4.3 Specify the edges between nodes of the graph.
builder.add_edge("entry_node", "greet_node")
builder.add_edge("entry_node", "topic_node")
builder.add_edge("greet_node", "merge_node")
builder.add_edge("topic_node", "merge_node")

# Set the entry and finish points for the graph
builder.set_entry_point("entry_node")
builder.set_finish_point("merge_node")

graph = builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------
result = graph.invoke({"name": "Prof. K. Mani Chandy",
                      "topic": "distributed systems"})
print("🎉 Final Output -- MyState when graph execution terminates:\n")
pprint.pprint(result)

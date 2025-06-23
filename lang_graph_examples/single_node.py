"""
This module is an example of a LangGraph with a single node.

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

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

# ---------------------------------------------
# Step 2: Define the state: a TypedDict.
# ----------------------------------------------


class State(TypedDict):
    question: str
    answer: str

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.
# The functions return a dict where the keys are
# also keys of State.
# In this case, the function returns a dict
# with a single key "answer" which is a key of State.
# ----------------------------------------------


def answer_function(state: State) -> dict:
    # The function reads state["question"] and writes
    # state["answer"].
    prompt = f"Answer the question: {state['question']}"
    response = llm.invoke(prompt)
    # Put the content of the response into the state of the function.
    # state["snswer"] becomes response.content.
    return {"answer": response.content}


# ---------------------------------------------
# Step 4: Build the graph.
# The nodes of the graph are agents that execute
# functions that read and write the state.
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(State)

# 4.2 Add nodes to the graph.
# Give a name to the node and specify the function
# that will be executed by the node.
builder.add_node("answer_node", answer_function)

# 4.3 Define the edges between nodes of the graph.
# In this case, the graph has a single node and
# no edges.

# 4.4 Specify the entry and finish points of the graph.
builder.set_entry_point("answer_node")
builder.set_finish_point("answer_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: Run the graph with a prompt.
#
# The prompt is a dict where the keys of the dict
# are fields of the state. Here the prompt has a
# single key "question" which is a field of State.
#
# In this case the entry point -- i.e. answer_node --
# is invoked with an instance of State where
# State["question"]is set to
# "What is the capital of France?",
# and where State["answer"] is empty.
#
# The result is the state after the nodes in the
# graph have been executed.

# ----------------------------------------------
graph_prompt = {
    "question": "What is the capital of France?"
}
result = graph.invoke(graph_prompt)
print(f"Printing the state after graph execution completes. \n")
print("🎉 Result:\n")
pprint.pprint(result)

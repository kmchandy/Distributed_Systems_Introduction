"""
This module is an example of a LangGraph with two nodes in sequence.
The module is called from the command line by passing a name as an 
argument.
Example Usage
python3 sequence_basic.py "Rose"

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
# Step 2: Define the state: a TypedDict.
# ----------------------------------------------


class State(TypedDict):
    name: str
    greeting: str
    compliment: str

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
    name = state["name"]
    prompt = f"Say a single kind short sentence about the name {name}.\n"
    response = llm.invoke(prompt)
    # Put the content of the response into the state of the function.
    # state["greeting"] becomes response.content.
    return {"greeting": response.content}


def compliment_function(state: State) -> dict:
    '''
    Reads state['greeting'] and assigns value to state['compliment'].

    '''
    greeting = state["greeting"]
    prompt = f"Say one motivational sentence based on {greeting}."
    response = llm.invoke(prompt)
    # Put the content of the response into the state of the function.
    # state["compliment"] becomes response.content
    return {"compliment": response.content}


# ---------------------------------------------
# Step 4: Build the graph
# The nodes of the graph are agents that execute
# functions that read and write the state.
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(State)

# 4.2 Add nodes to the graph.
# Give a name to the node and specify the function
# that will be executed by the node.
# Here we create two nodes called "greet_node" and "compliment_node".
builder.add_node("greet_node", greet_function)
builder.add_node("compliment_node", compliment_function)

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
The keys of the input dict must match the keys in State.

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
    python3 sequence_basic.py "Rose"

    '''
    if len(sys.argv) < 2:
        print("Usage: python3 sequence_basic.py [name]")
        sys.exit(1)
    # Get input_name from command line arguments
    input_name = sys.argv[1]

    # graph_prompt, is a dict that specifies some fields of state.
    graph_prompt = {"name": input_name}
    # Execute the graph.
    result = graph.invoke(graph_prompt)

    # result is the final value of state.
    # pretty print the result
    print(f"Printing the state after graph execution completes. \n")
    print(f"The state is a dict with three keys: name, greeting, compliment \n")
    import pprint
    pprint.pprint(result)

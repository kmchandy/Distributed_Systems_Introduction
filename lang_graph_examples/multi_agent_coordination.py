"""
LangGraph Example: Multi-Agent Coordination (see sequential_basic.py)

This script demonstrates a distributed coordination pattern using LangGraph,
where different agents perform planning, execution, and validation.

Example Usage:
python3 multi_agent_coordination_basic.py "Make coffee."

The user input is an instruction to achieve a goal such as brew a cup of coffee.
The planner_node determines a plan as specified in the instruction.
The executor_node executes the plan, which in this case is simulated by returning a string 
indicating that execution has completed.
The validator_node checks if the execution was correct.

This pattern is used to coordinate multiple agents. 
The graph structure is the same as in sequential_basic.py



"""

import os
import sys
from typing import TypedDict, Literal
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END


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
# # ----------------------------------------------


class State(TypedDict):
    goal: str
    plan: str
    result: str
    is_valid: bool


# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.
# The functions return a dict where the keys are
# also keys of State.
# ----------------------------------------------

def planner_function(state: State) -> dict:
    prompt = f"Develop a short plan to achieve this goal: {state['goal']}"
    response = llm.invoke(prompt)
    plan_determined_by_LLM = response.content
    print("Planner generated the following plan: \n")
    print(plan_determined_by_LLM)
    # state["plan"] becomes plan_determined_by_LLM
    return {"plan": plan_determined_by_LLM}


def executor_function(state: State) -> dict:
    '''
    Reads state['plan'] and assigns value to state['result'].

    '''
    execution = f"Executing: {state['plan']}"
    print("Executor ran the plan.")
    # Simulate execution by returning the result
    # state["result"] becomes execution
    return {"result": execution}


def validator_function(state: State) -> dict:
    '''
    Reads state['result'] and assigns value to state['is_valid'].

    '''
    prompt = f"Does this execution look correct? {state['result']}. Respond yes or no."
    response = llm.invoke(prompt)
    valid = "yes" in response.content.lower()
    print("Validator checked the result:", "Valid" if valid else "Invalid")
    return {"is_valid": valid}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(State)

# 4.2 Specify nodes of the graph
# Give a name to each node and specify the function
# that will be executed by the node.

builder.add_node("planner_node", planner_function)
builder.add_node("executor_node", executor_function)
builder.add_node("validator_node", validator_function)

# 4.3 Specify the edges between nodes of the graph.
builder.add_edge("planner_node", "executor_node")
builder.add_edge("executor_node", "validator_node")
builder.add_edge("validator_node", END)

# 4.4 Set the entry and finish nodes of the graph
builder.set_entry_point("planner_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------

# graph_prompt, is a dict that specifies some of the fields of state.
if __name__ == "__main__":
    '''
    Example Usage
    python3 multi_agent_coordination_basic.py "Make coffee."

    Example Usage
    python3 multi_agent_coordination_basic.py "Clean kitchen."

    '''
    if len(sys.argv) < 2:
        print("Usage: python3 multi_agent_coordination_basic.py [goal]")
        sys.exit(1)
    # Get the goal from command line arguments
    goal = sys.argv[1]

    # graph_prompt, is a dict that specifies some fields of state.
    graph_prompt = {"goal": goal}
    # Execute the graph.
    result = graph.invoke(graph_prompt)

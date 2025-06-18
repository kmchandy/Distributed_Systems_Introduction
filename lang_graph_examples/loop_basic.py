"""
This module is an example of a LangGraph with two nodes in a loop.
In this example the graph is prompted with a text and the graph
returns with a text that is a positive spin on the original text.

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
# The state is a TypedDict.
# ----------------------------------------------


class State(TypedDict):
    text: str
    sentiment_score: float

# ---------------------------------------------
# Step 3: Specify the functions that are executed
# by nodes in the graph.
# The functions return a dict where the keys are
# also keys of State.
# In this example we define three functions:
# summarizer_function, evaluator_function, and router_function.
# ----------------------------------------------


# summarizer_function rewrites the text in a positive tone.
def summarizer_function(state: State) -> dict:
    prompt = f"Write {state['text']} in as positive a tone as possible."
    result = llm.invoke(prompt)
    print(f"result: {result.content} \n")
    # state["text"] becomes result.content.
    return {"text": result.content}


# evaluator_function estimates the sentiment of a text (using naive approach)
def evaluator_function(state: State) -> dict:
    prompt = f"""On a scale from 0 (very negative) to 1 (very positive), 
    how positive is {state['text']}? Only return a number.\n\n"""
    response = llm.invoke(prompt)

    score = response.content
    try:
        value = float(score.strip())
    except ValueError:
        value = 0.0
    # Print the sentiment score to see how it increases with each iteration.
    print(f"sentiment score: {value} \n")
    # state["sentiment_score"] becomes value.
    return {"sentiment_score": value}


# router_function routes control to end_node or summarizer_node
# based on sentiment score.
def router_function(state: State) -> dict:
    if state["sentiment_score"] >= 0.85:
        return {"next": "terminate_iterations"}
    else:
        return {"next": "iterate_again"}


# ---------------------------------------------
# Step 4: Build the graph
# ----------------------------------------------

# 4.1 Create builder
builder = StateGraph(State)

# # 4.2 Add nodes to the graph.
# Create an "end_node" to finish the graph. The end_node does nothing.
builder.add_node("end_node", lambda x: x)
# Give a name to each node and specify the function
# that will be executed by the node.
builder.add_node("summarizer_node", summarizer_function)
builder.add_node("evaluator_node", evaluator_function)
builder.add_node("router_node", router_function)

# 4.3 Specify the edges between nodes of the graph.
builder.add_edge("summarizer_node", "evaluator_node")
builder.add_edge("evaluator_node", "router_node")
# Add edges from router_node to end_node and summarizer_node
# Execute "end_node" when router_function returns "terminate_iterations"
# Execute "summarizer_node" when router_function returns "iterate_again"
builder.add_conditional_edges(
    "router_node",
    lambda x: x["next"],  # routing function
    {
        "terminate_iterations": "end_node",
        "iterate_again": "summarizer_node"
    }
)

# 4.4 Set the entry and finish points for the graph
builder.set_entry_point("summarizer_node")
builder.set_finish_point("end_node")

# 4.5 Compile the graph
graph = builder.compile()

# ---------------------------------------------
# Step 5: Run graph
# ----------------------------------------------

# graph_prompt, is a dict that specifies some fields of state.
graph_prompt = {
    "text": "The economy is in shambles. Inflation is high and unemployment is rising",
    "sentiment_score": 0.0,
}
print("📜 Text with different positive sentiments. Stops when sentiment is high enough. \n")
# Execute the graph.
result = graph.invoke(graph_prompt)
# result is the final value of state.
print("✅ Final text:")
print(result['text'])
print("📈 Sentiment Score:", result['sentiment_score'])

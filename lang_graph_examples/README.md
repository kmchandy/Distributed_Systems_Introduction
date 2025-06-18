# 🧠 LangGraph Example Progression

This folder contains a structured series of LangGraph examples. Each example introduces one concept.

---

## ✅ Sequence of Examples

### 0. Single Node
- **Concept**: Simplest graph consisting of a single node.
- **Example**: Answer a query
- **File**: `single_node.py`

---

### 1. Sequential Nodes
- **Concept**: One node runs after another, passing and modifying shared state.
- **Example**: Greet someone and then offer a compliment.
- **File**: `sequence_basic.py`

---

### 2. Parallel Execution
- **Concept**: Run multiple nodes in parallel and merge their outputs.
- **Example**: Greet a person and get a fun fact in parallel, then combine.
- **File**: `parallel_basic.py`

---

### 3. Conditional Branching
- **Concept**: Route execution to different nodes based on input.
- **Example**: If input contains 'tech', route to tech support; otherwise to general.
- **File**: `branching_basic.py`

---

### 4. Looping / Iteration
- **Concept**: Repeat a step until a condition is met (e.g., quality or approval).
- **Example**: Refine a summary until it meets quality criteria.
- **File**: 'loop_basic.py'

---

### 5. Map-Reduce Pattern
- **Concept**: Distribute computation over multiple nodes and aggregate results.
- **Example**: Analyze documents in parallel, summarize all.
- **File**: 'map_reduce_basic.py'

---

### 6. Modular Subgraphs
- **Concept**: Encapsulate reusable logic in subgraphs.
- **Example**: Authentication subgraph reused across workflows.
- **File**: 'modular_subgraph_basic.py'

---

### 7. Multi-Agent Coordination
- **Concept**: Use different agents for planning, execution, and validation.
- **Example**: Planner suggests a plan, executors carry it out.
- **File**: _(coming soon)_

---

### 8. Human-in-the-Loop
- **Concept**: Pause and allow user approval before continuing.
- **Example**: Wait for review before publishing a generated answer.
- **File**: _(coming soon)_

---

### 9. State Persistence
- **Concept**: Save and restore graph state.
- **Example**: Rewind execution to a previous state if there's an error.
- **File**: _(coming soon)_

---

### 10. External Tools & API Calls
- **Concept**: Extend LangGraph with external services and tool use.
- **Example**: Use an API to fetch data and incorporate it in the graph.
- **File**: _(coming soon)_

---

## 📁 How to Use

Open any of the `.ipynb` notebooks in [Google Colab](https://colab.research.google.com/) or your preferred Jupyter environment. These examples are designed for progressive learning.


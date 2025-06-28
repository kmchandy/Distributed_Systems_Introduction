# Message Passing Examples

This folder contains introductory examples for building distributed systems using Python's built-in `multiprocessing` and `SimpleQueue`.

Each example defines one or more agents that run as independent processes and communicate using message-passing queues. Some agents may also use the OpenAI API to simulate intelligent behavior (e.g., rewriting or summarizing messages).

## How to Run the Examples

From the **top-level** `Distributed_Systems_Introduction/` directory, run examples using the Python interpreter and a relative path:

```bash
python message_passing_examples/example_1_basic.py
```

This approach:
- Ensures that shared utilities like `get_credentials.py` can be imported correctly
- Makes it clear to students **where the code lives** and **how it’s structured**
- Works across platforms (macOS, Windows, Linux)

## Requirements

Some examples require the following Python packages:

- `openai`
- `python-dotenv`

Install them using:

```bash
pip install -r requirements.txt
```

Also, create a `.env` file in the top-level directory to store your OpenAI key:

```
OPENAI_API_KEY=your-api-key-here
```

## Example Index

| File Name                         | Description                                     |
|----------------------------------|-------------------------------------------------|
| `example_1_basic.py`             | Basic sender → receiver message passing        |
| `example_2_gpt_receiver.py`      | Sender sends a message to a GPT-based agent    |
| `example_3_chain.py` *(upcoming)*| Linear chain: A → B → C                         |
| `example_4_dispatcher.py` *(upcoming)*| Routed message handling using types       |

---

Happy coding!
from multiprocessing import Process, SimpleQueue
import time
import os
from openai import OpenAI
from dotenv import load_dotenv

# ---------------------------------------------
# Step 1: Set up OpenAI.
# ----------------------------------------------

# Load API key from .env file
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

# Ensure the API key is available
if not api_key:
    raise ValueError("No API key found. Please check your .env file.")
# Set your OpenAI API key
# or hard-code for testing (not recommended)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class Agent:
    def __init__(self, init_fn=None, handle_msg=None, name="Agent"):
        # The input queue from which this agent receives messages.
        self.queue = SimpleQueue()
        # The function executed before the agent starts processing messages.
        # If this function is not given then the agent starts processing
        # messages when the agent starts.
        self.init_fn = init_fn
        # The function that handles messages received by the agent.
        # If this function is not given then the agent stops after
        # executing intit_fn.
        self.handle_msg = handle_msg
        self.name = name
        # A dictionary of peers that this agent to which this agent
        # can send messages
        self.peers = {}

    def run(self):
        # Run the initialization function if it exists
        if self.init_fn:
            self.init_fn(self)
        # If the message handler function is not given then stop the agent
        # without handling messages.
        if not self.handle_msg:
            return
        # Process messages in the queue until __STOP__ is received.
        while True:
            msg = self.queue.get()
            if msg == "__STOP__":
                break
            self.handle_msg(self, msg)

    def start(self):
        p = Process(target=self.run)
        p.start()
        return p

# OpenAI-powered message handler


def gpt_handle_msg(self, msg):
    print(f"{self.name} received: {msg}")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": msg}],
            temperature=0.3
        )
        reply = response.choices[0].message.content.strip()
        print(f"{self.name} (GPT reply): {reply}")
    except Exception as e:
        print(f"{self.name} encountered an error: {e}")

# Sender sends a message to GPT


def init_fn(self):
    prompt = "Rewrite this sentence to be more formal: 'What's up?'"
    self.peers["GPT"].queue.put(prompt)
    time.sleep(0.5)
    self.peers["GPT"].queue.put("__STOP__")


if __name__ == "__main__":
    gpt_agent = Agent(handle_msg=gpt_handle_msg, name="GPT")
    sender = Agent(init_fn=init_fn, name="Sender")
    sender.peers["GPT"] = gpt_agent

    sender_proc = sender.start()
    gpt_proc = gpt_agent.start()

    sender_proc.join()
    gpt_proc.join()

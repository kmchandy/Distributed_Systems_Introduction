'''
The class inherited by all agents in message_passing_examples.
An agent receives messages along a single input queue, self.queue.


'''
from multiprocessing import Process, SimpleQueue


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

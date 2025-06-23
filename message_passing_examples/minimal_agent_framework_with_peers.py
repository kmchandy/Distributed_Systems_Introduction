from multiprocessing import Process, SimpleQueue
import time


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


def init_fn(self):
    for i in range(3):
        self.peers["Receiver"].queue.put(f"Hi {i}")
        time.sleep(0.5)
    self.peers["Receiver"].queue.put("__STOP__")


def handle_msg(self, msg):
    print(f"{self.name} received: {msg}")


if __name__ == "__main__":
    # Create agents
    receiver = Agent(handle_msg=handle_msg, name="Receiver")
    sender = Agent(init_fn=init_fn, name="Sender")

    # Wire agents using peer dictionary
    sender.peers["Receiver"] = receiver

    # Start agents
    sender_proc = sender.start()
    receiver_proc = receiver.start()

    sender_proc.join()
    receiver_proc.join()

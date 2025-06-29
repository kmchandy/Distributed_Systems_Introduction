from core import Agent, Network
import time

# Define a sender agent as a subclass of Agent


class SenderAgent(Agent):
    def run(self):
        for i in range(3):
            print(f"{self.name} sending: Hi {i}")
            self.send(f"Hi {i}", "output")
            time.sleep(0.5)
        self.send("__STOP__", "output")

# Define a receiver agent as a subclass of Agent


class ReceiverAgent(Agent):
    def run(self):
        while True:
            msg = self.recv("input")
            if msg == "__STOP__":
                break
            print(f"{self.name} received: {msg}")


# Instantiate the agents
sender = SenderAgent(name="Sender", outports=["output"])
receiver = ReceiverAgent(name="Receiver", inports=["input"])

# Create the network
blocks = {"sender": sender, "receiver": receiver}
connections = [["sender", "output", "receiver", "input"]]
net = Network(name="net", blocks=blocks, connections=connections)

# Run the network
if __name__ == "__main__":
    net.run()

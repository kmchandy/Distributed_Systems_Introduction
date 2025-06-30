from core import Agent, Network


def sender_run(self):
    for i in range(3):
        print(f"{self.name} sending: Hi {i}")
        self.send(f"Hi {i}", "output")
    self.send("__STOP__", "output")


def receiver_run(self):
    while True:
        msg = self.recv("input")
        if msg == "__STOP__":
            break
        print(f"{self.name} received: {msg}")


# Instantiate the agents
sender = Agent(name="Sender", outports=["output"], run_fn=sender_run)
receiver = Agent(name='receiver', inports=["input"], run_fn=receiver_run)


# Create the network
blocks = {"sender": sender, "receiver": receiver}
connections = [["sender", "output", "receiver", "input"]]
net = Network(name="net", blocks=blocks, connections=connections)

# Run the network
if __name__ == "__main__":
    net.run()

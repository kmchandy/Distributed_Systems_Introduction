from core import Network, Agent
import time


def init_fn(self):
    for i in range(3):
        print(f'Sending Hi {i}')
        self.send(msg=f"Hi {i}", outport="output")
        time.sleep(0.5)
    self.send(msg="__STOP__", outport='output')


def handle_msg(self, msg):
    print(f"{self.name} received: {msg}")


agent_receiver = Agent(
    inport='input',
    handle_msg=handle_msg,
    name="Receiver"
)

agent_sender = Agent(
    outports=['output'],
    init_fn=init_fn,
    name="Sender"
)


if __name__ == "__main__":

    nodes = {'sender': agent_sender,
             'receiver': agent_receiver}
    edges = [
        ['sender', 'output', 'receiver', 'input']
    ]
    net = Network(name='net', nodes=nodes, edges=edges)
    net.run()

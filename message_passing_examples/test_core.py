
import unittest
from multiprocessing import SimpleQueue
from core import Block, Agent, Network, SimpleAgent


class TestNetwork(unittest.TestCase):

    def test_two_simple_agents(self):
        '''
        Tests a sender agent that sends "Hello" to a
        receiver agent. Similar to test_two__agents
        (below) and the difference is that here we use 
        the SimpleAgent class and not the Agent class.

        '''

        def init_fn(self):
            self.send(msg="hello", outport="out")
            self.send(msg="__STOP__", outport="out")

        received = []
        def handle_msg(self, msg): received.append(msg)

        # Instantiate the two simple_agents
        sender = SimpleAgent(name="Sender", outports=["out"], init_fn=init_fn,)
        receiver = SimpleAgent(
            name="Receiver", inport="in", handle_msg=handle_msg,)

        # Create the network. This network has no inports or outports
        # that are visible to other networks. The outport of sender and
        # the inport of receiver are local to these components and so
        # these ports do not appear in inports and outports of the network.
        net = Network(
            name="Net",
            inports=[],
            outports=[],
            blocks={"sender": sender, "receiver": receiver},
            connections=[
                ("sender", "out", "receiver", "in")
            ]
        )
        # Run the network
        net.run()
        self.assertEqual(received, ["hello"])

    def test_two_agents(self):
        '''
        Tests a sender agent that sends "Hello" to a
        receiver agent. Similar to test_two_simple_agents
        and the difference is use of Agent and not
        SimpleAgent class.

        '''

        def sender_run(self):
            self.send(msg="Hello", outport="output")
            self.send(msg="__STOP__", outport="output")

        received = []

        def receiver_run(self):
            while True:
                msg = self.recv(inport="input")
                if msg == "__STOP__":
                    break
                received.append(msg)

        # Instantiate the agents
        sender = Agent(name="sends_hello_agent", outports=[
                       "output"], run_fn=sender_run)
        receiver = Agent(name='receiver', inports=[
                         "input"], run_fn=receiver_run)

        # Create the network with two blocks, sender and receiver
        blocks = {"sender": sender, "receiver": receiver}
        connections = [["sender", "output", "receiver", "input"]]
        net = Network(name="net", blocks=blocks, connections=connections)

        # Run the network
        net.run()

        # Check run
        self.assertEqual(received, ["Hello"])

    def test_merge_agent(self):
        '''
        Tests an agent that receives messages from
        two inports.

        '''

        def sender_hello_run(self):
            '''
            A message is a dict that identifies the sender and
            the message contents.

            '''
            self.send(
                msg={'sender': 'sends_hello', 'message': 'hello'},
                outport="out",
            )
            self.send(
                msg={'sender': 'sends_hello', 'message': '__STOP__'},
                outport="out",
            )

        def sender_world_run(self):
            '''
            Sends message 'world' and then message '__STOP__'

            '''
            self.send(
                msg={'sender': 'sends_world', 'message': 'world'},
                outport="out",
            )
            self.send(
                msg={'sender': 'sends_world', 'message': '__STOP__'},
                outport="out",
            )

        received = []

        def receiver_run(self):
            # received_stop_from is the set of agents that
            # sent '__STOP__' messages to this agent.
            received_stop_from = set()
            while True:
                msg = self.recv(inport="input")
                msg_contents = msg['message']
                msg_sender = msg['sender']
                if msg_contents != "__STOP__":
                    received.append(msg_contents)
                elif msg_sender not in received_stop_from:
                    # Add msg_sender to the set of agents
                    # that have sent __STOP__ messages.
                    received_stop_from.add(msg_sender)
                    if len(received_stop_from) == 2:
                        break
                else:
                    # The same sender is sending multiple stops.
                    pass

        # Instantiate the agents.
        sender_hello_agent = Agent(
            name="sends_hello", outports=["out"], run_fn=sender_hello_run
        )
        sender_world_agent = Agent(
            name="sends_world", outports=["out"], run_fn=sender_world_run
        )
        receiver = Agent(name='receiver', inports=[
                         "input"], run_fn=receiver_run)

        # Create the network
        blocks = {
            "sender_world_agent": sender_world_agent,
            "sender_hello_agent": sender_hello_agent,
            "receiver": receiver}
        connections = [
            ["sender_world_agent", "out", "receiver", "input"],
            ["sender_hello_agent", "out", "receiver", "input"],
        ]
        net = Network(name="net", blocks=blocks, connections=connections)

        # Run the network
        net.run()

        # Check run
        self.assertEqual(set(received), {'hello', 'world'})

    def test_network_check_validation(self):
        sender = SimpleAgent(name="Sender", outports=["out"])
        receiver = SimpleAgent(name="Receiver", inport="in")

        net = Network(
            name="BadNet",
            inports=[],
            outports=[],
            blocks={"sender": sender, "receiver": receiver},
            connections=[
                ("sender", "bad_out", "receiver", "in")
            ]
        )
        with self.assertRaises(ValueError):
            net.check()


if __name__ == "__main__":
    unittest.main()

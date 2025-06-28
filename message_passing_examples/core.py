'''
network.py
This module defines the Network and Agent classes, and the connect_ports() function.
These form the foundation of a message-passing framework for building distributed
applications. In the following we refer to an instance of the Network class as 'network'
and an instance of the Agent class as 'agent'. A 'stream' is a sequence of messages.

Input and output ports of a network:
------------------------------------
A network has a dict of named input ports and named output ports.
A stream is fed to a network on each of the network's input ports. A network generates a stream
on each of the network's output ports. Input and output ports are called inports and outports,
respectively.

Components
----------
A network consists of one or more components. A component of a network is a network. 
Later we refer to a component as a node of a directed graph. The edges of the graph
show how streams flow between ports of components.

Connecting ports
----------------
Components of the network are connected in the following way:
1. A stream into to an input port of a network is the stream to an input
port of one component of the network.
    [input port 'p'of network ] ---> [input port 'w' of component 'X']
    
2. The stream from an output port of a network is the stream from an output 
port of one component of the network.
    [output port 'w' of component 'X'] --->  [output port 'p'of network ] 
    
3. An input port of a component of the network can be fed by streams from
multiple output ports of components of the network and by streams fed to multiple
input ports of the network. Multiple streams can merge to form the input stream
into an input port of a component.
                                            ___________________________________
    [input port 'p'of network ]        ---> |                                 |
    [input port 'q'of network ]        ---> | input port 'r' of component 'Z' |
    [output port 'w' of component 'X'] ---> |                                 |
    [output port 'v' of component 'Y'] ---> |_________________________________|
                                            
4. The stream from an output port of a component is connected exactly once.
A stream from an output port of a component is either (1) the stream of exactly
one output port of the network or (2) the stream of one input port of a component.
Case 1: [output port 'w' of component 'X'] ---> [output port 'v' of network]
Case 2: [output port 'w' of component 'X'] ---> [input port 'v' of component 'Y']

Network parameters
------------------
1. name of a network is arbitrary. It is helpful in debugging.
2. nodes is a dict:  node_name   --->  node
where node is a component of the network, and so node is an instance of Network.
3. edges is a list of 4-tuples where all elements of each list are strings.
An edge is one of the following 3:
    (a) [from_node_name, from_port, to_node_name, to_port] 
    This edge specifies that the stream from the port called from_port of the node with
    name from_node_name flows to the port called to_port of the node with name to_node.
    (b) ['external', from_network_port, to_node_name, to_port]
    This edge specifies that the stream that flows into the port called from_network_port
    of the network flows into the port called to_port of the node called to_node_name.
    (c) [from_node_name, from_port, 'external', to_network_port]
    This edge specifies that the stream from the port called from_port of the node called
    from_node_name flows out through the node called to_network_port of the network.
4. inports is a list of names of input ports of the network.
5. outport is the list of names of output ports of the network
6. init_fn is the function that is executed after the components of the network have been
    initiated and before the components are run.

'''

from __future__ import annotations
from multiprocessing import SimpleQueue
from typing import Callable, Optional, List, Tuple, Dict
from multiprocessing import SimpleQueue
from typing import Optional, List, Callable, Dict, Tuple, Any


class Block:
    """
    Base class for all composable units in the framework.
    A Block has named input and output ports and associated queues.
    """

    def __init__(
        self,
        name: str,
        inports: Optional[List[str]] = None,
        outports: Optional[List[str]] = None
    ):
        self.name = name
        self.inports = inports or []
        self.outports = outports or []

        # Dict: port name -> SimpleQueue
        self.in_q: Dict[str, SimpleQueue] = {
            port: SimpleQueue() for port in self.inports
        }
        self.out_q: Dict[str, Optional[SimpleQueue]] = {
            port: None for port in self.outports
        }

    def send(self, port: str, msg: Any):
        """Send a message to an output port."""
        if port not in self.out_q:
            raise ValueError(f"[{self.name}] Invalid output port: {port}")
        if self.out_q[port] is None:
            raise ValueError(
                f"[{self.name}] Output port '{port}' is not connected.")
        self.out_q[port].put(msg)

    def recv(self, port: str) -> Any:
        """Receive a message from an input port."""
        if port not in self.in_q:
            raise ValueError(f"[{self.name}] Invalid input port: {port}")
        return self.in_q[port].get()

    def connect_out(self, port: str, queue: SimpleQueue):
        """Connect an output port to a queue."""
        if port not in self.out_q:
            raise ValueError(f"[{self.name}] No such output port: {port}")
        self.out_q[port] = queue

    def connect_in(self, port: str, queue: SimpleQueue):
        """Connect an input port to a queue (replaces existing one)."""
        if port not in self.in_q:
            self.in_q[port] = queue  # allow dynamic inport expansion
            self.inports.append(port)
        else:
            self.in_q[port] = queue


class Network:
    def __init__(
        self,
        name: str,
        nodes: Dict,
        edges: List[Tuple[str, str, str, str]] = None,
        inports: Optional[List[str]] = None,
        outports: Optional[List[str]] = None,
        init_fn: Optional[Callable[[Agent], None]] = None,
    ):
        self.name = name
        self.nodes = nodes
        self.edges = edges
        self.inports = inports or []
        self.outports = outports or []
        self.init_fn = init_fn
        # For inport in self.inports self.in_q[inport] is a queue.
        self.in_q = {}
        # For outport in self.outports self.out_q[outport] is a queue.
        self.out_q = {}

    def check(self):
        '''
        Validates that:
        - All referenced node and port names are valid.
        - An inport of the entire network feeds (i.e. is connected to) exactly one inport of 
            a component node of the network.
        - An outport of the entire network is fed by exactly one outport of a component
            node of the network.
        - Each outport of a component node is connected exactly once. 
            An outport of a component node feeds either exactly one inport of a component node
            or feeds an outport of the entire network.
        - Each inport of a component node can be connected an arbitrary number of times.
            An inport of a component node can be fed by multiple inports of the entire
            network and by multiple outports of component nodes.

        '''
        # Helper for clear errors
        def assert_single_connection(port, matches):
            if len(matches) != 1:
                raise ValueError(
                    f'{port} must be connected exactly once, but found {len(matches)} connections.'
                )

        # 1. Make sure that there is no node called 'external'
        if 'external' in self.nodes:
            raise ValueError(
                f' *external* is a reserved keyword and cannot be used as a node name.'
            )

        # 2. Check edges

        for edge in self.edges:
            # Check edges from network input ports
            if edge[0] == "external":
                if edge[1] not in self.inports:
                    raise ValueError(
                        f' The network {self.name} has no input port called {edge[1]}.')
                if edge[2] not in self.nodes.keys():
                    raise ValueError(
                        f''' The network {self.name} input port {edge[1]} is connected to node {edge[2]} 
                        which is not one of the declared nodes of the network.''')
                if edge[3] not in self.inports:
                    raise ValueError(
                        f''' The network {self.name} input port {edge[1]} is connected to port {edge[3]}
                        of node {edge[2]}. But {edge[3]} is not an input port of node {edge[2]}.''')

            # Check edges to network output ports
            if edge[2] == "external":
                if edge[3] not in self.outports:
                    raise ValueError(
                        f''' The network {self.name} has no output port called {edge[3]}.''')
                if edge[0] not in self.nodes.keys():
                    raise ValueError(
                        f''' The network {self.name} output port {edge[3]} is connected to 
                        node {edge[0]} which is not one of the declared nodes of the network.''')
                if edge[1] not in self.outports:
                    raise ValueError(
                        f''' The network {self.name} output port {edge[3]} is connected to port {edge[1]} 
                        of node {edge[0]}. But {edge[1]} is not an output port of node {edge[0]}.''')
            # Check internal edges
            if (edge[0] != 'external') and (edge[2] != 'external'):
                if edge[0] not in self.nodes.keys():
                    raise ValueError(
                        f''' The {edge} of network {self.name} is incorrect.
                        {edge[0]} is not a node of the network.''')
                if edge[2] not in self.nodes.keys():
                    raise ValueError(
                        f''' The {edge} of network {self.name} is incorrect.
                        {edge[2]} is not a node of the network.''')
                if edge[1] not in self.nodes[edge[0]].outports:
                    raise ValueError(
                        f''' The {edge} of network {self.name} is incorrect. {edge[1]} is not an output
                         port of node {self.nodes[edge[0]].name}.''')
                if edge[3] not in self.nodes[edge[2]].inports:
                    raise ValueError(
                        f''' The {edge} of network {self.name} is incorrect.
                        {edge[3]} is not an input port of node {self.nodes[edge[2]].name}.''')

        # 3. Validate network-level inports
        for inport in self.inports:
            matches = [e for e in self.edges if e[0]
                       == "external" and e[1] == inport]
            assert_single_connection(
                port=f"Network {self.name} inport '{inport}'",
                matches=matches)

        # 4. Validate network-level outports
        for outport in self.outports:
            matches = [e for e in self.edges if e[2]
                       == "external" and e[3] == outport]
            assert_single_connection(
                port=f"Network {self.name}  outport '{outport}'",
                matches=matches)

        # 5. Validate each node’s inports and outports
        for node_name, node in self.nodes.items():
            # Outports
            for outport in node.outports or []:
                to_external = [e for e in self.edges if e[0] ==
                               node_name and e[1] == outport and e[2] == "external"]
                to_internal = [e for e in self.edges if e[0] ==
                               node_name and e[1] == outport and e[2] != "external"]

                if len(to_external) == 1 and len(to_internal) == 0:
                    continue  # valid external connection
                elif len(to_internal) == 1 and len(to_external) == 0:
                    continue  # valid internal connection
                else:
                    raise ValueError(
                        f'''Outport '{outport}' of node '{node_name}' of network {self.name}
                        must be connected exactly once. It is connected to {len(to_external)}
                        outports of the network and to {len(to_internal)} inports of nodes
                        in the network.'''
                    )

            # Inports
            for inport in node.inports or []:
                from_external = [e for e in self.edges if e[0] ==
                                 "external" and e[3] == inport and e[2] == node_name]
                from_internal = [e for e in self.edges if e[3] ==
                                 inport and e[2] == node_name and e[0] != "external"]

                if len(from_external) + len(from_internal) == 0:
                    print(f'''WARNING. Input port {inport} of node {node_name} of 
                          network {self.name} is not connected.'''
                          )

    def connect(self):
        for edge in self.edges:
            from_node, from_port, to_node, to_port = edge
            if from_node == "external":
                self.in_q[from_port] = self.nodes[to_node].in_q[to_port]
            elif to_node == "external":
                self.nodes[from_node].out_q[from_port] = self.out_q[to_port]
            else:
                self.nodes[from_node].out_q[from_port] = self.nodes[to_node].in_q[to_port]

    def run(self):
        self.check()
        self.connect()
        for node in self.nodes.values():
            node.run()


class Agent(Network):
    def __init__(
        self,
        inport: Optional[str] = None,
        outports: Optional[List[str]] = None,
        init_fn: Optional[Callable[[Agent], None]] = None,
        handle_msg: Optional[Callable[[Agent, str], None]] = None,
        name: str = "Agent"
    ):
        # Validate: if handling messages, must have an input port
        if handle_msg and not inport:
            raise ValueError(
                "If 'handle_msg' is provided, 'inport' must also be provided.")

        # Define inports and outports
        inports = [inport] if inport else []
        outports = outports or []

        # Create in_q and out_q
        in_q = {inport: SimpleQueue()} if handle_msg and inport else {}
        out_q = {port: None for port in outports}

        # Call Network constructor
        super().__init__(
            name=name,
            nodes={},
            edges=[],
            inports=inports,
            outports=outports,
            init_fn=init_fn
        )

        # Set instance-specific attributes
        self.inport = inport
        self.outports = outports
        self.init_fn = init_fn
        self.handle_msg = handle_msg
        self.in_q = in_q
        self.out_q = out_q
        self.input_queue = in_q[inport] if handle_msg and inport else None

    def send(self, msg, outport: str):
        if outport not in self.out_q:
            raise ValueError(f"{outport} is not an output port.")
        if self.out_q[outport] is None:
            raise ValueError(
                f"The outport, {outport}, is not connected to an input port.")
        self.out_q[outport].put(msg)

    def run(self):
        # Run the initialization function if it exists
        if self.init_fn:
            self.init_fn(self)
        # Run the handle_msg function if it exists.
        # Stop processing messages when '__STOP__' is received.
        if not self.handle_msg:
            return
        while True:
            msg = self.input_queue.get()
            if msg == "__STOP__":
                break
            self.handle_msg(self, msg)

from assignment_6.prt_system.station import Station
from assignment_6.prt_system.prt_model import PRTModel
from pypdevs.simulator import Simulator
from pypdevs.DEVS import *

import pydot

class DotBuilder:
    def __init__(self):
        self.node_counter = None
        self.node_dict = None
        self.output = None
        self.started_models = None
        self.added_connections = None

    def reset(self):
        self.node_counter = 0
        self.node_dict = dict()
        self.output = ""
        self.started_models = set()
        self.added_connections = set()

    def get_unique_name(self):
        self.node_counter += 1
        return f"n{self.node_counter}"

    def append(self, text):
        self.output += f"{text}\n"

    def getNode(self, obj):
        # Returns or creates a node for given object
        if obj not in self.node_dict:
            # assert name is not None #
            node_name = self.get_unique_name()
            self.node_dict[obj] = node_name
            self.append(f"{node_name}[label=\"{obj.name}\"]")

        return self.node_dict[obj]

    def addConnection(self, model_from, model_to):
        if (model_from, model_to) in self.added_connections:
            return
        self.added_connections.add((model_from, model_to))

        node_from = self.getNode(model_from)
        node_to = self.getNode(model_to)
        self.append(f"{node_from} -> {node_to}")

    def discover_port(self, port):
        model = port.host_DEVS
        for connection in port.inline:
            from_model = connection.host_DEVS
            self.addConnection(from_model, model)
            self.makeConnections(from_model)
        for connection in port.outline:
            to_model = connection.host_DEVS
            self.addConnection(model, to_model)
            self.makeConnections(to_model)

    def makeConnections(self, model):
        if model in self.started_models:
            return
        self.started_models.add(model)

        for inport in model.IPorts:
            self.discover_port(inport)
        for outport in model.OPorts:
            self.discover_port(outport)

    def toDot(self, model: PRTModel):
        self.reset()
        self.append("digraph G {")

        # We should just start in a random station, but to be sure there aren't any stations without connections from
        #  and to, we do this for all stations and rails
        for station_name in model.stations:
            station = model.stations[station_name]
            self.makeConnections(station)
        for rail_name in model.rails:
            rail = model.rails[rail_name]
            self.makeConnections(rail)

        self.append("}")
        return self.output


if __name__ == '__main__':
    model = PRTModel("Main")
    dotBuilder = DotBuilder()
    output = dotBuilder.toDot(model)
    dot_output = "output.dot"
    with open(dot_output, "w") as file:
        file.write(output)

    # (graph,) = pydot.graph_from_dot_file(dot_output)
    # graph.write_png('output.png')




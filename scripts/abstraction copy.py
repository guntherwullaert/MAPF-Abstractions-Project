import clingo, os, subprocess

from numpy import full

class AbstractedMap():
    def __init__(self):
        self.layer = 0
        self.nodes = []
        self.edges = []
        self.cliques = []
        self.loners = []
        self.loner_connections = {}

        self.latest_model = []

    def load_in_clingo(self, ctl):
        for node in self.nodes:
            ctl.add("base", [], str(node) + ".")
        for edge in self.edges:
            ctl.add("base", [], str(edge) + ".")

    def vizualize(self):
        if (os.path.exists("out/to_viz")):
            os.remove("out/to_viz")
        with open('out/to_viz', 'w') as f:
            for node in self.nodes:
                f.write(str(node) + ".")
            for edge in self.edges:
                f.write(str(edge) + ".")
            for clique in self.cliques:
                clique_definition = "clique("
                for atom in clique:
                    clique_definition += str(atom) + ","
                    f.write(f"clique_count_node_is_in({atom}, {len(clique)}).")
                clique_definition = clique_definition[:-1] + ")."
                f.write(clique_definition)
        
        output = subprocess.run(["clingraph", "out/to_viz", "encodings/viz.lp", "--engine=neato", "--format=pdf"])
        print(output)

    def create_abstraction(self):
        abstraction = AbstractedMap()
        abstraction.layer = self.layer + 1

        print("Abstraction Layer: ", abstraction.layer)

        # find orphans
        orphans = []
        for loner in self.loners:
            if len(self.loner_connections[loner]) == 1:
                orphans.append(loner)
            else:
                # add all loners as a clique consisting of itself:
                self.cliques.append([loner])

        for orphan in orphans:
            self.loners.remove(orphan)
            for clique in self.cliques:
                if self.loner_connections[orphan][0] in clique:
                    clique.append(orphan)
                    break
            self.loner_connections.pop(orphan, None)

        print("Orphans: ", orphans)

        # Create a dictionary with usefull information for upcomming calculations
        nodes = {}
        for node in self.nodes:
            nodes[node.arguments[0]] = {}

            clique_index = [i for i in range(len(self.cliques)) if node.arguments[0] in self.cliques[i]]
            if len(clique_index) > 0:
                clique_index = clique_index[0]

            nodes[node.arguments[0]]["clique_id"] = clique_index

        print("Nodes Dict: ", nodes)

        # create for every clique an node
        for clique in self.cliques:
            print(clique)
            clique_id = nodes[clique[0]]["clique_id"]
            abstraction.nodes.append(clique_id)

            # create edges between new nodes
            for node in clique:
                for edge in self.edges:
                    if edge.arguments[0] == node and nodes[edge.arguments[1]]["clique_id"] != clique_id:
                        abstraction.edges.append((clique_id, nodes[edge.arguments[1]]["clique_id"]))
        
def on_model_load_input(m, map):
    for symbol in m.symbols(shown=True):
        if(str(symbol).startswith("node")):
            map.nodes.append(symbol)
        if(str(symbol).startswith("edge")):
            map.edges.append(symbol)

def on_model_load_abstraction(m, map):
    map.latest_model = m.symbols(shown=True)

def load_abstraction_finished(map):
    for symbol in map.latest_model:
        if(str(symbol).startswith("in_clique_with")):
            node_to_check = symbol.arguments[0]
            node_to_be_in_clique = symbol.arguments[1]

            found_clique = False
            for clique in map.cliques:
                if node_to_be_in_clique in clique:
                    if node_to_check not in clique:
                        clique.append(node_to_check)
                    found_clique = True
            
            if(not found_clique):
                map.cliques.append([node_to_check, node_to_be_in_clique])
        if(str(symbol).startswith("loner(")):
            map.loners.append(str(symbol.arguments[0]))
        if(str(symbol).startswith("loner_connected_with")):
            loner = str(symbol.arguments[0])
            connected_with = str(symbol.arguments[1])

            if loner in map.loner_connections:
                map.loner_connections[loner].append(connected_with)
            else:
                map.loner_connections[loner] = [connected_with]

# Create an object where we can store the full map
full_map = AbstractedMap()

def run():
    full_map = AbstractedMap()

    # Load instance and translate input
    ctl = clingo.Control()
    ctl.load("instances/corridor_instance.lp")
    ctl.load("encodings/input.lp")
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: on_model_load_input(m, full_map))

    # Find cliques in the first abstraction graph
    ctl = clingo.Control()
    ctl.load("encodings/find-cliques.lp")
    full_map.load_in_clingo(ctl)
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: on_model_load_abstraction(m, full_map))
    load_abstraction_finished(full_map)
    #print(ctl.configuration.solve.keys)
    #print(ctl.configuration.solve.__desc_solve_limit)

    print(full_map.cliques)
    print(full_map.loners)
    print(full_map.loner_connections)
    #full_map.vizualize()

    full_map.create_abstraction()

run()
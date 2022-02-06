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
            ctl.add("base", [],  f"node({node['id']}).")
        for edge in self.edges:
            ctl.add("base", [], f"edge(({edge['id']}, {edge['id2']})).")

    def vizualize(self):
        if (os.path.exists("out/to_viz")):
            os.remove("out/to_viz")
        with open('out/to_viz', 'w') as f:
            for node in self.nodes:
                f.write(f"node({node['id']}).")
            for edge in self.edges:
                f.write(f"edge(({edge['id']}, {edge['id2']})).")
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

        # Create a dictionary with usefull information for upcomming calculations
        nodes = {}
        for node in self.nodes:
            nodes[node["id"]] = {}

            clique_index = [i for i in range(len(self.cliques)) if str(node["id"]) in self.cliques[i]]

            if len(clique_index) > 0:
                clique_index = clique_index[0]

            nodes[node["id"]]["clique_id"] = str(clique_index)

        # create for every clique an node
        for clique in self.cliques:
            clique_id = nodes[str(clique[0])]["clique_id"]
            abstraction.nodes.append({
                "id": clique_id
            })

            # create edges between new nodes
            for node in clique:
                for edge in self.edges:
                    if edge["id"] == node and nodes[edge["id2"]]["clique_id"] != clique_id:
                        abstraction.edges.append({
                            "id": clique_id, 
                            "id2": nodes[edge["id2"]]["clique_id"]
                        })

        return abstraction

def on_model_load_input(m, map):
    for symbol in m.symbols(shown=True):
        if(str(symbol).startswith("node")):
            map.nodes.append({
                "id": str(symbol.arguments[0])
            })
        if(str(symbol).startswith("edge")):
            map.edges.append({
                "id": str(symbol.arguments[0].arguments[0]),
                "id2": str(symbol.arguments[0].arguments[1])
            })

def on_model_load_abstraction(m, map):
    map.latest_model = m.symbols(shown=True)

def load_abstraction_finished(map):
    for symbol in map.latest_model:
        if(str(symbol).startswith("in_clique_with")):
            node_to_check = str(symbol.arguments[0])
            node_to_be_in_clique = str(symbol.arguments[1])

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

def vizualize_maps(*maps):
    if (os.path.exists("out/to_viz")):
        os.remove("out/to_viz")
    with open('out/to_viz', 'w') as f:
        for map in maps:
            f.write(f"graph(abstraction_{map.layer}).")
            for node in map.nodes:
                f.write(f"node(a{map.layer}n{node['id']}, abstraction_{map.layer}).")
            for edge in map.edges:
                f.write(f"edge((a{map.layer}n{edge['id']}, a{map.layer}n{edge['id2']}), abstraction_{map.layer}).")
            for clique in map.cliques:
                clique_definition = "clique("
                for atom in clique:
                    clique_definition += str(atom) + ","
                    f.write(f"clique_count_node_is_in(a{map.layer}n{atom}, {len(clique)}, abstraction_{map.layer}).")
                clique_definition = clique_definition[:-1] + ")."
                f.write(clique_definition)
    
    output = subprocess.run(["clingraph", "out/to_viz", "encodings/viz.lp", "--engine=neato", "--format=pdf"])


def run():
    full_map = AbstractedMap()

    # Load instance and translate input
    ctl = clingo.Control()
    ctl.load("instances/small_grid.lp") # TODO: Als parameter übertragen
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

    abstraction = full_map.create_abstraction()
    #abstraction.vizualize()
    
    # Find cliques in the second abstraction graph
    ctl = clingo.Control()
    ctl.load("encodings/find-cliques.lp")
    abstraction.load_in_clingo(ctl)
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: on_model_load_abstraction(m, abstraction))
    load_abstraction_finished(abstraction)

    abstraction2 = abstraction.create_abstraction()

    # Find cliques in the second abstraction graph
    ctl = clingo.Control()
    ctl.load("encodings/find-cliques.lp")
    abstraction2.load_in_clingo(ctl)
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: on_model_load_abstraction(m, abstraction2))
    load_abstraction_finished(abstraction2)

    abstraction3 = abstraction2.create_abstraction()
    
    vizualize_maps(full_map, abstraction, abstraction2, abstraction3)

run()
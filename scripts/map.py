import os, subprocess
from pydoc import cli
from itertools import product, groupby

class AbstractedMap():
    def __init__(self):
        self.layer = 0
        self.nodes = []
        self.edges = []
        self.robots = []
        self.goals = []
        self.cliques = []
        self.loners = []
        self.loner_connections = {}

        self.latest_model = []

    def load_in_clingo(self, ctl):
        for node in self.nodes:
            ctl.add("base", [],  f"node({node['id']}).")
        for edge in self.edges:
            ctl.add("base", [], f"edge(({edge['id']}, {edge['id2']})).")
        for robot in self.robots:
            ctl.add("base", [], f"robot_at({robot['id']}, {robot['node_id']}).")
        for goal in self.goals:
            ctl.add("base", [], f"goal({goal['node_id']}, {goal['count']}).")

        ctl.add("base", [], f"robot(ID) :- robot_at(ID, _).")

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

    def on_model_load_input(self, m):
        for symbol in m.symbols(shown=True):
            if(str(symbol).startswith("node")):
                self.nodes.append({
                    "id": str(symbol.arguments[0])
                })
            if(str(symbol).startswith("edge")):
                self.edges.append({
                    "id": str(symbol.arguments[0].arguments[0]),
                    "id2": str(symbol.arguments[0].arguments[1])
                })
            if(str(symbol).startswith("robot_at")):
                self.robots.append({
                    "id": str(symbol.arguments[0]),
                    "node_id": str(symbol.arguments[1])
                })
            if(str(symbol).startswith("goal")):
                self.goals.append({
                    'node_id': str(symbol.arguments[0]),
                    'count': int(str(symbol.arguments[1]))
                })
    
    def on_model_load_abstraction(self, m):
        self.latest_model = m.symbols(shown=True)

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
            clique_id = nodes[str(next(iter(clique)))]["clique_id"]
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

        # Transfer goals and robots to the new abstraction
        for robot in self.robots:
            abstraction.robots.append({
                "id": robot["id"],
                "node_id": nodes[robot["node_id"]]["clique_id"]
            })

        new_goals = {}
        for goal in self.goals:
            clique_id = nodes[goal["node_id"]]["clique_id"]
            if(clique_id in new_goals.keys()):
                new_goals[clique_id] += goal["count"]
            else:
                new_goals[clique_id] = goal["count"]
        for node, count in new_goals.items():
            abstraction.goals.append({
                "node_id": node,
                "count": count
            })

        return abstraction

    def load_abstraction_finished(self):
        cliques = []
        for symbol in self.latest_model:
            if(str(symbol).startswith("in_clique_with")):
                cliques.append({str(symbol.arguments[0]), str(symbol.arguments[1])})

            if(str(symbol).startswith("loner(")):
                self.loners.append(str(symbol.arguments[0]))
            if(str(symbol).startswith("loner_connected_with")):
                loner = str(symbol.arguments[0])
                connected_with = str(symbol.arguments[1])

                if loner in self.loner_connections:
                    self.loner_connections[loner].append(connected_with)
                else:
                    self.loner_connections[loner] = [connected_with]

        # Merge all cliques containing common elements
        #cartesian product merging elements if some element in common
        for a,b in product(cliques,cliques):
            if a.intersection(b):
                a.update(b)
                b.update(a)

        #back to list of lists
        cliques = sorted( [sorted(list(x)) for x in cliques])

        #remove dups
        self.cliques = list(l for l,_ in groupby(cliques))

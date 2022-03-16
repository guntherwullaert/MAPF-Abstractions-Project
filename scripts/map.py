import os, subprocess, clingo
from tkinter import W
from time import time
from pydoc import cli
from itertools import product, groupby

class AbstractedMap():
    def __init__(self):
        self.layer = 0
        self.nodes = []
        self.node_count = {}
        self.node_coord = {}
        self.edges = []
        self.robots = []
        self.goals = []
        self.cliques = []
        self.loners = []
        self.loner_connections = {}
        self.paths = {}
        self.nodes_in_clique = {}

        self.latest_model = []

    def load_in_clingo(self, ctl, paths = {}):
        for node in self.nodes:
            ctl.add("base", [],  f"node({node['id']}).")
        for node_id, coord in self.node_coord.items():
            ctl.add("base", [],  f"coord_of_node({node_id}, {coord[0]}, {coord[1]}).")
        for node_id, count in self.node_count.items():
            ctl.add("base", [],  f"count_of_node({node_id}, {count}).")
        for edge in self.edges:
            ctl.add("base", [], f"edge(({edge['id']}, {edge['id2']})).")
            
        for robot in self.robots:
                ctl.add("base", [], f"robot_at({robot['id']}, {robot['node_id']}).")

        for goal in self.goals:
            ctl.add("base", [], f"goal({goal['node_id']}, {goal['count']}).")

        for robot_id, path in paths.items():
            for step, node_id in path.items():
                ctl.add("base", [], f"path({robot_id}, {node_id}, {step}).")

        for clique_id, nodes in self.nodes_in_clique.items():
            for node in nodes:
                ctl.add("base", [], f"node_in_clique({clique_id}, {node}).")

        ctl.add("base", [], f"robot(ID) :- robot_at(ID, _).")

    def solve(self, horizon, paths = {}):
        ctl = clingo.Control(["--heuristic=Domain"])
        ctl.add("base", [], f"#const horizon={horizon}.")
        ctl.load("encodings/solve-map.lp")
        self.load_in_clingo(ctl, paths)
        ctl.ground([("base", [])])
        with open("out/solution.lp", 'w') as f:
            ctl.solve(on_model= lambda m: self.on_model_solution(m, f))

    def vizualize(self, f, timestep = -1):
        robots_connected_to_node = {}

        timestep_append = ""
        if(timestep != -1):
            timestep_append = f"_S{timestep}"

        graph_name = f"abstraction_{self.layer}{timestep_append}"

        f.write(f"graph({graph_name}).")
        for node in self.nodes:
            f.write(f"node(a{self.layer}n{node['id']}s{timestep_append}, {graph_name}).")
        for edge in self.edges:
            f.write(f"edge((a{self.layer}n{edge['id']}s{timestep_append}, a{self.layer}n{edge['id2']}s{timestep_append}), {graph_name}).")
        
        if(timestep == -1):
            for robot in self.robots:
                #f.write(f"robot({robot['id']}, a{map.layer}n{robot['node_id']}, abstraction_{map.layer}).")
                if robot["node_id"] in robots_connected_to_node.keys():
                    robots_connected_to_node[robot["node_id"]].append(robot["id"])
                else:
                    robots_connected_to_node[robot["node_id"]] = [robot["id"]]
        else:
            for robot, steps in self.paths.items():
                if steps[timestep] in robots_connected_to_node.keys():
                    robots_connected_to_node[steps[timestep]].append(robot)
                else:
                    robots_connected_to_node[steps[timestep]] = [robot]

        for goal in self.goals:
            f.write(f"goal(a{self.layer}n{goal['node_id']}s{timestep_append}, {graph_name}).")
        for clique in self.cliques:
            clique_definition = "clique("
            for atom in clique:
                clique_definition += str(atom) + ","
                f.write(f"clique_count_node_is_in(a{self.layer}n{atom}s{timestep_append}, {len(clique)}, {graph_name}).")
            clique_definition = clique_definition[:-1] + ")."
            f.write(clique_definition)

        for node in self.nodes:
            label = f"{node['id']}({self.node_count[node['id']]})"
            if node['id'] in robots_connected_to_node.keys():
                robot_string = ""
                for r in robots_connected_to_node[node['id']]:
                    robot_string += "R" + r + " "
                label = label + " - " + robot_string

            f.write(f"attr(node, a{self.layer}n{node['id']}s{timestep_append}, label, \"{label}\").")

        for node_id, coord in self.node_coord.items():
            f.write(f"attr(node, a{self.layer}n{node_id}s{timestep_append}, pos, \"{coord[0]},{coord[1]}!\").")

    def vizualize_solution_for_map(self, f, horizon):
        for step in range(horizon+1):
            self.vizualize(f, step)

    def on_model_load_input(self, m):
        for symbol in m.symbols(shown=True):
            if(str(symbol).startswith("node")):
                self.nodes.append({
                    "id": str(symbol.arguments[0])
                })
            elif(str(symbol).startswith("count_of_node")):
                self.node_count[str(symbol.arguments[0])] = str(symbol.arguments[1])
            elif(str(symbol).startswith("coord_of_node")):
                self.node_coord[str(symbol.arguments[0])] = [str(symbol.arguments[1]), str(symbol.arguments[2])]
            elif(str(symbol).startswith("edge")):
                self.edges.append({
                    "id": str(symbol.arguments[0].arguments[0]),
                    "id2": str(symbol.arguments[0].arguments[1])
                })
            elif(str(symbol).startswith("robot_at")):
                self.robots.append({
                    "id": str(symbol.arguments[0]),
                    "node_id": str(symbol.arguments[1])
                })
            elif(str(symbol).startswith("goal")):
                self.goals.append({
                    'node_id': str(symbol.arguments[0]),
                    'count': int(str(symbol.arguments[1]))
                })

    def on_model_load_abstraction(self, m):
        self.latest_model = m.symbols(shown=True)

    def on_model_output_to_file(self, m, file):
        for atom in m.symbols(shown=True):
            file.write(f"{atom}.\n")

    def on_model_solution(self, m, file):
        for symbol in m.symbols(shown=True):
            if(str(symbol).startswith("robot_at") and len(symbol.arguments) > 2):
                robot_id = str(symbol.arguments[0])
                node_id = str(symbol.arguments[1])
                step = int(str(symbol.arguments[2]))

                if robot_id in self.paths.keys():
                    self.paths[robot_id][step] = node_id 
                else:
                    self.paths[robot_id] = {step : node_id}
                
        self.on_model_output_to_file(m, file)

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
            abstraction.node_coord[clique_id] = self.node_coord[str(next(iter(clique)))]

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

        #remove duplicate nodes
        #TODO: Find out why it happens
        abstraction.nodes = [x for n, x in enumerate(abstraction.nodes) if abstraction.nodes.index(x) == n]

        self.nodes_in_clique = {}

        for node, element in nodes.items():
            if element["clique_id"] in self.nodes_in_clique:
                self.nodes_in_clique[element["clique_id"]].append(node)
            else:
                self.nodes_in_clique[element["clique_id"]] = [node]

        for clique, nodes in self.nodes_in_clique.items():
            total_count = 0
            for node in nodes: 
                total_count += int(self.node_count[node])
            abstraction.node_count[clique] = total_count

        return abstraction

    def load_abstraction_finished(self):
        cliques = []
        for symbol in self.latest_model:
            if(str(symbol).startswith("clique")):
                clique = []
                for argument in symbol.arguments:
                    clique.append(str(argument))
                cliques.append(set(clique))

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
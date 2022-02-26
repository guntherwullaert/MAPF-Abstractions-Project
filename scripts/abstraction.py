import string
import clingo, os, subprocess, argparse

from numpy import full
from map import AbstractedMap

def vizualize_maps(*maps):
    if (os.path.exists("out/to_viz")):
        os.remove("out/to_viz")
    with open('out/to_viz', 'w') as f:        
        for map in maps:
            robots_connected_to_node = {}

            f.write(f"graph(abstraction_{map.layer}).")
            for node in map.nodes:
                f.write(f"node(a{map.layer}n{node['id']}, abstraction_{map.layer}).")
            for edge in map.edges:
                f.write(f"edge((a{map.layer}n{edge['id']}, a{map.layer}n{edge['id2']}), abstraction_{map.layer}).")
            for robot in map.robots:
                #f.write(f"robot({robot['id']}, a{map.layer}n{robot['node_id']}, abstraction_{map.layer}).")
                if robot["node_id"] in robots_connected_to_node.keys():
                    robots_connected_to_node[robot["node_id"]].append(robot["id"])
                else:
                   robots_connected_to_node[robot["node_id"]] = [robot["id"]]
            for goal in map.goals:
                f.write(f"goal(a{map.layer}n{goal['node_id']}, abstraction_{map.layer}).")
            for clique in map.cliques:
                clique_definition = "clique("
                for atom in clique:
                    clique_definition += str(atom) + ","
                    f.write(f"clique_count_node_is_in(a{map.layer}n{atom}, {len(clique)}, abstraction_{map.layer}).")
                clique_definition = clique_definition[:-1] + ")."
                f.write(clique_definition)
    

            for node in map.nodes:
                label = node['id']
                if node['id'] in robots_connected_to_node.keys():
                    robot_string = ""
                    for r in robots_connected_to_node[node['id']]:
                        robot_string += "R" + r + " "
                    label = label + " - " + robot_string
                f.write(f"attr(node, a{map.layer}n{node['id']}, label, \"{label}\").")

    clin_out = subprocess.Popen(['clingo', 'out/to_viz', 'encodings/viz.lp', '-n', '0', '--outf=2'], stdout=subprocess.PIPE)
    output = subprocess.run(["clingraph", "--json", "--render", "--engine=neato", "--format=pdf"], stdin=clin_out.stdout)

def save_to_file(m, file):
    if (os.path.exists(file)):
        os.remove(file)

    with open(file, 'w') as f:
        for atom in m.symbols(shown=True):
            f.write(f"{atom}.")

def abstract(args, map):
    ctl = clingo.Control()
    ctl.load("encodings/find-cliques.lp")
    map.load_in_clingo(ctl)
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: map.on_model_load_abstraction(m))
    map.load_abstraction_finished()

    if(args.cliques):
        print(f"Cliques[{map.layer}]: ", map.cliques)

    abstraction = map.create_abstraction()

    if(args.debug):
        ctl = clingo.Control()
        map.load_in_clingo(ctl)
        ctl.ground([("base", [])])
        ctl.solve(on_model= lambda m: save_to_file(m, f"out/map_{abstraction.layer}.lp"))

    return abstraction

def run(args):
    full_map = AbstractedMap()

    # Load instance and translate input
    ctl = clingo.Control()
    ctl.load(args.instance)
    ctl.load("encodings/input.lp")
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: full_map.on_model_load_input(m))

    if(args.debug):
        ctl = clingo.Control()
        full_map.load_in_clingo(ctl)
        ctl.ground([("base", [])])
        ctl.solve(on_model= lambda m: save_to_file(m, f"out/map_{full_map.layer}.lp"))

    # Find cliques in the first abstraction graph
    map = full_map
    maps = [full_map]
    for i in range(args.abstractions):
        map = abstract(args, map)
        maps.append(map)
    
    if(args.vizualize):
        vizualize_maps(*maps)


parser = argparse.ArgumentParser()

parser.add_argument("-i", "--instance", help="Instance to do the abstractions for", required=True)
parser.add_argument("-d", "--debug", help="If each map's clingo representation is saved to a file", action='store_true')
parser.add_argument("-a", "--abstractions", help="How many abstractions should be created", type=int, required=True)
parser.add_argument("-c", "--cliques", help="If the exact cliques should be printed", action='store_true')
parser.add_argument("-v", "--vizualize", help="If the graphs should be vizualized", action='store_true')

args = parser.parse_args()

run(args)
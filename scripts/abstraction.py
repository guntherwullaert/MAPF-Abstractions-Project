import string
import clingo, os, subprocess, argparse

from numpy import full
from map import AbstractedMap

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
    
    vizualize_maps(*maps)


parser = argparse.ArgumentParser()

parser.add_argument("-i", "--instance", help="Instance to do the abstractions for")
parser.add_argument("-d", "--debug", help="If each map's clingo representation is saved to a file", action='store_true')
parser.add_argument("-a", "--abstractions", help="How many abstractions should be created", type=int)

args = parser.parse_args()

run(args)
import string
import clingo, os, subprocess, argparse

from numpy import full
from map import AbstractedMap

def vizualize_maps(*maps):
    if (os.path.exists("out/to_viz")):
        os.remove("out/to_viz")
    with open('out/to_viz', 'w') as f:        
        for map in maps:
            map.vizualize(f)

    clin_out = subprocess.Popen(['clingo', 'out/to_viz', 'encodings/viz.lp', '-n', '0', '--outf=2'], stdout=subprocess.PIPE)
    output = subprocess.run(["clingraph", "--json", "--render", "--engine=neato", "--format=pdf", "-q"], stdin=clin_out.stdout)

def vizualize_solution_for_map(map, horizon):
    if (os.path.exists("out/to_viz")):
        os.remove("out/to_viz")
    with open('out/to_viz', 'w') as f:        
        map.vizualize_solution_for_map(f, horizon)

    clin_out = subprocess.Popen(['clingo', 'out/to_viz', 'encodings/viz.lp', '-n', '0', '--outf=2'], stdout=subprocess.PIPE)
    output = subprocess.run(["clingraph", "--json", "--render", "--engine=neato", "--format=pdf", "--gif", "--gif-name=path_animation.gif", "-q", "--select-model=1"], stdin=clin_out.stdout)


def save_to_file(m, file):
    if (os.path.exists(file)):
        os.remove(file)

    with open(file, 'w') as f:
        for atom in m.symbols(shown=True):
            f.write(f"{atom}.")

def abstract(args, map):
    ctl = clingo.Control(["--heuristic=Domain"])
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
        abstraction.load_in_clingo(ctl)
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

    horizon = 2

    #maps[-1].solve(horizon)
    #maps[-2].solve(horizon*2, maps[-1].paths)
    #vizualize_solution_for_map(maps[-2], horizon*2)

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
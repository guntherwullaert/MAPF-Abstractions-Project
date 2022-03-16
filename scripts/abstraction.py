import string
import clingo, os, subprocess, argparse, time

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
    output = subprocess.run(["clingraph", "--json", "--render", "--engine=neato", "--format=pdf", "--gif", "--gif-name=path_animation.gif", "-q", "--select-model=1", "--gif-param=fps=1"], stdin=clin_out.stdout)


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
    performance_start_time = time.perf_counter_ns()
    start_time = time.process_time_ns()

    full_map = AbstractedMap()

    start_input_translation_time = time.process_time_ns()

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

    if(args.benchmark):
        end_input_translation_time = time.process_time_ns()
        print(f"Input Translation: {end_input_translation_time - start_input_translation_time}ns")


    # Find cliques in the first abstraction graph
    total_abstractions_time = 0
    map = full_map
    maps = [full_map]
    for i in range(args.abstractions):
        start_layer_time = time.process_time_ns()

        map = abstract(args, map)
        maps.append(map)

        if(args.benchmark):
            end_layer_time = time.process_time_ns()
            total_abstractions_time += end_layer_time - start_layer_time
            print(f"Abstracting layer {map.layer}: {end_layer_time - start_layer_time}ns")

    if(args.benchmark):
        print(f"Total Time needed for Abstracting: {total_abstractions_time}ns")

    horizon = args.horizon
    final_horizon = horizon

    #print("Solving for Map 3")
    #maps[-1].solve(horizon)
    #print("Solving for Map 2")
    #maps[-2].solve(horizon*2+2, maps[-1].paths)
    #print("Solving for Map 1")
    #maps[-3].solve(horizon*4+6, maps[-2].paths)
    #print("Solving for Map 0")
    #maps[-4].solve(horizon*8+13, maps[-3].paths)
    #print("Vizualizing")
    #vizualize_solution_for_map(maps[-4], horizon*8+5)

    #vizualize_solution_for_map(maps[-4], horizon*8+13)
    #vizualize_solution_for_map(maps[-4], horizon*8+16)

    #print("Solving for Map 3")
    #maps[-1].solve(horizon)
    #print("Solving for Map 2")
    #maps[-2].solve(horizon*2+2, maps[-1].paths)
    #print("Solving for Map 1")
    #maps[-3].solve(horizon*4+6, maps[-2].paths)
    #print("Solving for Map 0")
    #maps[-4].solve(horizon*8+13, maps[-3].paths)
    #print("Vizualizing")
    
    #vizualize_solution_for_map(maps[-4], horizon*8+9)

    if(args.solving):
        total_solving_time = 0
        previous_map = False
        for map in maps[::-1]:
            print(f"Solving for map layer {map.layer} with horizon={final_horizon}")
            start_solving_time = time.process_time_ns()

            if(previous_map == False):
                map.solve(final_horizon, args.wait)
            else:
                map.solve(final_horizon, args.wait, previous_map.paths)
            final_horizon = (final_horizon + 1) * 2
            previous_map = map

            if map.paths == {}:
                print("No solution was found!")
                break
            
            if(args.benchmark):
                end_solving_time = time.process_time_ns()
                total_solving_time += end_solving_time - start_solving_time
                print(f"Solving time for map layer {map.layer} with horizon={final_horizon}: {end_solving_time - start_solving_time}ns")

        if map.paths != {}:
            print(previous_map.paths)

        if(args.benchmark):
                print(f"Total Solving Time: {total_solving_time}ns")

    if(args.vizualize):
        if(args.solving):
            vizualize_solution_for_map(maps[0], final_horizon)
        else:
            vizualize_maps(*maps)

    if(args.benchmark):
        performance_end_time = time.perf_counter_ns()
        end_time = time.process_time_ns()

        print(f"Total Real World Time Elapsed: {performance_end_time - performance_start_time}ns")
        print(f"Total Processing Time Elapsed: {end_time - start_time}ns")

parser = argparse.ArgumentParser()

parser.add_argument("-i", "--instance", help="Instance to do the abstractions for", required=True)
parser.add_argument("-d", "--debug", help="If each map's clingo representation is saved to a file", action='store_true')
parser.add_argument("-a", "--abstractions", help="How many abstractions should be created", type=int, required=True)
parser.add_argument("-c", "--cliques", help="If the exact cliques should be printed", action='store_true')
parser.add_argument("-v", "--vizualize", help="If the graphs should be vizualized", action='store_true')
parser.add_argument("-b", "--benchmark", help="If the benchmark stats should be output", action='store_true')
parser.add_argument("-s", "--solving", help="If the solving should be run after abstraction requires horizon and wait to be set", action='store_true')
parser.add_argument("-w", "--wait", help="How often the plan can be shifted", type=int)
parser.add_argument("-o", "--horizon", help="How long the smallest plan can be for the most abstracted layer", type=int)

args = parser.parse_args()

run(args)
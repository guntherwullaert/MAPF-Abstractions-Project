import clingo, os, subprocess, sys

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

def run(instance):
    full_map = AbstractedMap()

    # Load instance and translate input
    ctl = clingo.Control()
    ctl.load(instance)
    ctl.load("encodings/input.lp")
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: full_map.on_model_load_input(m))

    # Find cliques in the first abstraction graph
    ctl = clingo.Control()
    ctl.load("encodings/find-cliques.lp")
    full_map.load_in_clingo(ctl)
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: full_map.on_model_load_abstraction(m))
    full_map.load_abstraction_finished()
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
    ctl.solve(on_model= lambda m: abstraction.on_model_load_abstraction(m))
    abstraction.load_abstraction_finished()

    abstraction2 = abstraction.create_abstraction()

    # Find cliques in the second abstraction graph
    ctl = clingo.Control()
    ctl.load("encodings/find-cliques.lp")
    abstraction2.load_in_clingo(ctl)
    ctl.ground([("base", [])])
    ctl.solve(on_model= lambda m: abstraction2.on_model_load_abstraction(m))
    abstraction2.load_abstraction_finished()

    abstraction3 = abstraction2.create_abstraction()
    
    vizualize_maps(full_map, abstraction, abstraction2, abstraction3)


if(len(sys.argv) < 2):
    print("abstraction.py [instance]")

run(sys.argv[1])
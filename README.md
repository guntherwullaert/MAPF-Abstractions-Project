# MAPF Abstractions Project

Project of Günther Wullaert and Alexander Benjamin Glätzer

run with the following command:

`python scripts\abstraction.py --instance {instance.lp} -a {abstractions} [-cdv]`

flags:
    `-i` `--instance {instance.lp}` - Instance to do the abstractions for  
    `-d` `--debug` - If each map's clingo representation is saved to a file  
    `-a` `--abstractions {number}` - How many abstractions should be created  
    `-c` `--cliques` - If the exact cliques should be printed  
    `-v` `--vizualize` - If the graph should be vizualized  

dependencies:
    - clingraph
    - clingo api


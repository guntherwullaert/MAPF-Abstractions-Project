# MAPF Abstractions Project

Project of Günther Wullaert and Alexander Benjamin Glätzer

run with the input transformation with the following command:

`clingo instances\corridor_instanc.lp encodings\input.lp --outf=0 -V0 --out-atomf=%s. > intermediate-0`

This intermediate format contains the SAT at the end, as there is no head command in windows, we use a script for this:

`python scripts\shorten.py intermediate-0`

For doing an abstraction we use the find-cliques file on the intermediate-0 output :
`clingo intermediate-0 encodings\find-cliques.lp --outf=0 -V0 --out-atomf=%s. > intermediate-1`

Next we can vizualize the graphs for this with clingraph (see: https://clingraph.readthedocs.io/en/latest/):
`clingraph intermediate_1 encodings\viz.lp --format=png --engine=neato`
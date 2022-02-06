# MAPF Abstractions Project

Project of Günther Wullaert and Alexander Benjamin Glätzer

run with the input transformation with the following command:

`clingo instances\corridor_instance.lp encodings\input.lp --outf=0 -V0 --out-atomf=%s. > intermediate-0`

This intermediate format contains the SAT at the end, as there is no head command in windows, we use a script for this:

`python scripts\shorten.py intermediate-0`

For doing an abstraction we use the find-cliques file on the intermediate-0 output :
`clingo intermediate-0 encodings\find-cliques.lp --outf=0 -V0 --out-atomf=%s. > intermediate-1`

Next we can vizualize the graphs for this with clingraph (see: https://clingraph.readthedocs.io/en/latest/):
`clingraph intermediate-1 encodings\viz.lp --format=png --engine=neato`

For Linux:
Input transformation:
`clingo instances/corridor_instance.lp encodings/input.lp --outf=0 -V0 --out-atomf=%s. > intermediate-0`

Remove everything but the first line:
`sed -i '1!d' intermediate-0`

Abstraction:
`clingo intermediate-0 encodings/find-cliques.lp --outf=0 -V0 --out-atomf=%s. > intermediate-1`

Remove suboptimal abstractions:
`sed -i '$!d' intermediate-1`

Vizualization:
`clingraph intermediate-1 encodings/viz.lp --format=pdf --engine=neato`


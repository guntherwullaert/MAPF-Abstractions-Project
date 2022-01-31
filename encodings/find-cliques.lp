{in_clique_with(ID, ID') : edge((ID, ID'))} :- node(ID).

in_clique_with(ID', ID) :- in_clique_with(ID, ID'), ID < ID'.

:- edge((ID, ID')), not in_clique_with(ID, _), not in_clique_with(ID', _).

:- in_clique_with(ID, ID1), in_clique_with(ID1, ID2), not in_clique_with(ID, ID2), ID < ID1, ID < ID2.

clique_count_node_is_in(IDENTIFIER, AMOUNT+1) :- AMOUNT = #count{1, ID2 : in_clique_with(IDENTIFIER,ID2)}, node(IDENTIFIER).

#maximize{2,ID : clique_count_node_is_in(ID, 4)}.
#maximize{1,ID : clique_count_node_is_in(ID, 3)}.
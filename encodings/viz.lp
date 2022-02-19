
attr(edge, UID, arrowhead, none) :- edge(UID, _).

attr(node, ID, color, red) :- clique_count_node_is_in(ID, COUNT, _), COUNT > 4.
attr(node, ID, color, darkorange) :- clique_count_node_is_in(ID, 4, _).
attr(node, ID, color, green) :- clique_count_node_is_in(ID, 3, _).
attr(node, ID, color, blue) :- clique_count_node_is_in(ID, 2, _).

attr(node, ID, shape, doubleoctagon) :- node(ID, A), goal(ID, A).
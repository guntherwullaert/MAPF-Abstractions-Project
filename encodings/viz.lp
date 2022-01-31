
attr(edge, UID, arrowhead, none) :- edge(UID).

attr(node, ID, color, red) :- clique_count_node_is_in(ID, 4).
attr(node, ID, color, green) :- clique_count_node_is_in(ID, 3).
attr(node, ID, color, blue) :- clique_count_node_is_in(ID, 2).
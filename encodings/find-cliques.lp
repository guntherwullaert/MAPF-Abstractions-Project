
% Choose cliques
{clique(ID, ID') : edge((ID, ID'))}.
{clique(ID, ID', ID'') : edge((ID, ID')),edge((ID, ID''))}.
{clique(ID, ID', ID'', ID''') : edge((ID, ID')), edge((ID, ID'')), edge((ID, ID'''))}.

clique(ID', ID) :- clique(ID, ID').
clique(ID'', ID, ID') :- clique(ID, ID', ID'').
clique(ID''', ID, ID', ID'') :- clique(ID, ID', ID'', ID''').

% clique cannot exist if edge does not exist
:- clique(ID, ID'), not edge((ID, ID')).
:- clique(ID, ID', _), not edge((ID, ID')).
:- clique(ID, ID', _, _), not edge((ID, ID')).

% node cannot be in two cliques
:- in_clique_with(ID, ID'), in_clique_with(ID', ID''), not in_clique_with(ID'', ID), ID != ID', ID != ID'', ID' != ID''.

in_clique_with(ID, ID') :- in_clique_with(ID', ID).

in_clique_with(ID, ID') :- clique(ID, ID').
in_clique_with(ID, ID') :- clique(ID, ID', _).
in_clique_with(ID, ID') :- clique(ID, ID', _, _).

loner(ID) :- not clique(ID, _), not clique(ID, _, _), not clique(ID, _, _, _), node(ID).
loner_connected_with(ID, ID') :- loner(ID), edge((ID, ID')).

% Heuristic for finding best cliques
#heuristic loner(ID). [4,false]
#heuristic clique(ID,ID2). [3,false]
#heuristic clique(ID,ID2,ID3). [2,false]
#heuristic clique(ID,ID2,ID3,ID4). [1,false]
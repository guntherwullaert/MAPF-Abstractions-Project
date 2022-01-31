node(ID,X,Y) :- init(object(node,ID),value(at,(X,Y))).

node(ID) :- node(ID,_,_).

edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X+1, Y).
edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X, Y+1).
edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X+1, Y+1).
edge((ID, ID2)) :- node(ID, X, Y+1), node(ID2, X+1, Y).

edge((ID2, ID)) :- edge((ID, ID2)).

#show.
#show node/1.
#show edge/1.
node(ID,X,Y) :- init(object(node,ID),value(at,(X,Y))).

node(ID) :- node(ID,_,_).

edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X+1, Y).
edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X, Y+1).
edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X+1, Y+1).
edge((ID, ID2)) :- node(ID, X, Y+1), node(ID2, X+1, Y).

edge((ID2, ID)) :- edge((ID, ID2)).

% robot definition
robot(R) :- robot_at(R, _).
robot_at(R, ID) :- node(ID,X,Y), init(object(robot,R), value(at,(X,Y))).

% goal definition
goal(ID) :- node(ID,X,Y), init(object(shelf,_),value(at,(X,Y))).

#show.
#show node/1.
#show edge/1.
#show robot/1.
#show robot_at/2.
#show goal/1.
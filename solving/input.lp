% Only temporary, for solving from asprilo instances (maybe useful to get optimal plan to compare?)
node(ID,X,Y) :- init(object(node,ID),value(at,(X,Y))).
start(ID,X,Y) :- init(object(robot,ID),value(at,(X,Y))).
goal(ID,X,Y) :- init(object(shelf,ID),value(at,(X,Y))).


node(ID) :- node(ID,_,_).
robot(ID) :- start(ID,_,_).

% Initializing starting positions of each robot
start(IDR,IDN) :- start(IDR, X, Y), node(IDN, X, Y).

% Initializing goal positions of each robot (currently shelf id assigns the targets)
goal(IDN) :- goal(_, X, Y), node(IDN, X, Y).

% Initializing edges
edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X+1, Y).
edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X, Y+1).
edge((ID, ID2)) :- node(ID, X, Y), node(ID2, X+1, Y+1).
edge((ID, ID2)) :- node(ID, X, Y+1), node(ID2, X+1, Y).

edge((ID2, ID)) :- edge((ID, ID2)).

% Flag for edges that cross each other (crossing conflict detection)
is_crossing((ID,ID4),(ID2,ID3)) :- node(ID, X, Y), node(ID2, X+1, Y), node(ID3, X, Y+1), node(ID4, X+1, Y+1).

is_crossing((ID,ID4),(ID3,ID2)) :- is_crossing((ID,ID4),(ID2,ID3)).
is_crossing((ID4,ID),(ID3,ID2)) :- is_crossing((ID,ID4),(ID2,ID3)).
is_crossing((ID4,ID),(ID2,ID3)) :- is_crossing((ID,ID4),(ID2,ID3)).

% For abstraction: set goal for abstracted path

#show.
#show node/1.
#show edge/1.

#show is_crossing/2.
#show node/3.
#show robot/1.
#show start/2.
#show goal/1.
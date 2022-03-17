step(1..horizon).

%% INITIAL POSITIONS %%
robot_at(ID, NID, 0) :- robot_at(ID, NID).

%% MOVEMENT %%
1 {move(ID, T); wait(ID, T)} 1 :- step(T), robot(ID).

1 {move_to(ID, NID', T) : edge((NID, NID'))} 1 :- move(ID, T), robot_at(ID, NID, T-1).

%% UPDATE %%
robot_at(ID, NID, T) :- wait(ID,T), robot_at(ID, NID, T-1).
%:- wait(ID,T), robot_at(ID, NID2, T), robot_at(ID, NID, T), NID < NID2.

robot_at(ID, NID, T) :- move(ID,T), move_to(ID, NID, T).
%:- move(ID,T), robot_at(ID, NID, T), robot_at(ID, NID, T-1).

:- robot_at(ID, NID, T), robot_at(ID, NID2, T), NID < NID2.

%% GOAL %%
:- #count{ID : robot_at(ID, NID, horizon)} != COUNT, goal(NID, COUNT).

% Stay at target behaviour
%:- goal(NID, _), robot_at(RID, NID, T), robot_at(RID, NID', T'), T' > T, NID != NID'.
%:- goal(NID, _), robot_at(RID, NID, T), robot_at(RID, NID'', horizon), robot_at(RID, NID', T'),T' > T, NID != NID''.
%:- robot_at(RID,NID,T), goal(NID,_), robot_at(RID, NID', T'),T' > T, NID != NID', robot_at(RID2,NID2,T), goal(NID2,_), RID2 != RID.


%% PATH %%
% STRICT VERSION
%1 { robot_at(RID, NID, T*2) : node_in_clique(CID, NID)} 1 :- path(RID, CID, T).
%1 { robot_at(RID, NID, T*2+1) : node_in_clique(CID, NID)} 1 :- path(RID, CID, T).

% RELAXED VERSION
2 { robot_at(RID, NID, T*2..T*2+1+allowed_wait_times) : node_in_clique(CID, NID)} 2+allowed_wait_times :- path(RID, CID, T).

%% CONFLICTS %%
% Vertex Conflict
:- robot_at(RID, NID, T), robot_at(RID', NID, T), RID < RID', count_of_node(NID, 1).
:- N = #count{RID : robot_at(RID, NID, T)}, node(NID), step(T), count_of_node(NID, COUNT), N >= COUNT, COUNT > 1.
% Swapping Conflict 
:- robot_at(RID, NID, T), robot_at(RID, NID', T + 1), robot_at(RID', NID', T), robot_at(RID', NID, T + 1), RID < RID', count_of_node(NID, 1), count_of_node(NID', 1).

#heuristic wait(ID, T). [2,false]
#heuristic move(ID, T). [1,false]
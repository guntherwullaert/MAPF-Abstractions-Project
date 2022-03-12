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

%% PATH %%
1 { robot_at(RID, NID, T*2) : node_in_clique(CID, NID)} 1 :- path(RID, CID, T).
1 { robot_at(RID, NID, T*2+1) : node_in_clique(CID, NID)} 1 :- path(RID, CID, T).

%% CONFLICTS %%
 :- robot_at(RID, NID, T), robot_at(RID', NID, T), RID < RID'.
 :- robot_at(RID, NID, T), robot_at(RID, NID', T + 1), robot_at(RID', NID', T), robot_at(RID', NID, T + 1), RID < RID'.


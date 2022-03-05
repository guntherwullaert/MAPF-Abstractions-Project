step(0..horizon).

%% INITIAL POSITIONS %%
robot_at(ID, NID, 0) :- robot_at(ID, NID).

%% MOVEMENT %%
1 {move(ID, T); wait(ID, T)} 1 :- step(T), robot(ID).

1 {move_to(ID, NID', T) : edge((NID, NID'))} 1 :- move(ID, T), robot_at(ID, NID, T).

%% UPDATE %%
robot_at(ID, NID, T+1) :- wait(ID,T), robot_at(ID, NID, T).
:- wait(ID,T), robot_at(ID, NID2, T+1), robot_at(ID, NID), NID != NID2.
robot_at(ID, NID, T+1) :- move(ID,T), move_to(ID, NID, T).
:- move(ID,T), robot_at(ID, NID, T+1), robot_at(ID, NID).

%% GOAL %%
:- #count{ID : robot_at(ID, NID, horizon+1)} != COUNT, goal(NID, COUNT).

%% PATH %%
%1 { robot_at(RID, NID, T*2) : node_in_clique(CID, NID)} 1 :- path(RID, CID, T).

%%%%%%%%%%%%%%%%
%Initialization%
%%%%%%%%%%%%%%%%

% Maximum plan length for every agent (upper bound).
maxsteps(25).

% First path segment of each agent is at its start location.
path(ID, 0, V) :- start((ID, V)).

% Each next step is either a wait action or a move to an adjacent Vertex.
0{ path(ID, T + 1, V); path(ID, T + 1, U) : edge((V, U)) }1 :- path(ID, T, V), T < M, maxsteps(M).

% Each Vertex the path of an agent goes over is marked visited, and the goal has to be visited.
:- goal((ID, V)), not visit(ID, V).
visit(ID, V) :- path(ID, T, V).

% Stay at target
:- goal((ID, V)), path(ID, T, V2), plan_length(ID, MIN), T > MIN, V != V2.

% No steps after all agents have reached their target
:- makespan(M), path(_,T,_), M<T.

%%%%%%%%%%%%%%%%%%%%%
%Detecting Conflicts%
%%%%%%%%%%%%%%%%%%%%%

% No vertex conflicts (ID: 0).
%conflict(0, ID, ID0, T, V) :- path(ID, T, V), path(ID0, T, V), ID < ID0.
 :- path(ID, T, V), path(ID0, T, V), ID < ID0.

% No swapping(edge) conflicts (ID: 1).
%conflict(1, ID, ID0, T, (V, W)) :- path(ID, T, V), path(ID, T + 1, W), path(ID0, T, W), path(ID0, T + 1, V), ID < ID0.
:- path(ID, T, V), path(ID, T + 1, W), path(ID0, T, W), path(ID0, T + 1, V), ID < ID0.

% No crossing conflicts (ID: 2, possibly only on abstraction 0).
%conflict(2, ID, ID0, T, ((V,W),(V2,W2))) :- path(ID, T, V), path(ID, T + 1, W), path(ID0, T, V2), path(ID0, T + 1, W2), is_crossing((V,W),(V2,W2)).
:- path(ID, T, V), path(ID, T + 1, W), path(ID0, T, V2), path(ID0, T + 1, W2), is_crossing((V,W),(V2,W2)).

%%%%%%%%%%%%%%
%Optimization%
%%%%%%%%%%%%%%

% Get individual plan lengths
plan_length(ID, T) :- path(ID, T, V), goal((ID, V)), path(ID,T-1,W), not goal((ID,W)).

% Calculate makespan
makespan(M) :- M =  #max {T : plan_length(_, T)}.

% Calculate sum-of-costs
sum_of_costs(SOC) :- SOC = #sum { T,ID : plan_length(ID, T), robot(ID)}.

% Minimal sum-of-costs
#minimize{SOC : sum_of_costs(SOC)}.

% Minimal makespan
%#minimize{M : makespan(M)}.

%%%%%%%%
%Output%
%%%%%%%%

% Output transformation for asprilo-visualizer
occurs(object(robot, ID), action(move, (X2-X, Y2-Y)), T) :- path(ID, T+1, V2), node(V2, X2, Y2), path(ID, T, V), node(V, X, Y).
#show.
#show occurs/3.

%#show path/3.
%#show makespan/1.
%#show sum_of_costs/1.

%#show conflict/5.
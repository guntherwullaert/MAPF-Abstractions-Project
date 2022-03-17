% Transforms solved output and asprilo instance to asprilo Output
% Execute for example with:
% clingo --quiet=1,2,2 --outf=0 -V0 --out-atomf=%s. instances/corridor_instance.lp out/solution.lp solving/asprilo_transformation.lp > out/asprilo_output.lp
% truncate last line

node(ID,X,Y) :- init(object(node,ID),value(at,(X,Y))).

finished(T, NID, ID) :- robot_at(ID, NID, T), goal(NID, _).
fake(T, NID):- finished(T, NID, ID), robot_at(ID2,NID2, T), ID != ID2, not goal(NID2,_).

occurs(object(robot, RID), action(move, (X2-X, Y2-Y)), T) :- robot_at(RID, NID, T), node(NID, X, Y), robot_at(RID, NID', T + 1) , node(NID', X2, Y2), T <= M, finished(M, FID, _), not fake(M, FID).
#show.
#show occurs/3.
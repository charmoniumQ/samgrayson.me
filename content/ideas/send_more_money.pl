:- use_module(library(clpfd)).

all_digits([H|T]) :- between(0, 9, H), all_digits(T).
all_digits([]).

digit_sum([H1|T1], [H2|T2], [H3|T3], C1) :-
	H3 is (H1 + H2 + C1) mod 10,
	C2 is floor((H1 + H2 + C1) / 10),
	digit_sum(T1, T2, T3, C2).
digit_sum([], [], [H|T], C) :- H is C, empty(T).

empty([]).

:-
	All = [S,E,N,D,M,O,R,Y],
	all_digits(All),
	all_different(All),
	reverse([S,E,N,D], A_1), reverse([M,O,R,E], A_2), reverse([M,O,N,E,Y], A_3),
	digit_sum(A_1, A_2, A_3, 0),
	write([S,E,N,D]), write("+"), write([M,O,R,E]), write("="), write([M,O,N,E,Y]), write("\n").
	
